"""Track management and analysis endpoints."""

from datetime import datetime
import json
import logging
from json import JSONDecodeError
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.security import get_current_user_id, get_current_user_id_optional
from ...models import Analysis, Artist, Track, TrackAsset, TrackTags, PitchCopy, User
from ...schemas.track import (
    AnalysisResult,
    AnalysisStatus,
    TrackUploadPayload,
    TrackUploadResponse,
    TrackWithAnalysis,
    TranscriptionResult,
)
from ...schemas.track import (
    Track as TrackSchema,
)
from ...services.ai_enhancement import (
    explain_genre_with_ai,
    explain_hooks_with_ai,
    predict_breakout_with_ai,
)
from ...services.ai_tagging.mood_classifier import MoodClassifier
from ...services.ai_tagging.pitch_generator import PitchGenerator
from ...services.audio.feature_extraction import extract_audio_features
from ...services.audio.transcription import get_transcriber
from ...services.classification import detect_genre, detect_genre_hybrid
from ...services.embeddings.search import create_embedding_for_track
from ...services.lyrics.acquisition import LyricsAcquisition
from ...services.lyrics.analysis import analyze_lyrics
from ...services.scoring import calculate_tunescore

logger = logging.getLogger(__name__)

router = APIRouter()

# File storage configuration
STORAGE_DIR = Path("files")
STORAGE_DIR.mkdir(exist_ok=True)

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


