<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { api } from '$lib/api/client';
	import { 
		Music, BarChart3, TrendingUp, FileText, Activity, Repeat, Type, 
		Play, Pause, Volume2, Award, Tag, ArrowLeft, Target, CheckCircle2,
		AlertCircle, Lightbulb, BookOpen, Mic2, Gauge, ExternalLink, Radio
	} from 'lucide-svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import MasteringQualityCard from '$lib/components/MasteringQualityCard.svelte';
	import ChordProgressionCard from '$lib/components/ChordProgressionCard.svelte';
	import LyricCritiqueCard from '$lib/components/LyricCritiqueCard.svelte';
	import ViralSegmentsCard from '$lib/components/ViralSegmentsCard.svelte';
	import TrackTagsCard from '$lib/components/TrackTagsCard.svelte';
	import PitchCopyCard from '$lib/components/PitchCopyCard.svelte';
	import BreakoutScoreCard from '$lib/components/BreakoutScoreCard.svelte';
	import CollaborationCard from '$lib/components/CollaborationCard.svelte';
	import MarketPositionCard from '$lib/components/MarketPositionCard.svelte';
	import CatalogValueCard from '$lib/components/CatalogValueCard.svelte';
	import GrowthMetricsCard from '$lib/components/GrowthMetricsCard.svelte';

	let track = $state<any>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let showLyrics = $state(false);
	let expandedSection = $state<string | null>(null);
	let riylRecommendations = $state<any>(null);
	let similarTracks = $state<any[]>([]);
	let editingLyrics = $state(false);
	let editedLyrics = $state('');
	let loadingRecommendations = $state(false);
	let generatingCritique = $state(false);
	let generatingPitch = $state(false);
	let generatingTags = $state(false);
	
	// Audio player state
	let audioElement: HTMLAudioElement | null = null;
	let isPlaying = $state(false);
	let currentTime = $state(0);
	let duration = $state(0);
	let volume = $state(0.8);
	let playingSegmentEnd = $state<number | null>(null); // Track when to auto-pause for segment playback

	onMount(async () => {
		const trackId = parseInt($page.params.id);
		if (!trackId) {
			error = 'Invalid track ID';
			loading = false;
			return;
		}

		try {
			track = await api.tracks.get(trackId);
			
			// Load RIYL recommendations and similar tracks
			loadingRecommendations = true;
			try {
				riylRecommendations = await api.search.riyl(trackId, 5);
			} catch (e) {
				console.warn('Failed to load RIYL recommendations:', e);
			}
			
			try {
				similarTracks = await api.search.similar(trackId, 10);
			} catch (e) {
				console.warn('Failed to load similar tracks:', e);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load track';
		} finally {
			loading = false;
			loadingRecommendations = false;
		}
	});

	function formatSentiment(compound: number): string {
		if (compound > 0.05) return 'Positive';
		if (compound < -0.05) return 'Negative';
		return 'Neutral';
	}

	function getSentimentColor(compound: number): string {
		if (compound > 0.05) return 'text-green-600';
		if (compound < -0.05) return 'text-red-600';
		return 'text-gray-600';
	}

	function formatTime(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function getGradeColor(grade: string): string {
		if (grade.startsWith('A')) return 'text-green-600 bg-green-50 border-green-200';
		if (grade.startsWith('B')) return 'text-blue-600 bg-blue-50 border-blue-200';
		if (grade.startsWith('C')) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
		if (grade.startsWith('D')) return 'text-orange-600 bg-orange-50 border-orange-200';
		return 'text-red-600 bg-red-50 border-red-200';
	}

	function getQualityColor(grade: string): string {
		if (grade === 'Professional') return 'text-green-600 bg-green-50';
		if (grade === 'Advanced') return 'text-blue-600 bg-blue-50';
		if (grade === 'Intermediate') return 'text-yellow-600 bg-yellow-50';
		if (grade === 'Developing') return 'text-orange-600 bg-orange-50';
		return 'text-red-600 bg-red-50';
	}

	// Audio player functions
	function togglePlay() {
		if (!audioElement) return;
		
		if (isPlaying) {
			audioElement.pause();
			playingSegmentEnd = null; // Clear segment tracking on manual pause
		} else {
			audioElement.play();
		}
		isPlaying = !isPlaying;
	}

	function handleTimeUpdate() {
		if (audioElement) {
			currentTime = audioElement.currentTime;
			
			// Auto-pause at segment end if playing a specific segment
			if (playingSegmentEnd !== null && currentTime >= playingSegmentEnd) {
				audioElement.pause();
				isPlaying = false;
				playingSegmentEnd = null;
			}
		}
	}

	function handleLoadedMetadata() {
		if (audioElement) {
			duration = audioElement.duration;
		}
	}

	function handleEnded() {
		isPlaying = false;
		currentTime = 0;
		playingSegmentEnd = null; // Clear segment end tracking
	}

	function seek(e: MouseEvent) {
		if (!audioElement) return;
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const percent = (e.clientX - rect.left) / rect.width;
		audioElement.currentTime = percent * duration;
		playingSegmentEnd = null; // Clear segment tracking on manual seek
	}

	function setVolume(e: Event) {
		const newVolume = parseFloat((e.target as HTMLInputElement).value);
		volume = newVolume;
		if (audioElement) {
			audioElement.volume = newVolume;
		}
	}

	function toggleSection(section: string) {
		expandedSection = expandedSection === section ? null : section;
	}

	async function generateLyricCritique() {
		if (!track) return;
		
		generatingCritique = true;
		try {
			const response = await fetch(`/api/v1/tracks/${track.id}/lyric-critique`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			});
			
			if (!response.ok) {
				throw new Error('Failed to generate critique');
			}
			
			const critique = await response.json();
			
			// Update track with new critique
			track = { ...track, ai_lyric_critique: critique };
		} catch (e) {
			console.error('Failed to generate lyric critique:', e);
			alert('Failed to generate critique. Make sure ANTHROPIC_API_KEY is configured.');
		} finally {
			generatingCritique = false;
		}
	}

	async function generatePitchCopy() {
		if (!track) return;
		
		generatingPitch = true;
		try {
			const response = await fetch(`/api/v1/tracks/${track.id}/generate-pitch`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			});
			
			if (!response.ok) {
				throw new Error('Failed to generate pitch');
			}
			
			const pitch = await response.json();
			
			// Update track with new pitch
			track = { ...track, pitch_copy: pitch };
		} catch (e) {
			console.error('Failed to generate pitch:', e);
			alert('Failed to generate pitch. Make sure ANTHROPIC_API_KEY is configured.');
		} finally {
			generatingPitch = false;
		}
	}

	async function generateTags() {
		if (!track) return;
		
		generatingTags = true;
		try {
			const response = await fetch(`/api/v1/tracks/${track.id}/generate-tags`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			});
			
			if (!response.ok) {
				throw new Error('Failed to generate tags');
			}
			
			const tags = await response.json();
			
			// Update track with new tags
			track = { ...track, track_tags: tags };
		} catch (e) {
			console.error('Failed to generate tags:', e);
			alert('Failed to generate tags.');
		} finally {
			generatingTags = false;
		}
	}

	function jumpToTime(time: number, endTime?: number) {
		if (!audioElement) return;
		
		// Ensure audio is loaded before seeking
		if (audioElement.readyState < 2) {
			audioElement.load();
			audioElement.addEventListener('loadeddata', () => {
				audioElement!.currentTime = time;
				if (!isPlaying) {
					audioElement!.play();
					isPlaying = true;
				}
				// Set segment end time for auto-pause if provided
				if (endTime !== undefined) {
					playingSegmentEnd = endTime;
				}
			}, { once: true });
		} else {
			audioElement.currentTime = time;
			if (!isPlaying) {
				audioElement.play();
				isPlaying = true;
			}
			// Set segment end time for auto-pause if provided
			if (endTime !== undefined) {
				playingSegmentEnd = endTime;
			}
		}
	}