@router.post(
    "/upload", response_model=TrackUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_track(
    track_data: str = Form(..., description="Serialized track metadata"),
    audio_file: UploadFile | None = File(None),
    lyrics_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> TrackUploadResponse:
    """
    Upload a track with audio file and optional lyrics.

    This endpoint:
    1. Validates and saves the audio file
    2. Creates track and artist records
    3. Performs audio analysis (sonic genome + hook detection)
    4. Performs lyrical analysis if lyrics provided
    5. Returns track info and analysis results
    """
    # Parse metadata payload
    try:
        payload = TrackUploadPayload.model_validate_json(track_data)
    except JSONDecodeError as exc:
        logger.error(f"Failed to decode track_data: {exc}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid track_data payload. Expecting JSON string.",
        ) from exc
    except ValidationError as exc:
        logger.error(f"Track upload payload validation failed: {exc.errors()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    if audio_file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required",
        )

    if not audio_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is missing a filename",
        )

    # Validate file extension
    file_ext = Path(audio_file.filename).suffix.lower()
    if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )

    # Validate file extension (already done above)
    # File size will be validated during the save process to avoid reading twice

    lyrics_text = payload.lyrics.strip() if payload.lyrics else None

    if lyrics_file is not None:
        try:
            lyrics_bytes = await lyrics_file.read()
            lyrics_text_candidate = lyrics_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            logger.error("Failed to decode uploaded lyrics file as UTF-8")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lyrics file must be UTF-8 encoded text",
            ) from exc
        else:
            lyrics_text = lyrics_text_candidate or lyrics_text

    try:
        # Normalise artist metadata
        artist_name = payload.artist_name.strip() if payload.artist_name else None

        # Create or get artist
        artist = None
        if artist_name:
            stmt = select(Artist).where(Artist.name == artist_name)
            result = await db.execute(stmt)
            artist = result.scalar_one_or_none()

            if not artist:
                artist = Artist(name=artist_name)
                db.add(artist)
                await db.flush()

        # Create track record
        track = Track(
            title=payload.title,
            user_id=current_user_id,
            artist_id=artist.id if artist else None,
        )
        db.add(track)
        await db.flush()

        # Save audio file and validate size in a single pass
        audio_dir = STORAGE_DIR / str(track.user_id) / str(track.id)
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_filename = f"audio{file_ext}"
        audio_path = audio_dir / audio_filename

        # Write file in chunks and validate size during write
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        try:
            async with aiofiles.open(audio_path, "wb") as f:
                while chunk := await audio_file.read(chunk_size):
                    file_size += len(chunk)
                    if file_size > MAX_FILE_SIZE:
                        max_mb = MAX_FILE_SIZE / (1024 * 1024)
                        current_mb = file_size / (1024 * 1024)
                        # File will be cleaned up by the context manager
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large: {current_mb:.1f}MB (max: {max_mb:.0f}MB)",
                        )
                    await f.write(chunk)
        except HTTPException:
            # Clean up partial file if size validation failed
            if audio_path.exists():
                audio_path.unlink()
            raise

        # Create track asset record (will be updated with lyrics provenance later)
        track_asset = TrackAsset(
            track_id=track.id,
            audio_path=str(audio_path),
            audio_format=file_ext.lstrip("."),
            lyrics_text=lyrics_text,
        )
        db.add(track_asset)
        await db.flush()  # Ensure track_asset has an ID before updating

        # Perform audio analysis
        logger.info(f"Starting audio analysis for track {track.id}")
        try:
            sonic_genome, hook_data, quality_metrics, mastering_quality, chord_analysis = extract_audio_features(str(audio_path))

            # Update track duration
            track.duration = sonic_genome.get("duration")

        except Exception as e:
            logger.error(f"Audio analysis failed for track {track.id}: {e}")
            sonic_genome = None
            hook_data = None
            quality_metrics = None
            mastering_quality = None
            chord_analysis = None

        # Lyrics acquisition using multi-source orchestrator
        lyrics_acquisition = LyricsAcquisition()
        lyrics_result = await lyrics_acquisition.get_lyrics(
            audio_path=str(audio_path) if audio_path else None,
            track_title=track.title,
            artist_name=artist_name,
            duration=sonic_genome.get("duration") if sonic_genome else None,
            provided_lyrics=lyrics_text,
        )
        
        # Update lyrics text and metadata
        lyrics_text = lyrics_result["text"] if lyrics_result["success"] else None
        lyrics_source = lyrics_result["source"]
        lyrics_confidence = lyrics_result["confidence"]
        lyrics_language = lyrics_result.get("language")
        lyrics_metadata = lyrics_result.get("metadata", {})
        
        # Update track asset with lyrics provenance
        track_asset.lyrics_text = lyrics_text
        track_asset.lyrics_source = lyrics_source
        track_asset.lyrics_confidence = lyrics_confidence
        track_asset.lyrics_language = lyrics_language
        track_asset.lyrics_metadata = lyrics_metadata
        
        # Build transcription result for response
        transcription_result = None
        if lyrics_result["success"] and lyrics_source != "user":
            transcription_result = TranscriptionResult(
                text=lyrics_result["text"],
                language=lyrics_language or "en",
                confidence=lyrics_confidence,
                success=True,
                verified=False,
            )
        
        # Handle lyrics verification if requested
        lyrics_verification = None
        if payload.verify_lyrics and lyrics_text and audio_path and lyrics_source == "user":
            logger.info(f"Verifying user-provided lyrics for track {track.id}")
            try:
                transcriber = get_transcriber()
                transcription = transcriber.transcribe_lyrics(str(audio_path))
                
                if transcription["success"] and transcription["text"]:
                    comparison = transcriber.compare_lyrics(
                        lyrics_text, 
                        transcription["text"]
                    )
                    lyrics_verification = comparison
                    logger.info(
                        f"Lyrics verification complete. Similarity: {comparison['similarity_score']:.2f}"
                    )
            except Exception as e:
                logger.error(f"Lyrics verification failed for track {track.id}: {e}")
        
        # Perform lyrical analysis if lyrics available
        lyrical_genome = None
        if lyrics_text:
            logger.info(f"Starting lyrical analysis for track {track.id}")
            try:
                # Pass track title and artist name for AI context
                lyrical_genome = analyze_lyrics(
                    lyrics_text,
                    track_title=track.title,
                    artist_name=payload.artist_name
                )
            except Exception as e:
                logger.error(f"Lyrical analysis failed for track {track.id}: {e}")

        # Calculate TuneScore
        logger.info(f"Calculating TuneScore for track {track.id}")
        tunescore_data = calculate_tunescore(
            sonic_genome or {},
            lyrical_genome,
            hook_data,
        )
        
        # Detect genre using hybrid (ML + instruments + heuristics)
        logger.info(f"Detecting genre for track {track.id}")
        try:
            genre_data = detect_genre_hybrid(
                str(audio_path) if audio_path else None,
                sonic_genome or {},
                lyrical_genome,
            )
        except Exception as exc:  # pragma: no cover - resilience
            logger.warning(f"Hybrid genre detection failed, falling back: {exc}")
            genre_data = detect_genre(sonic_genome or {}, lyrical_genome)
        
        # Extract AI critique from lyrical genome if present
        ai_lyric_critique = None
        if lyrical_genome and lyrical_genome.get('ai_critique'):
            ai_lyric_critique = lyrical_genome['ai_critique']
        
        # Create analysis record with enhanced data
        analysis = Analysis(
            track_id=track.id,
            sonic_genome=sonic_genome or {},
            lyrical_genome=lyrical_genome or {},
            hook_data=hook_data or {},
            tunescore=tunescore_data,
            genre_predictions=genre_data,
            quality_metrics=quality_metrics or {},
            mastering_quality=mastering_quality or {},
            chord_analysis=chord_analysis or {},
            ai_lyric_critique=ai_lyric_critique,  # Populate from auto-analysis
        )
        db.add(analysis)

        # Generate embedding for RIYL
        logger.info(f"Generating embedding for track {track.id}")
        try:
            await create_embedding_for_track(track.id, db)
        except Exception as e:
            logger.error(f"Embedding generation failed for track {track.id}: {e}")

        # ===== UNGATED AI FEATURES =====
        # Generate tags automatically (no button click needed!)
        logger.info(f"Generating AI tags for track {track.id}")
        track_tags = None
        try:
            classifier = MoodClassifier()
            mood_data = classifier.classify(sonic_genome or {}, lyrical_genome)
            commercial_tags = classifier.classify_commercial_tags(sonic_genome or {})
            
            track_tags = TrackTags(
                track_id=track.id,
                moods=mood_data.get("moods", []),
                commercial_tags=commercial_tags,
                use_cases=mood_data.get("use_cases", []),
                sounds_like=mood_data.get("sounds_like", [])
            )
            db.add(track_tags)
            logger.info(f"✅ Tags generated: {len(track_tags.moods)} moods, {len(commercial_tags)} commercial tags")
        except Exception as e:
            logger.error(f"Tag generation failed for track {track.id}: {e}")

        # Generate pitch copy automatically (if AI available)
        logger.info(f"Generating AI pitch copy for track {track.id}")
        pitch_copy = None
        try:
            pitch_generator = PitchGenerator()
            pitch_data = pitch_generator.generate_pitch(
                track_title=track.title,
                artist_name=payload.artist_name,
                sonic_genome=sonic_genome or {},
                lyrical_genome=lyrical_genome,
                tags={
                    "moods": track_tags.moods if track_tags else [],
                    "commercial_tags": track_tags.commercial_tags if track_tags else [],
                    "sounds_like": track_tags.sounds_like if track_tags else [],
                } if track_tags else None
            )
            
            pitch_copy = PitchCopy(
                track_id=track.id,
                elevator_pitch=pitch_data.get("elevator_pitch"),
                short_description=pitch_data.get("short_description"),
                sync_pitch=pitch_data.get("sync_pitch"),
                cost=pitch_data.get("cost"),
                generated_at=pitch_data.get("generated_at")
            )
            db.add(pitch_copy)
            logger.info(f"✅ Pitch copy generated (cost: ${pitch_data.get('cost', 0):.4f})")
        except ValueError as e:
            logger.warning(f"Pitch generation unavailable (no AI key): {e}")
        except Exception as e:
            logger.error(f"Pitch generation failed for track {track.id}: {e}")
        
        # ===== PHASE 2: AI-ENHANCED HEURISTICS =====
        ai_enhancements = {}
        total_ai_cost = 0.0
        
        # AI Genre Reasoning
        if genre_data and sonic_genome:
            logger.info(f"Generating AI genre reasoning for track {track.id}")
            try:
                genre_reasoning = explain_genre_with_ai(
                    track_title=track.title,
                    artist_name=payload.artist_name,
                    sonic_genome=sonic_genome,
                    genre_predictions=genre_data,
                    lyrical_themes=lyrical_genome.get("themes", []) if lyrical_genome else None
                )
                if genre_reasoning:
                    ai_enhancements["genre_reasoning"] = genre_reasoning
                    total_ai_cost += genre_reasoning.get("cost", 0)
                    logger.info(f"✅ Genre reasoning: ${genre_reasoning.get('cost', 0):.4f}")
            except Exception as e:
                logger.error(f"Genre reasoning failed: {e}")
        
        # AI Hook Explanation
        if hook_data:
            logger.info(f"Generating AI hook explanation for track {track.id}")
            try:
                hook_explanation = explain_hooks_with_ai(
                    track_title=track.title,
                    hook_data=hook_data,
                    lyrical_sections=lyrical_genome.get("sections", []) if lyrical_genome else None,
                    sonic_genome=sonic_genome
                )
                if hook_explanation:
                    ai_enhancements["hook_explanation"] = hook_explanation
                    total_ai_cost += hook_explanation.get("cost", 0)
                    logger.info(f"✅ Hook explanation: ${hook_explanation.get('cost', 0):.4f}")
            except Exception as e:
                logger.error(f"Hook explanation failed: {e}")
        
        # AI Breakout Prediction
        if tunescore_data and genre_data:
            logger.info(f"Generating AI breakout prediction for track {track.id}")
            try:
                primary_genre = genre_data.get("top_genres", [{}])[0].get("genre", "Unknown") if genre_data.get("top_genres") else "Unknown"
                breakout_prediction = predict_breakout_with_ai(
                    track_title=track.title,
                    artist_name=payload.artist_name,
                    tunescore=tunescore_data,
                    genre=primary_genre,
                    moods=track_tags.moods if track_tags else [],
                    hook_strength=hook_data.get("hook_strength", 0.5) if hook_data else 0.5,
                    track_duration=sonic_genome.get("duration", None) if sonic_genome else None
                )
                if breakout_prediction:
                    ai_enhancements["breakout_prediction"] = breakout_prediction
                    total_ai_cost += breakout_prediction.get("cost", 0)
                    logger.info(f"✅ Breakout prediction: ${breakout_prediction.get('cost', 0):.4f}")
            except Exception as e:
                logger.error(f"Breakout prediction failed: {e}")
        
        # Update analysis with AI enhancements
        if ai_enhancements:
            # Store in a new field or merge into existing
            import json
            current_ai_costs = analysis.ai_costs or {}
            current_ai_costs.update({
                "genre_reasoning": ai_enhancements.get("genre_reasoning", {}).get("cost", 0),
                "hook_explanation": ai_enhancements.get("hook_explanation", {}).get("cost", 0),
                "breakout_prediction": ai_enhancements.get("breakout_prediction", {}).get("cost", 0),
                "phase2_total": total_ai_cost,
                "grand_total": current_ai_costs.get("total", 0) + total_ai_cost
            })
            analysis.ai_costs = current_ai_costs
            
            # Store AI enhancements in genre_predictions for now (we can add a dedicated field later)
            if genre_data:
                genre_data["ai_reasoning"] = ai_enhancements.get("genre_reasoning")
                analysis.genre_predictions = genre_data
            
            # Store hook explanation in hook_data
            if hook_data and ai_enhancements.get("hook_explanation"):
                hook_data["ai_explanation"] = ai_enhancements.get("hook_explanation")
                analysis.hook_data = hook_data
            
            # Store breakout prediction in tunescore
            if tunescore_data and ai_enhancements.get("breakout_prediction"):
                tunescore_data["ai_breakout"] = ai_enhancements.get("breakout_prediction")
                analysis.tunescore = tunescore_data
            
            logger.info(f"✅ Phase 2 AI enhancements complete: ${total_ai_cost:.4f}")
        # ===== END PHASE 2 =====
        # ===== END UNGATED AI FEATURES =====

        await db.commit()
        await db.refresh(track)

        return TrackUploadResponse(
            track=TrackSchema.from_orm(track),
            analysis_started=True,
            message=f"Track uploaded with full AI analysis! (AI cost: ${current_ai_costs.get('grand_total', 0):.4f})" if ai_enhancements else "Track uploaded and analyzed successfully (AI features included!)",
            transcription=transcription_result,
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Track upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("/{track_id}", response_model=TrackWithAnalysis)
async def get_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> TrackWithAnalysis:
    """
    Get track details with analysis results.
    """
    # Get track
    stmt = select(Track).where(Track.id == track_id)
    result = await db.execute(stmt)
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Track not found"
        )

    # Get track asset (for lyrics)
    stmt = select(TrackAsset).where(TrackAsset.track_id == track_id)
    result = await db.execute(stmt)
    track_asset = result.scalar_one_or_none()

    # Get artist name if available
    artist_name = None
    if track.artist_id:
        stmt = select(Artist).where(Artist.id == track.artist_id)
        result = await db.execute(stmt)
        artist = result.scalar_one_or_none()
        if artist:
            artist_name = artist.name

    # Get latest analysis
    stmt = (
        select(Analysis)
        .where(Analysis.track_id == track_id)
        .order_by(Analysis.created_at.desc())
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    # Get AI tags
    stmt = select(TrackTags).where(TrackTags.track_id == track_id)
    result = await db.execute(stmt)
    track_tags = result.scalar_one_or_none()
    
    ai_tags = None
    if track_tags:
        ai_tags = {
            "moods": track_tags.moods,
            "commercial_tags": track_tags.commercial_tags,
            "use_cases": track_tags.use_cases,
            "sounds_like": track_tags.sounds_like,
        }
    
    # Get AI pitch copy
    stmt = select(PitchCopy).where(PitchCopy.track_id == track_id)
    result = await db.execute(stmt)
    pitch_copy = result.scalar_one_or_none()
    
    ai_pitch = None
    if pitch_copy:
        ai_pitch = {
            "elevator_pitch": pitch_copy.elevator_pitch,
            "short_description": pitch_copy.short_description,
            "sync_pitch": pitch_copy.sync_pitch,
            "cost": pitch_copy.cost,
            "generated_at": pitch_copy.generated_at.isoformat() if pitch_copy.generated_at else None,
        }

    return TrackWithAnalysis(
        id=track.id,
        title=track.title,
        duration=track.duration,
        user_id=track.user_id,
        artist_id=track.artist_id,
        artist_name=artist_name,
        spotify_id=track.spotify_id,
        created_at=track.created_at,
        updated_at=track.updated_at,
        sonic_genome=analysis.sonic_genome if analysis else None,
        lyrical_genome=analysis.lyrical_genome if analysis else None,
        hook_data=analysis.hook_data if analysis else None,
        tunescore=analysis.tunescore if analysis else None,
        genre_predictions=analysis.genre_predictions if analysis else None,
        quality_metrics=analysis.quality_metrics if analysis else None,
        mastering_quality=analysis.mastering_quality if analysis else None,
        chord_analysis=analysis.chord_analysis if analysis else None,
        ai_lyric_critique=analysis.ai_lyric_critique if analysis else None,
        ai_tags=ai_tags,
        ai_pitch=ai_pitch,
        track_tags=ai_tags,  # Frontend expects this field name
        pitch_copy=ai_pitch,  # Frontend expects this field name
        lyrics=track_asset.lyrics_text if track_asset else None,
        lyrics_source=track_asset.lyrics_source if track_asset else None,
        lyrics_confidence=track_asset.lyrics_confidence if track_asset else None,
        lyrics_language=track_asset.lyrics_language if track_asset else None,
        lyrics_metadata=track_asset.lyrics_metadata if track_asset else None,
    )


@router.get("/{track_id}/analysis", response_model=AnalysisResult)
async def get_track_analysis(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> AnalysisResult:
    """
    Get analysis results for a track.
    """
    # Verify track exists
    stmt = select(Track).where(Track.id == track_id)
    result = await db.execute(stmt)
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Track not found"
        )

    # Get latest analysis
    stmt = (
        select(Analysis)
        .where(Analysis.track_id == track_id)
        .order_by(Analysis.created_at.desc())
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found for this track",
        )

    return AnalysisResult.from_orm(analysis)


@router.get("/{track_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> AnalysisStatus:
    """
    Get analysis status for a track.
    """
    # Verify track exists
    stmt = select(Track).where(Track.id == track_id)
    result = await db.execute(stmt)
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Track not found"
        )

    # Get latest analysis
    stmt = (
        select(Analysis)
        .where(Analysis.track_id == track_id)
        .order_by(Analysis.created_at.desc())
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        return AnalysisStatus(
            track_id=track_id,
            status="pending",
            sonic_genome_complete=False,
            lyrical_genome_complete=False,
            hook_detection_complete=False,
        )

    # Check what's complete
    sonic_complete = bool(analysis.sonic_genome)
    lyrical_complete = bool(analysis.lyrical_genome)
    hook_complete = bool(analysis.hook_data)

    status_str = "completed" if sonic_complete and hook_complete else "processing"

    return AnalysisStatus(
        track_id=track_id,
        status=status_str,
        sonic_genome_complete=sonic_complete,
        lyrical_genome_complete=lyrical_complete,
        hook_detection_complete=hook_complete,
    )


@router.get("/")
async def list_tracks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_id: int | None = Depends(get_current_user_id_optional),
) -> list[dict]:
    """
    List tracks with artist names and scores included.
    
    If authenticated, returns only the user's tracks.
    If not authenticated, returns all tracks (public mode).
    """
    # Build query based on authentication
    if current_user_id is not None:
        # Authenticated: show only user's tracks
        stmt = (
            select(Track)
            .where(Track.user_id == current_user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Track.created_at.desc())
        )
    else:
        # Not authenticated: show all tracks (public mode)
        stmt = (
            select(Track)
            .offset(skip)
            .limit(limit)
            .order_by(Track.created_at.desc())
        )
    result = await db.execute(stmt)
    tracks = result.scalars().all()

    # Fetch all unique artist IDs
    artist_ids = {track.artist_id for track in tracks if track.artist_id}
    artists_map = {}
    
    if artist_ids:
        stmt = select(Artist).where(Artist.id.in_(artist_ids))
        result = await db.execute(stmt)
        artists = result.scalars().all()
        artists_map = {artist.id: artist.name for artist in artists}

    # Fetch latest analysis for each track (for tunescore)
    track_ids = [track.id for track in tracks]
    analyses_map = {}
    if track_ids:
        # Get latest analysis for each track using a subquery
        from sqlalchemy import func
        subquery = (
            select(
                Analysis.track_id,
                func.max(Analysis.created_at).label('max_created_at')
            )
            .where(Analysis.track_id.in_(track_ids))
            .group_by(Analysis.track_id)
            .subquery()
        )
        
        stmt = (
            select(Analysis)
            .join(
                subquery,
                (Analysis.track_id == subquery.c.track_id) &
                (Analysis.created_at == subquery.c.max_created_at)
            )
        )
        result = await db.execute(stmt)
        analyses = result.scalars().all()
        
        # Map by track_id
        for analysis in analyses:
            analyses_map[analysis.track_id] = analysis

    # Build response with artist names and scores
    response = []
    for track in tracks:
        track_data = {
            **TrackSchema.from_orm(track).model_dump(),
            "artist_name": artists_map.get(track.artist_id) if track.artist_id else None,
        }
        
        # Add tunescore if available
        analysis = analyses_map.get(track.id)
        if analysis and analysis.tunescore:
            track_data["tunescore"] = analysis.tunescore
        
        response.append(track_data)
    
    return response


@router.post("/{track_id}/lyric-critique")
async def generate_lyric_critique(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Generate AI-powered lyric critique for a track.
    
    Requires ANTHROPIC_API_KEY to be configured.
    Cost: ~$0.02-0.10 per critique depending on lyrics length.
    """
    from ...services.lyrics.ai_critic import AILyricCritic
    
    # Get track
    stmt = select(Track).where(Track.id == track_id)
    result = await db.execute(stmt)
    track = result.scalar_one_or_none()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Get track asset (for lyrics)
    stmt = select(TrackAsset).where(TrackAsset.track_id == track_id)
    result = await db.execute(stmt)
    track_asset = result.scalar_one_or_none()
    
    if not track_asset or not track_asset.lyrics_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No lyrics found for this track"
        )
    
    # Get analysis (for lyrical genome context)
    stmt = (
        select(Analysis)
        .where(Analysis.track_id == track_id)
        .order_by(Analysis.created_at.desc())
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()
    
    if not analysis or not analysis.lyrical_genome:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Track must be analyzed before generating critique"
        )
    
    # Generate critique
    try:
        critic = AILyricCritic()
        critique = critic.critique(
            track_asset.lyrics_text,
            analysis.lyrical_genome
        )
        
        # Store in database
        analysis.ai_lyric_critique = critique
        await db.commit()
        
        logger.info(
            f"Generated lyric critique for track {track_id}, "
            f"cost: ${critique.get('cost', 0):.4f}"
        )
        
        return critique
        
    except ValueError as e:
        # API key not configured
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI critique service not configured: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to generate critique for track {track_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate critique"
        )


@router.patch("/{track_id}/lyrics")
async def update_lyrics(
    track_id: int,
    lyrics: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> dict:
    """
    Update track lyrics and mark as user-verified.
    
    This endpoint allows users to edit/correct lyrics that were auto-transcribed
    or fetched from external sources. Updated lyrics are marked as "user_verified"
    with 100% confidence.
    
    The lyrical genome will be re-analyzed after the update.
    """
    # Get track and verify ownership
    stmt = select(Track).where(Track.id == track_id)
    result = await db.execute(stmt)
    track = result.scalar_one_or_none()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    if track.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this track"
        )
    
    # Get track asset
    stmt = select(TrackAsset).where(TrackAsset.track_id == track_id)
    result = await db.execute(stmt)
    track_asset = result.scalar_one_or_none()
    
    if not track_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track asset not found"
        )
    
    try:
        # Update lyrics with user-verified provenance
        track_asset.lyrics_text = lyrics.strip()
        track_asset.lyrics_source = "user_verified"
        track_asset.lyrics_confidence = 1.0
        track_asset.lyrics_metadata = {
            **track_asset.lyrics_metadata,
            "previous_source": track_asset.lyrics_source,
            "edited_at": datetime.utcnow().isoformat(),
        }
        
        # Re-analyze lyrics
        logger.info(f"Re-analyzing lyrics for track {track_id} after user edit")
        
        # Get artist name for context
        artist_name = None
        if track.artist_id:
            stmt = select(Artist).where(Artist.id == track.artist_id)
            result = await db.execute(stmt)
            artist = result.scalar_one_or_none()
            if artist:
                artist_name = artist.name
        
        # Perform lyrical analysis
        lyrical_genome = analyze_lyrics(
            lyrics.strip(),
            track_title=track.title,
            artist_name=artist_name or ""
        )
        
        # Update analysis
        stmt = (
            select(Analysis)
            .where(Analysis.track_id == track_id)
            .order_by(Analysis.created_at.desc())
        )
        result = await db.execute(stmt)
        analysis = result.scalar_one_or_none()
        
        if analysis:
            analysis.lyrical_genome = lyrical_genome
            
            # Recalculate tunescore with new lyrics
            tunescore_data = calculate_tunescore(
                sonic_genome=analysis.sonic_genome,
                lyrical_genome=lyrical_genome,
                hook_data=analysis.hook_data,
                quality_metrics=analysis.quality_metrics
            )
            analysis.tunescore = tunescore_data
        
        await db.commit()
        
        logger.info(f"✅ Successfully updated lyrics for track {track_id}")
        
        return {
            "message": "Lyrics updated successfully",
            "lyrics_source": "user_verified",
            "lyrics_confidence": 1.0,
            "reanalyzed": True
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update lyrics for track {track_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update lyrics: {str(e)}"
        )