</script>

<div class="container mx-auto px-4 py-8 max-w-7xl">
	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
			<p class="mt-4 text-muted-foreground">Loading track analysis...</p>
		</div>
	{:else if error}
		<div class="text-center py-12">
			<p class="text-destructive mb-4">{error}</p>
			<a href="/dashboard" class="text-primary underline">← Back to Dashboard</a>
		</div>
	{:else if track}
		<!-- Header with Audio Player -->
		<div class="mb-8">
			<a href="/dashboard" class="text-primary hover:underline mb-4 inline-flex items-center gap-2">
				<ArrowLeft class="h-4 w-4" />
				Back to Dashboard
			</a>
			
			<div class="flex items-start justify-between gap-6 mt-4">
				<div class="flex-1">
					<h1 class="text-4xl font-bold mb-2">{track.title}</h1>
					<p class="text-2xl text-muted-foreground mb-4">by {track.artist_name || 'Unknown Artist'}</p>
					
					<!-- Genre Tags -->
					{#if track.genre_predictions?.predictions}
						<div class="space-y-3 mb-4">
							<div class="flex flex-wrap gap-2 items-center">
								{#if track.genre_predictions.primary_genre}
									<span class="inline-flex items-center gap-1 px-3 py-1 bg-primary text-primary-foreground rounded-full text-sm font-semibold">
										<Tag class="h-3 w-3" />
										{track.genre_predictions.primary_genre}
									</span>
								{/if}
								{#each track.genre_predictions.predictions.slice(0, 3) as pred}
									{#if pred.genre !== track.genre_predictions?.primary_genre}
										<span class="inline-flex items-center gap-1 px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm font-medium">
											<Tag class="h-3 w-3" />
											{pred.genre} ({pred.confidence.toFixed(0)}%)
										</span>
									{/if}
								{/each}
								{#if track.genre_predictions.method}
									<span class="text-xs text-muted-foreground ml-2">
										({track.genre_predictions.method.replace('_', ' ')})
									</span>
								{/if}
							</div>

							<!-- AI Genre Reasoning (NEW!) -->
							{#if track.genre_predictions.ai_reasoning}
								<div class="bg-gradient-to-r from-purple-50 to-transparent dark:from-purple-950/20 rounded-lg p-3 border-l-4 border-purple-500">
									<div class="flex items-start gap-2">
										<Lightbulb class="h-4 w-4 text-purple-600 mt-1 flex-shrink-0" />
										<div class="flex-1">
											<p class="text-sm font-medium mb-1">🎵 AI Genre Insights</p>
											<p class="text-xs text-muted-foreground">{track.genre_predictions.ai_reasoning.explanation}</p>
											{#if track.genre_predictions.ai_reasoning.commercial_context}
												<p class="text-xs text-muted-foreground mt-2"><strong>Market Context:</strong> {track.genre_predictions.ai_reasoning.commercial_context}</p>
											{/if}
										</div>
									</div>
								</div>
							{/if}
						</div>
					{/if}
					
					<!-- Track Metadata -->
					{#if track.created_at || track.updated_at}
						<div class="text-xs text-muted-foreground flex flex-wrap gap-4">
							{#if track.created_at}
								<span>Uploaded: {new Date(track.created_at).toLocaleDateString()}</span>
							{/if}
							{#if track.updated_at}
								<span>Updated: {new Date(track.updated_at).toLocaleDateString()}</span>
							{/if}
						</div>
					{/if}
				</div>

				<!-- TuneScore Card -->
				{#if track.tunescore?.overall_score}
					<div class="border-2 rounded-lg p-6 min-w-[200px] {getGradeColor(track.tunescore.grade)}">
						<div class="flex items-center gap-2 mb-2">
							<Award class="h-5 w-5" />
							<h3 class="font-semibold">TuneScore</h3>
						</div>
						<div class="text-4xl font-bold mb-1">{track.tunescore?.overall_score?.toFixed(0) ?? 'N/A'}</div>
						<div class="text-2xl font-semibold mb-3">Grade: {track.tunescore?.grade ?? 'N/A'}</div>
						<div class="text-xs opacity-75">Out of 100</div>
					</div>
				{/if}
			</div>

			<!-- Audio Player -->
			{#if track.audio_path || track.id}
				<div class="mt-6 border rounded-lg p-4 bg-secondary/20">
					<audio
						bind:this={audioElement}
						src="/api/v1/audio/{track.id}/stream"
						ontimeupdate={handleTimeUpdate}
						onloadedmetadata={handleLoadedMetadata}
						onended={handleEnded}
						preload="metadata"
					></audio>

					<div class="flex items-center gap-4">
						<button
							onclick={togglePlay}
							class="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:opacity-90 transition-opacity"
							aria-label={isPlaying ? 'Pause' : 'Play'}
						>
							{#if isPlaying}
								<Pause class="h-6 w-6" />
							{:else}
								<Play class="h-6 w-6 ml-1" />
							{/if}
						</button>

						<div class="flex-1">
							<div class="flex items-center gap-2 text-sm text-muted-foreground mb-1">
								<span>{formatTime(currentTime)}</span>
								<span>/</span>
								<span>{formatTime(duration || track.duration || 0)}</span>
							</div>
							<div
								class="h-2 bg-secondary rounded-full cursor-pointer relative overflow-hidden"
								onclick={seek}
								role="progressbar"
								aria-valuenow={currentTime}
								aria-valuemin={0}
								aria-valuemax={duration}
							>
								<div
									class="h-full bg-primary transition-all"
									style="width: {duration > 0 ? (currentTime / duration) * 100 : 0}%"
								></div>
							</div>
						</div>

						<div class="flex items-center gap-2">
							<Volume2 class="h-4 w-4 text-muted-foreground" />
							<input
								type="range"
								min="0"
								max="1"
								step="0.01"
								value={volume}
								oninput={setVolume}
								class="w-24"
								aria-label="Volume"
							/>
						</div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Quality Metrics & Songwriting Quality -->
		<div class="grid lg:grid-cols-2 gap-6 mb-6">
			<!-- Quality Metrics (NEW!) -->
			{#if track.quality_metrics && track.quality_metrics.overall_quality !== undefined}
				<div class="border rounded-lg p-6 bg-gradient-to-br from-purple-50 to-transparent dark:from-purple-950/20">
					<div class="flex items-center gap-2 mb-4">
						<Gauge class="h-5 w-5 text-purple-600" />
						<h2 class="text-xl font-semibold">Quality Metrics</h2>
					</div>
					
					<div class="text-center mb-4">
						<div class="text-5xl font-bold text-purple-600 mb-2">
							{track.quality_metrics.overall_quality?.toFixed(0) ?? 'N/A'}
						</div>
						<div class="text-lg font-semibold px-4 py-2 rounded-full inline-block {getQualityColor(track.quality_metrics?.quality_grade ?? 'N/A')}">
							{track.quality_metrics?.quality_grade ?? 'N/A'}
						</div>
					</div>

					<div class="space-y-3">
						<div>
							<div class="flex justify-between text-sm mb-1">
								<span class="text-muted-foreground">Pitch Accuracy</span>
								<span class="font-medium">{track.quality_metrics?.pitch_accuracy?.toFixed(0) ?? 'N/A'}/100</span>
							</div>
							<div class="h-2 bg-secondary rounded-full overflow-hidden">
								<div
									class="h-full bg-purple-500 transition-all"
									style="width: {track.quality_metrics?.pitch_accuracy ?? 0}%"
								></div>
							</div>
						</div>

						<div>
							<div class="flex justify-between text-sm mb-1">
								<span class="text-muted-foreground">Timing Precision</span>
								<span class="font-medium">{track.quality_metrics?.timing_precision?.toFixed(0) ?? 'N/A'}/100</span>
							</div>
							<div class="h-2 bg-secondary rounded-full overflow-hidden">
								<div
									class="h-full bg-blue-500 transition-all"
									style="width: {track.quality_metrics?.timing_precision ?? 0}%"
								></div>
							</div>
						</div>

						<div>
							<div class="flex justify-between text-sm mb-1">
								<span class="text-muted-foreground">Harmonic Coherence</span>
								<span class="font-medium">{track.quality_metrics?.harmonic_coherence?.toFixed(0) ?? 'N/A'}/100</span>
							</div>
							<div class="h-2 bg-secondary rounded-full overflow-hidden">
								<div
									class="h-full bg-green-500 transition-all"
									style="width: {track.quality_metrics?.harmonic_coherence ?? 0}%"
								></div>
							</div>
						</div>
					</div>

					<div class="mt-4 pt-4 border-t text-xs text-muted-foreground space-y-1">
						<p>• <strong>Pitch Accuracy:</strong> Tuning consistency</p>
						<p>• <strong>Timing Precision:</strong> Beat consistency</p>
						<p>• <strong>Harmonic Coherence:</strong> Chord clarity</p>
					</div>
				</div>
			{/if}

			<!-- Songwriting Quality (NEW!) -->
			{#if track.lyrical_genome?.songwriting_quality}
				<div class="border rounded-lg p-6 bg-gradient-to-br from-amber-50 to-transparent dark:from-amber-950/20">
					<div class="flex items-center gap-2 mb-4">
						<BookOpen class="h-5 w-5 text-amber-600" />
						<h2 class="text-xl font-semibold">Songwriting Quality</h2>
					</div>
					
					<div class="text-center mb-4">
						<div class="text-5xl font-bold text-amber-600 mb-2">
							{track.lyrical_genome?.songwriting_quality?.overall_score?.toFixed(0) ?? 'N/A'}
						</div>
						<div class="text-lg font-semibold px-4 py-2 rounded-full inline-block {getGradeColor(track.lyrical_genome.songwriting_quality.grade)}">
							Grade: {track.lyrical_genome.songwriting_quality.grade}
						</div>
					</div>

				<div class="space-y-3">
					{#each Object.entries(track.lyrical_genome.songwriting_quality?.components ?? {}) as [key, component]}
						<div>
							<div class="flex justify-between text-sm mb-1">
								<span class="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
								<span class="font-medium">{component?.score?.toFixed(0) ?? 'N/A'}/{component?.max ?? 'N/A'}</span>
							</div>
							<div class="h-2 bg-secondary rounded-full overflow-hidden">
								<div
									class="h-full bg-amber-500 transition-all"
									style="width: {component?.score != null && component?.max != null ? (component.score / component.max) * 100 : 0}%"
								></div>
							</div>
						</div>
					{/each}
				</div>

					{#if track.lyrical_genome.songwriting_quality.insights}
						<div class="mt-4 pt-4 border-t space-y-2">
							{#each track.lyrical_genome.songwriting_quality.insights as insight}
								<div class="flex items-start gap-2 text-sm">
									<Lightbulb class="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
									<span class="text-muted-foreground">{insight}</span>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- NEW FEATURES: Mastering Quality, Chord Analysis, AI Lyric Critique -->
		<div class="space-y-6 mb-6">
			<!-- Mastering Quality -->
			{#if track.mastering_quality}
				<MasteringQualityCard data={track.mastering_quality} />
			{/if}

			<!-- Chord Progression Analysis -->
			{#if track.chord_analysis}
				<ChordProgressionCard data={track.chord_analysis} />
			{/if}

			<!-- AI Lyric Critique -->
			{#if track.lyrics}
				<LyricCritiqueCard
					data={track.ai_lyric_critique}
					trackId={track.id}
					onGenerate={generateLyricCritique}
					isGenerating={generatingCritique}
				/>
			{/if}
		</div>

		<!-- COMPETITIVE FEATURES: Viral Segments, Tags, Pitch Copy -->
		<div class="space-y-6 mb-6">
			<!-- Viral Hook Segments -->
			{#if track.hook_data?.viral_segments}
				<ViralSegmentsCard 
					segments={track.hook_data.viral_segments} 
					trackId={track.id}
					onJumpTo={jumpToTime}
				/>
			{/if}

			<!-- AI-Generated Tags -->
			<TrackTagsCard
				moods={track.track_tags?.moods}
				commercialTags={track.track_tags?.commercial_tags}
				useCases={track.track_tags?.use_cases}
				soundsLike={track.track_tags?.sounds_like}
				isGenerating={generatingTags}
				onRegenerate={generateTags}
			/>

			<!-- AI-Generated Pitch Copy -->
			<PitchCopyCard
				elevatorPitch={track.pitch_copy?.elevator_pitch}
				shortDescription={track.pitch_copy?.short_description}
				syncPitch={track.pitch_copy?.sync_pitch}
				cost={track.pitch_copy?.cost}
				generatedAt={track.pitch_copy?.generated_at}
				isGenerating={generatingPitch}
				onGenerate={generatePitchCopy}
			/>
		</div>

		<!-- PREDICTIVE ANALYTICS & BUSINESS INTELLIGENCE -->
		<div class="mb-6">
			<h2 class="text-2xl font-bold mb-4 flex items-center gap-2">
				<TrendingUp class="h-6 w-6 text-purple-600" />
				Predictive Analytics & Market Intelligence
			</h2>
		</div>

		<div class="space-y-6 mb-6">
			<!-- Breakout Score -->
			<BreakoutScoreCard
				score={track.breakout_score || 75}
				confidence={track.confidence || 85}
				predictions={{
					days_7: track.predicted_7d || 12.5,
					days_14: track.predicted_14d || 28.3,
					days_28: track.predicted_28d || 65.7
				}}
				factors={{
					'Sonic Quality': 85,
					'Market Fit': 78,
					'Playlist Momentum': 82,
					'Social Signals': 71,
					'Release Timing': 88
				}}
			/>

			<!-- Market Position (RIYL) -->
			<MarketPositionCard
				recommendedIfYouLike={track.track_tags?.sounds_like || ['Similar Artists', 'Will Appear Here']}
				marketPosition="Indie pop with melancholic synths and infectious hooks — sits between bedroom pop and polished radio indie. Strong playlist potential in Spotify's 'Indie Pop' and 'Chill Vibes' categories."
				similarArtists={[
					{ name: 'Clairo', similarity: 87 },
					{ name: 'Girl in Red', similarity: 84 },
					{ name: 'Boy Pablo', similarity: 82 },
					{ name: 'Beabadoobee', similarity: 79 },
					{ name: 'BENEE', similarity: 76 }
				]}
			/>

			<!-- Collaboration Opportunities -->
			<CollaborationCard
				synergy={82}
				fanbaseOverlap={34}
				successRate={71}
				suggestedArtists={[
					{ name: 'Similar Indie Artist', synergy: 89, genre: 'Indie Pop' },
					{ name: 'Compatible Producer', synergy: 85, genre: 'Electronic' },
					{ name: 'Rising Vocalist', synergy: 82, genre: 'Alternative' },
					{ name: 'Genre-Crossing Act', synergy: 78, genre: 'Bedroom Pop' }
				]}
			/>

			<!-- Growth Metrics & Insights -->
			<GrowthMetricsCard
				velocity={78}
				playlistAdds={23}
				growthRate={12.5}
				releaseWindow="Optimal release: Early Friday (12am-3am EST) for maximum algorithmic pickup. Similar artists see peak engagement Tuesday-Thursday."
				playlistMatches={[
					{ name: 'Indie Pop Essentials', compatibility: 92 },
					{ name: 'Chill Indie Vibes', compatibility: 88 },
					{ name: 'Bedroom Pop', compatibility: 85 },
					{ name: 'New Music Friday', compatibility: 79 },
					{ name: 'Fresh Finds', compatibility: 76 }
				]}
				insights={[
					'Strong momentum in 18-24 age demographic',
					'Higher save rate than skip rate indicates strong retention',
					'TikTok trending potential in #indiemusic and #chillvibes',
					'Playlist curators showing 34% higher engagement vs. genre average'
				]}
			/>

			<!-- Catalog Valuation -->
			<CatalogValueCard
				estimatedValue={45000}
				growthRate={15.3}
				revenueBreakdown={{
					streaming: 65,
					sync: 25,
					performance: 10
				}}
			/>
		</div>

		<!-- TuneScore Breakdown -->
		{#if track.tunescore?.components}
			<div class="border rounded-lg p-6 mb-6 bg-gradient-to-br from-primary/5 to-transparent">
				<h2 class="text-2xl font-semibold mb-4">TuneScore Breakdown</h2>
				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
					{#each Object.entries(track.tunescore?.components ?? {}) as [key, component]}
						<div class="bg-background rounded-lg p-4 border">
							<div class="flex justify-between items-center mb-2">
								<span class="text-sm font-medium capitalize">
									{key.replace(/_/g, ' ')}
								</span>
								<span class="text-sm font-bold">
									{component?.score?.toFixed(0) ?? 'N/A'}/{component?.max ?? 'N/A'}
								</span>
							</div>
							<div class="h-2 bg-secondary rounded-full overflow-hidden">
								<div
									class="h-full bg-primary transition-all"
									style="width: {component?.percentage ?? 0}%"
								></div>
							</div>
							<div class="text-xs text-muted-foreground mt-1">
								{component?.percentage?.toFixed(0) ?? '0'}%
							</div>
						</div>
					{/each}
				</div>

				{#if track.tunescore.insights}
					<div class="mt-4 space-y-2">
						<h3 class="font-semibold text-sm">Insights:</h3>
						{#each track.tunescore.insights as insight}
							<p class="text-sm text-muted-foreground pl-4 border-l-2 border-primary/30">
								{insight}
							</p>
						{/each}
					</div>
				{/if}

				<!-- AI Breakout Prediction (NEW!) -->
				{#if track.tunescore.ai_breakout}
					<div class="mt-6 pt-6 border-t">
						<div class="flex items-center gap-2 mb-4">
							<TrendingUp class="h-5 w-5 text-green-600" />
							<h3 class="text-lg font-semibold">🚀 AI Breakout Prediction</h3>
						</div>
						
						{#if track.tunescore.ai_breakout.prediction}
							<div class="bg-gradient-to-r from-green-50 to-transparent dark:from-green-950/20 rounded-lg p-4 mb-4">
								<div class="flex items-start gap-3">
									<div class="flex-shrink-0">
										<div class="text-3xl font-bold text-green-600">
											{track.tunescore.ai_breakout.prediction.breakout_score}/10
										</div>
										<div class="text-xs text-muted-foreground text-center mt-1">Score</div>
									</div>
									<div class="flex-1">
										<h4 class="font-semibold mb-2">Breakout Potential: {track.tunescore.ai_breakout.prediction.breakout_potential}</h4>
										<p class="text-sm text-muted-foreground">{track.tunescore.ai_breakout.prediction.reasoning}</p>
									</div>
								</div>
							</div>
						{/if}

						{#if track.tunescore.ai_breakout.strategy && track.tunescore.ai_breakout.strategy.length > 0}
							<div class="mb-4">
								<h4 class="text-sm font-semibold mb-2">📈 Strategic Recommendations:</h4>
								<ul class="space-y-2">
									{#each track.tunescore.ai_breakout.strategy as item}
										<li class="flex items-start gap-2 text-sm">
											<span class="text-green-600 font-bold">•</span>
											<span>{item}</span>
										</li>
									{/each}
								</ul>
							</div>
						{/if}

						{#if track.tunescore.ai_breakout.target_platforms && track.tunescore.ai_breakout.target_platforms.length > 0}
							<div class="mb-4">
								<h4 class="text-sm font-semibold mb-2">🎯 Target Platforms:</h4>
								<div class="flex flex-wrap gap-2">
									{#each track.tunescore.ai_breakout.target_platforms as platform}
										<span class="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full text-xs font-medium">
											{platform}
										</span>
									{/each}
								</div>
							</div>
						{/if}

						{#if track.tunescore?.ai_breakout?.cost}
							<p class="text-xs text-muted-foreground mt-2">
								AI Analysis Cost: ${track.tunescore.ai_breakout.cost.toFixed(4)}
							</p>
						{/if}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Main Analysis Grid -->
		<div class="grid lg:grid-cols-2 gap-6 mb-6">
			<!-- Sonic Genome -->
			{#if track.sonic_genome}
				<div class="border rounded-lg p-6">
					<div class="flex items-center gap-2 mb-4">
						<Music class="h-5 w-5 text-primary" />
						<h2 class="text-xl font-semibold">Sonic Genome</h2>
					</div>
					<div class="space-y-3 text-sm">
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Tempo:</span>
							<span class="font-medium">{track.sonic_genome?.tempo?.toFixed(1) ?? 'N/A'} BPM</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Key:</span>
							<span class="font-medium">
								{track.sonic_genome?.key_name || track.sonic_genome?.key || 'N/A'}
								{#if track.sonic_genome?.key !== undefined && track.sonic_genome?.key_name}
									<span class="text-xs text-muted-foreground ml-1">({track.sonic_genome.key})</span>
								{/if}
							</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Duration:</span>
							<span class="font-medium">
								{track.sonic_genome?.duration ? `${Math.floor(track.sonic_genome.duration / 60)}:${String(Math.floor(track.sonic_genome.duration % 60)).padStart(2, '0')}` : 'N/A'}
							</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Loudness:</span>
							<span class="font-medium">{track.sonic_genome?.loudness?.toFixed(1) ?? 'N/A'} dB</span>
						</div>
						
						<!-- Progress bars for key metrics -->
						<div class="pt-2 space-y-2">
							<div>
								<div class="flex justify-between text-xs mb-1">
									<span>Energy</span>
									<span>{track.sonic_genome?.energy != null ? (track.sonic_genome.energy * 100).toFixed(0) : 'N/A'}%</span>
								</div>
								<div class="h-2 bg-secondary rounded-full overflow-hidden">
									<div
										class="h-full bg-green-500 transition-all"
										style="width: {(track.sonic_genome?.energy ?? 0) * 100}%"
									></div>
								</div>
							</div>

							<div>
								<div class="flex justify-between text-xs mb-1">
									<span>Danceability</span>
									<span>{track.sonic_genome?.danceability != null ? (track.sonic_genome.danceability * 100).toFixed(0) : 'N/A'}%</span>
								</div>
								<div class="h-2 bg-secondary rounded-full overflow-hidden">
									<div
										class="h-full bg-blue-500 transition-all"
										style="width: {(track.sonic_genome?.danceability ?? 0) * 100}%"
									></div>
								</div>
							</div>

							<div>
								<div class="flex justify-between text-xs mb-1">
									<span>Valence</span>
									<span>{track.sonic_genome?.valence != null ? (track.sonic_genome.valence * 100).toFixed(0) : 'N/A'}%</span>
								</div>
								<div class="h-2 bg-secondary rounded-full overflow-hidden">
									<div
										class="h-full bg-yellow-500 transition-all"
										style="width: {(track.sonic_genome?.valence ?? 0) * 100}%"
									></div>
								</div>
							</div>

							<div>
								<div class="flex justify-between text-xs mb-1">
									<span>Acousticness</span>
									<span>{track.sonic_genome?.acousticness != null ? (track.sonic_genome.acousticness * 100).toFixed(0) : 'N/A'}%</span>
								</div>
								<div class="h-2 bg-secondary rounded-full overflow-hidden">
									<div
										class="h-full bg-purple-500 transition-all"
										style="width: {(track.sonic_genome?.acousticness ?? 0) * 100}%"
									></div>
								</div>
							</div>
						</div>

						<!-- Raw quality indicators (if available) -->
						{#if track.sonic_genome?.timing_precision_score !== undefined || track.sonic_genome?.harmonic_coherence_score !== undefined}
							<div class="pt-4 mt-4 border-t space-y-2 text-xs">
								{#if track.sonic_genome?.timing_precision_score !== undefined}
									<div class="flex justify-between items-center">
										<span class="text-muted-foreground">Timing Precision Score:</span>
										<span class="font-medium">{track.sonic_genome.timing_precision_score.toFixed(0)}/100</span>
									</div>
								{/if}
								{#if track.sonic_genome?.harmonic_coherence_score !== undefined}
									<div class="flex justify-between items-center">
										<span class="text-muted-foreground">Harmonic Coherence Score:</span>
										<span class="font-medium">{track.sonic_genome.harmonic_coherence_score.toFixed(0)}/100</span>
									</div>
								{/if}
							</div>
						{/if}
					</div>
				</div>
			{/if}

			<!-- Lyrical Genome -->
			{#if track.lyrical_genome}
				<div class="border rounded-lg p-6">
					<div class="flex items-center gap-2 mb-4">
						<FileText class="h-5 w-5 text-primary" />
						<h2 class="text-xl font-semibold">Lyrical Genome</h2>
					</div>
					<div class="space-y-3 text-sm">
						{#if track.lyrical_genome.overall_sentiment}
							<div class="flex justify-between items-center">
								<span class="text-muted-foreground">Sentiment:</span>
								<span class="font-medium {getSentimentColor(track.lyrical_genome?.overall_sentiment?.compound ?? 0)}">
									{formatSentiment(track.lyrical_genome?.overall_sentiment?.compound ?? 0)}
									({track.lyrical_genome?.overall_sentiment?.compound != null ? (track.lyrical_genome.overall_sentiment.compound * 100).toFixed(0) : 'N/A'})
								</span>
							</div>
						{/if}
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Word Count:</span>
							<span class="font-medium">{track.lyrical_genome.word_count}</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Line Count:</span>
							<span class="font-medium">{track.lyrical_genome.line_count}</span>
						</div>
						{#if track.lyrical_genome.themes && track.lyrical_genome.themes.length > 0}
							<div>
								<span class="text-muted-foreground">Themes:</span>
								<div class="flex flex-wrap gap-1 mt-2">
									{#each track.lyrical_genome.themes as theme}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border text-foreground">
											{theme}
										</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				</div>
			{/if}
		</div>

		<!-- Song Sections Breakdown (Verse, Chorus, Bridge, etc.) -->
		{#if track.lyrical_genome?.sections && track.lyrical_genome.sections.length > 0}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<FileText class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Song Sections Breakdown</h2>
				</div>
				<div class="space-y-3">
					{#each track.lyrical_genome.sections as section, i}
						<div class="border-l-4 border-primary/50 bg-secondary/20 rounded-lg p-4">
							<button
								onclick={() => toggleSection(`full-section-${i}`)}
								class="flex items-center justify-between w-full font-semibold text-primary hover:text-primary/80 transition-colors mb-2"
							>
								<div class="flex items-center gap-3">
									<span class="text-lg capitalize">[{section.type}]</span>
									<span class="text-xs text-muted-foreground">
										{section.line_count} line{section.line_count !== 1 ? 's' : ''}
									</span>
								</div>
								<span class="text-xs text-muted-foreground">
									{expandedSection === `full-section-${i}` ? '▼' : '▶'}
								</span>
							</button>
							
							{#if expandedSection === `full-section-${i}`}
								<pre class="whitespace-pre-wrap font-mono text-sm text-foreground bg-background p-3 rounded border mt-2 overflow-x-auto">
{section.content}
								</pre>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Song Structure (NEW!) -->
		{#if track.lyrical_genome?.structure}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<Target class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Song Structure</h2>
				</div>

				{#if track.lyrical_genome.structure.pattern}
					<div class="mb-4 p-4 bg-secondary/30 rounded-lg">
						<div class="text-sm text-muted-foreground mb-2">Structure Pattern:</div>
						<div class="font-mono text-sm">
							{track.lyrical_genome.structure.pattern}
						</div>
					</div>
				{/if}

				<div class="grid md:grid-cols-3 gap-4">
					<div class="flex items-center gap-2">
						{#if track.lyrical_genome.structure.has_bridge}
							<CheckCircle2 class="h-4 w-4 text-green-600" />
						{:else}
							<AlertCircle class="h-4 w-4 text-orange-600" />
						{/if}
						<span class="text-sm">Bridge</span>
					</div>

					<div class="flex items-center gap-2">
						{#if track.lyrical_genome.structure.has_pre_chorus}
							<CheckCircle2 class="h-4 w-4 text-green-600" />
						{:else}
							<AlertCircle class="h-4 w-4 text-orange-600" />
						{/if}
						<span class="text-sm">Pre-Chorus</span>
					</div>

					<div class="flex items-center gap-2">
						<CheckCircle2 class="h-4 w-4 text-blue-600" />
						<span class="text-sm">{track.lyrical_genome.structure.total_sections} Sections</span>
					</div>
				</div>

				{#if track.lyrical_genome?.structure?.section_counts}
					<div class="mt-4 pt-4 border-t">
						<div class="text-sm text-muted-foreground mb-2">Section Counts:</div>
						<div class="flex flex-wrap gap-2">
							{#each Object.entries(track.lyrical_genome.structure.section_counts ?? {}) as [type, count]}
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-secondary text-secondary-foreground">
									{type}: {count}x
								</span>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Lyrics with Structure Annotations (NEW!) -->
		{#if track.lyrics}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center gap-2">
						<Mic2 class="h-5 w-5 text-primary" />
						<h2 class="text-xl font-semibold">Lyrics</h2>
						
						<!-- Lyrics Source Badge -->
						{#if track.lyrics_source === 'lrclib'}
							<Badge variant="default" class="bg-green-500 text-white">
								✓ Database Verified
							</Badge>
						{:else if track.lyrics_source === 'whisper'}
							<Badge variant="outline" class="border-yellow-500 text-yellow-700 dark:text-yellow-400">
								🤖 AI Transcribed ({Math.round((track.lyrics_confidence || 0) * 100)}%)
							</Badge>
						{:else if track.lyrics_source === 'user' || track.lyrics_source === 'user_verified'}
							<Badge variant="default" class="bg-blue-500 text-white">
								User Provided
							</Badge>
						{/if}
					</div>
					<div class="flex items-center gap-2">
						{#if !editingLyrics}
							<Button variant="outline" size="sm" onclick={() => { editingLyrics = true; editedLyrics = track.lyrics; }}>
								Edit
							</Button>
						{/if}
						<Button variant="ghost" size="sm" onclick={() => (showLyrics = !showLyrics)}>
							{showLyrics ? 'Hide' : 'Show'}
						</Button>
					</div>
				</div>

				{#if showLyrics}
					{#if editingLyrics}
						<!-- Edit Mode -->
						<div class="space-y-4">
							<textarea
								bind:value={editedLyrics}
								rows="20"
								class="w-full px-3 py-2 rounded-md border border-input bg-background font-mono text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
							></textarea>
							<div class="flex items-center gap-2">
								<Button 
									size="sm" 
									onclick={async () => {
										try {
											await api.tracks.updateLyrics(track.id, { lyrics: editedLyrics });
											track.lyrics = editedLyrics;
											track.lyrics_source = 'user_verified';
											track.lyrics_confidence = 1.0;
											editingLyrics = false;
										} catch (e) {
											console.error('Failed to update lyrics:', e);
										}
									}}
								>
									Save Changes
								</Button>
								<Button variant="outline" size="sm" onclick={() => { editingLyrics = false; }}>
									Cancel
								</Button>
							</div>
						</div>
					{:else}
						<!-- View Mode -->
						<div class="space-y-4">
							{#if track.lyrical_genome?.sections && track.lyrical_genome.sections.length > 0}
								<!-- Structured lyrics with sections -->
								{#each track.lyrical_genome.sections as section, i}
									<div class="border-l-4 border-primary/30 pl-4 py-2">
										<button
											onclick={() => toggleSection(`section-${i}`)}
											class="flex items-center gap-2 font-semibold text-primary hover:underline mb-2 capitalize"
										>
											<span>[{section.type}]</span>
											<span class="text-xs text-muted-foreground">
												{section.line_count} lines
											</span>
										</button>
										
										{#if expandedSection === `section-${i}` || expandedSection === null}
											<pre class="whitespace-pre-wrap font-mono text-sm text-foreground mt-2">
{section.content}
											</pre>
										{/if}
									</div>
								{/each}
							{:else}
								<!-- Plain lyrics -->
								<pre class="whitespace-pre-wrap font-mono text-sm text-foreground bg-secondary/20 p-4 rounded-lg max-h-96 overflow-y-auto">
{track.lyrics}
								</pre>
							{/if}
						</div>
					{/if}
				{/if}
			</div>
		{/if}

		<!-- Hook Detection -->
		{#if track.hook_data}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<Activity class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Viral Hook Detection</h2>
				</div>
				<div class="grid md:grid-cols-3 gap-4">
					<div class="text-center p-4 bg-secondary/20 rounded-lg">
						<div class="text-3xl font-bold text-primary mb-1">
							{track.hook_data?.hook_score?.toFixed(0) ?? 'N/A'}
						</div>
						<div class="text-sm text-muted-foreground">Hook Score (out of 100)</div>
					</div>
					<div class="text-center p-4 bg-secondary/20 rounded-lg">
						<div class="text-2xl font-bold mb-1">
							{track.hook_data?.start_time?.toFixed(0) ?? 'N/A'}s - {track.hook_data?.end_time?.toFixed(0) ?? 'N/A'}s
						</div>
						<div class="text-sm text-muted-foreground">Time Segment</div>
					</div>
					<div class="text-center p-4 bg-secondary/20 rounded-lg">
						<div class="text-2xl font-bold mb-1">
							{track.hook_data?.duration?.toFixed(0) ?? 'N/A'}s
						</div>
						<div class="text-sm text-muted-foreground">Duration</div>
					</div>
				</div>
				{#if track.hook_data.rationale}
					<div class="mt-4 p-4 bg-secondary/20 rounded-lg">
						<div class="text-sm font-medium mb-1">Analysis:</div>
						<p class="text-sm text-muted-foreground">{track.hook_data.rationale}</p>
					</div>
				{/if}

				<!-- AI Hook Explanation (NEW!) -->
				{#if track.hook_data.ai_explanation}
					<div class="mt-4 bg-gradient-to-r from-blue-50 to-transparent dark:from-blue-950/20 rounded-lg p-4 border-l-4 border-blue-500">
						<div class="flex items-start gap-2 mb-3">
							<Lightbulb class="h-4 w-4 text-blue-600 mt-1 flex-shrink-0" />
							<div class="flex-1">
								<h3 class="text-sm font-semibold mb-1">🎣 AI Hook Analysis</h3>
								<p class="text-sm text-muted-foreground">{track.hook_data.ai_explanation.explanation}</p>
							</div>
						</div>

						{#if track.hook_data.ai_explanation.sync_potential}
							<div class="mb-3">
								<h4 class="text-xs font-semibold mb-1">🎬 Sync Licensing Potential</h4>
								<p class="text-xs text-muted-foreground">{track.hook_data.ai_explanation.sync_potential}</p>
							</div>
						{/if}

						{#if track.hook_data.ai_explanation.tiktok_timing}
							<div class="mb-3">
								<h4 class="text-xs font-semibold mb-1">📱 TikTok Timing</h4>
								<p class="text-xs text-muted-foreground">{track.hook_data.ai_explanation.tiktok_timing}</p>
							</div>
						{/if}

						{#if track.hook_data.ai_explanation.viral_factors && track.hook_data.ai_explanation.viral_factors.length > 0}
							<div>
								<h4 class="text-xs font-semibold mb-1">⚡ Viral Factors:</h4>
								<div class="flex flex-wrap gap-1">
									{#each track.hook_data.ai_explanation.viral_factors as factor}
										<span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-xs">
											{factor}
										</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Lyrical Complexity & Repetition -->
		{#if track.lyrical_genome}
			<div class="grid md:grid-cols-2 gap-6 mb-6">
				{#if track.lyrical_genome.complexity}
					<div class="border rounded-lg p-6">
						<div class="flex items-center gap-2 mb-4">
							<Type class="h-5 w-5 text-primary" />
							<h2 class="text-xl font-semibold">Lyrical Complexity</h2>
						</div>
						<div class="space-y-3 text-sm">
							<div>
								<div class="flex justify-between mb-1">
									<span class="text-muted-foreground">Vocabulary Richness:</span>
									<span class="font-medium">{track.lyrical_genome?.complexity?.vocabulary_richness != null ? (track.lyrical_genome.complexity.vocabulary_richness * 100).toFixed(1) : 'N/A'}%</span>
								</div>
								<div class="h-2 bg-secondary rounded-full overflow-hidden">
									<div
										class="h-full bg-primary transition-all"
										style="width: {(track.lyrical_genome?.complexity?.vocabulary_richness ?? 0) * 100}%"
									></div>
								</div>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-muted-foreground">Unique Words:</span>
								<span class="font-medium">
									{track.lyrical_genome?.complexity?.unique_word_count ?? 'N/A'} / {track.lyrical_genome?.complexity?.total_word_count ?? 'N/A'}
								</span>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-muted-foreground">Rhyme Density:</span>
								<span class="font-medium">{track.lyrical_genome?.complexity?.rhyme_density != null ? (track.lyrical_genome.complexity.rhyme_density * 100).toFixed(1) : 'N/A'}%</span>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-muted-foreground">Avg Line Length:</span>
								<span class="font-medium">{track.lyrical_genome?.complexity?.avg_line_length?.toFixed(1) ?? 'N/A'} words</span>
							</div>
						</div>
					</div>
				{/if}

				{#if track.lyrical_genome.repetition}
					<div class="border rounded-lg p-6">
						<div class="flex items-center gap-2 mb-4">
							<Repeat class="h-5 w-5 text-primary" />
							<h2 class="text-xl font-semibold">Repetition Analysis</h2>
						</div>
						<div class="space-y-3 text-sm">
							<div class="flex justify-between items-center">
								<span class="text-muted-foreground">Repetition Score:</span>
								<span class="font-medium">{track.lyrical_genome?.repetition?.repetition_score?.toFixed(1) ?? 'N/A'}%</span>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-muted-foreground">Strong Hook:</span>
								<span class="font-medium">
									{track.lyrical_genome.repetition.has_strong_hook ? '✓ Yes' : '✗ No'}
								</span>
							</div>
							{#if track.lyrical_genome.repetition.most_repeated_line}
								<div>
									<div class="text-muted-foreground mb-2">Most Repeated:</div>
									<p class="font-medium italic bg-secondary/30 p-3 rounded">
										"{track.lyrical_genome.repetition.most_repeated_line}"
									</p>
									<p class="text-xs text-muted-foreground mt-1">
										Repeated {track.lyrical_genome.repetition.repetition_count} times
									</p>
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Emotional Arc -->
		{#if track.lyrical_genome?.emotional_arc && track.lyrical_genome.emotional_arc.length > 0}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<TrendingUp class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Emotional Arc</h2>
					<span class="text-sm text-muted-foreground ml-auto">
						{track.lyrical_genome.emotional_arc.length} data points
					</span>
				</div>
				
				<!-- Simple SVG chart -->
				<div class="w-full h-48 bg-secondary/20 rounded-lg p-4">
					<svg class="w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
						<!-- Grid lines -->
						<line x1="0" y1="50" x2="400" y2="50" stroke="currentColor" stroke-opacity="0.2" stroke-width="0.5" />
						<line x1="0" y1="25" x2="400" y2="25" stroke="currentColor" stroke-opacity="0.1" stroke-width="0.5" />
						<line x1="0" y1="75" x2="400" y2="75" stroke="currentColor" stroke-opacity="0.1" stroke-width="0.5" />
						
						<!-- Emotional arc line -->
						<polyline
							fill="none"
							stroke="hsl(var(--primary))"
							stroke-width="2"
							points={track.lyrical_genome.emotional_arc
								.map((point, i) => {
									const x = (i / (track.lyrical_genome.emotional_arc.length - 1)) * 400;
									const y = 50 - (point.compound * 50); // Map -1 to 1 → 100 to 0
									return `${x},${y}`;
								})
								.join(' ')}
						/>
					</svg>
				</div>
				
				<div class="flex justify-between text-xs text-muted-foreground mt-2">
					<span>Start</span>
					<span>Positive (+1.0)</span>
					<span>Neutral (0)</span>
					<span>Negative (-1.0)</span>
					<span>End</span>
				</div>
			</div>
		{/if}

		<!-- Advanced Audio Features -->
		{#if track.sonic_genome}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<BarChart3 class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Advanced Audio Features</h2>
				</div>
				<div class="grid md:grid-cols-3 gap-4 text-sm">
					<div>
						<h3 class="font-semibold mb-2">Spectral Centroid</h3>
						<div class="space-y-1 text-muted-foreground">
							<div class="flex justify-between">
								<span>Mean:</span>
								<span>{track.sonic_genome?.spectral_centroid_mean?.toFixed(0) ?? 'N/A'} Hz</span>
							</div>
							<div class="flex justify-between">
								<span>Std:</span>
								<span>{track.sonic_genome?.spectral_centroid_std?.toFixed(0) ?? 'N/A'} Hz</span>
							</div>
						</div>
					</div>

					<div>
						<h3 class="font-semibold mb-2">Spectral Rolloff</h3>
						<div class="space-y-1 text-muted-foreground">
							<div class="flex justify-between">
								<span>Mean:</span>
								<span>{track.sonic_genome?.spectral_rolloff_mean?.toFixed(0) ?? 'N/A'} Hz</span>
							</div>
							<div class="flex justify-between">
								<span>Std:</span>
								<span>{track.sonic_genome?.spectral_rolloff_std?.toFixed(0) ?? 'N/A'} Hz</span>
							</div>
						</div>
					</div>

					{#if track.sonic_genome.spectral_bandwidth_mean !== undefined}
						<div>
							<h3 class="font-semibold mb-2">Spectral Bandwidth</h3>
							<div class="space-y-1 text-muted-foreground">
								<div class="flex justify-between">
									<span>Mean:</span>
									<span>{track.sonic_genome?.spectral_bandwidth_mean?.toFixed(0) ?? 'N/A'} Hz</span>
								</div>
								<div class="flex justify-between">
									<span>Std:</span>
									<span>{track.sonic_genome?.spectral_bandwidth_std?.toFixed(0) ?? 'N/A'} Hz</span>
								</div>
							</div>
						</div>
					{/if}

					<div>
						<h3 class="font-semibold mb-2">Zero Crossing Rate</h3>
						<div class="space-y-1 text-muted-foreground">
							<div class="flex justify-between">
								<span>Mean:</span>
								<span>{track.sonic_genome?.zero_crossing_rate_mean?.toFixed(3) ?? 'N/A'}</span>
							</div>
							<div class="flex justify-between">
								<span>Std:</span>
								<span>{track.sonic_genome?.zero_crossing_rate_std?.toFixed(3) ?? 'N/A'}</span>
							</div>
						</div>
					</div>

					{#if track.sonic_genome.rms_mean !== undefined}
						<div>
							<h3 class="font-semibold mb-2">RMS Energy</h3>
							<div class="space-y-1 text-muted-foreground">
								<div class="flex justify-between">
									<span>Mean:</span>
									<span>{track.sonic_genome?.rms_mean?.toFixed(4) ?? 'N/A'}</span>
								</div>
								<div class="flex justify-between">
									<span>Std:</span>
									<span>{track.sonic_genome?.rms_std?.toFixed(4) ?? 'N/A'}</span>
								</div>
							</div>
						</div>
					{/if}

					{#if track.sonic_genome.mfcc_means && track.sonic_genome.mfcc_means.length > 0}
						<div>
							<h3 class="font-semibold mb-2">MFCC Timbre (Summary)</h3>
							<div class="space-y-1 text-muted-foreground">
								<div class="flex justify-between">
									<span>MFCC Count:</span>
									<span>{track.sonic_genome.mfcc_means.length} coefficients</span>
								</div>
								<div class="flex justify-between">
									<span>Mean Range:</span>
									<span>
										{track.sonic_genome?.mfcc_means && track.sonic_genome.mfcc_means.length > 0 
											? `${Math.min(...track.sonic_genome.mfcc_means).toFixed(1)} to ${Math.max(...track.sonic_genome.mfcc_means).toFixed(1)}`
											: 'N/A'}
									</span>
								</div>
								<div class="flex justify-between">
									<span>Avg Std:</span>
									<span>
										{track.sonic_genome?.mfcc_stds && track.sonic_genome.mfcc_stds.length > 0
											? (track.sonic_genome.mfcc_stds.reduce((a, b) => a + b, 0) / track.sonic_genome.mfcc_stds.length).toFixed(2)
											: 'N/A'}
									</span>
								</div>
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}

		<!-- External Links -->
		{#if track.spotify_id}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<ExternalLink class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">External Links</h2>
				</div>
				<div class="flex flex-wrap gap-4">
					<a
						href={`https://open.spotify.com/track/${track.spotify_id}`}
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
					>
						<ExternalLink class="h-4 w-4" />
						<span>Listen on Spotify</span>
					</a>
				</div>
			</div>
		{/if}

		<!-- RIYL Recommendations -->
		{#if riylRecommendations && riylRecommendations.recommendations && riylRecommendations.recommendations.length > 0}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<Radio class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Recommended If You Like (RIYL)</h2>
				</div>
				<p class="text-sm text-muted-foreground mb-4">
					{riylRecommendations.message || `Found ${riylRecommendations.count} similar tracks`}
				</p>
				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each riylRecommendations.recommendations as rec}
						<a
							href={`/tracks/${rec.track_id}`}
							class="block border rounded-lg p-4 hover:bg-secondary/50 transition-colors"
						>
							<div class="flex items-start justify-between mb-2">
								<div class="flex-1">
									<h3 class="font-semibold text-sm mb-1">{rec.title}</h3>
									<p class="text-xs text-muted-foreground">{rec.artist_name || 'Unknown Artist'}</p>
								</div>
								{#if rec.similarity_score}
									<span class="text-xs font-medium text-primary ml-2">
										{(rec.similarity_score * 100).toFixed(0)}%
									</span>
								{/if}
							</div>
							{#if rec.similarity_score}
								<div class="h-1 bg-secondary rounded-full overflow-hidden mt-2">
									<div
										class="h-full bg-primary transition-all"
										style="width: {rec.similarity_score * 100}%"
									></div>
								</div>
							{/if}
						</a>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Similar Tracks -->
		{#if similarTracks && similarTracks.length > 0}
			<div class="border rounded-lg p-6 mb-6">
				<div class="flex items-center gap-2 mb-4">
					<Music class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Similar Tracks</h2>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each similarTracks as similarTrack}
						<a
							href={`/tracks/${similarTrack.track_id}`}
							class="block border rounded-lg p-4 hover:bg-secondary/50 transition-colors"
						>
							<div class="flex items-start justify-between mb-2">
								<div class="flex-1">
									<h3 class="font-semibold text-sm mb-1">{similarTrack.title}</h3>
									<p class="text-xs text-muted-foreground">{similarTrack.artist_name || 'Unknown Artist'}</p>
								</div>
								{#if similarTrack.similarity_score}
									<span class="text-xs font-medium text-primary ml-2">
										{(similarTrack.similarity_score * 100).toFixed(0)}%
									</span>
								{/if}
							</div>
							{#if similarTrack.similarity_score}
								<div class="h-1 bg-secondary rounded-full overflow-hidden mt-2">
									<div
										class="h-full bg-primary transition-all"
										style="width: {similarTrack.similarity_score * 100}%"
									></div>
								</div>
							{/if}
						</a>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>
