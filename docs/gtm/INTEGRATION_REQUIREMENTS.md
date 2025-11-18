# Phase 1 Marketing & Data Integration Requirements

## Overview
This document outlines the technical requirements for integrating marketing tools and data sources into TuneScore. These integrations will enable artists to track their growth across platforms and measure ROI on marketing campaigns.

**Priority:** Phase 2 (after Product Hunt launch)
**Timeline:** 4-8 weeks
**Goal:** Unified dashboard showing all artist data in one place

---

## Integration Priority Matrix

| Integration | Priority | Complexity | Value | Timeline |
|------------|----------|------------|-------|----------|
| **CSV Universal Import** | P0 (Critical) | Low | High | Week 1 |
| **Instagram Basic Display API** | P1 (High) | Medium | High | Week 2-3 |
| **TikTok Scraper** | P1 (High) | High | High | Week 3-4 |
| **SubmitHub CSV Import** | P2 (Medium) | Low | Medium | Week 5 |
| **Facebook/Meta API** | P3 (Low) | Medium | Low | Week 6-7 |
| **Twitter API** | P3 (Low) | Low | Low | Week 8 |

---

## P0: CSV Universal Import (Week 1)

### Purpose
Allow artists to import data from any source (DistroKid, CD Baby, TuneCore, SubmitHub, etc.) via CSV upload.

### Technical Requirements

**Backend Implementation:**
```python
# backend/app/api/routers/integrations.py

from fastapi import UploadFile, HTTPException
import pandas as pd
from typing import Any

@router.post("/import-csv")
async def import_generic_csv(
    file: UploadFile,
    mapping: dict[str, str],  # User maps CSV columns to our fields
    source: str,  # "distrokid", "cd_baby", "tunecore", "custom"
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Universal CSV importer with column mapping.
    
    Args:
        file: CSV file upload
        mapping: Column mapping (e.g., {"Track Name": "track_title", "Streams": "spotify_streams"})
        source: Data source identifier
        db: Database session
        user_id: Current user ID
        
    Returns:
        Import summary (rows imported, errors, etc.)
    """
    try:
        # Read CSV
        df = pd.read_csv(file.file)
        
        # Validate columns
        missing_cols = [col for col in mapping.keys() if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing_cols}"
            )
        
        # Rename columns based on mapping
        df = df.rename(columns=mapping)
        
        # Validate required fields
        required_fields = ["track_title"]  # Minimum requirement
        missing_required = [field for field in required_fields if field not in df.columns]
        if missing_required:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {missing_required}"
            )
        
        # Import data
        imported = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Find or create track
                track = await find_or_create_track(
                    db=db,
                    user_id=user_id,
                    title=row.get("track_title"),
                    artist=row.get("artist_name"),
                )
                
                # Update metrics
                if "spotify_streams" in row:
                    await update_track_metrics(
                        db=db,
                        track_id=track.id,
                        platform="spotify",
                        streams=row["spotify_streams"],
                        source=source,
                    )
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return {
            "imported": imported,
            "errors": errors,
            "total_rows": len(df),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import CSV: {str(e)}"
        )
```

**Frontend Implementation:**
```typescript
// frontend/src/routes/integrations/csv-import/+page.svelte

<script lang="ts">
  import { onMount } from 'svelte';
  import Button from '$lib/components/ui/button.svelte';
  import Card from '$lib/components/ui/card.svelte';
  import { addToast } from '$lib/stores/toast';

  let file: File | null = null;
  let csvData: any[][] = [];
  let columnMapping: Record<string, string> = {};
  let availableFields = [
    'track_title',
    'artist_name',
    'spotify_streams',
    'apple_music_streams',
    'youtube_views',
    'release_date',
  ];

  async function handleFileUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      file = target.files[0];
      
      // Parse CSV preview
      const text = await file.text();
      const rows = text.split('\n').map(row => row.split(','));
      csvData = rows.slice(0, 6); // Preview first 5 rows + header
    }
  }

  async function importCSV() {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('mapping', JSON.stringify(columnMapping));
    formData.append('source', 'custom');

    try {
      const response = await fetch('/api/v1/integrations/import-csv', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        addToast({
          type: 'success',
          message: `Imported ${result.imported} rows successfully!`,
        });
      } else {
        throw new Error('Import failed');
      }
    } catch (error) {
      addToast({
        type: 'error',
        message: 'Failed to import CSV',
      });
    }
  }
</script>

<div class="container mx-auto py-8">
  <h1 class="text-3xl font-bold mb-6">Import CSV Data</h1>

  <Card class="p-6 mb-6">
    <h2 class="text-xl font-semibold mb-4">Step 1: Upload CSV</h2>
    <input
      type="file"
      accept=".csv"
      on:change={handleFileUpload}
      class="mb-4"
    />

    {#if csvData.length > 0}
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr>
              {#each csvData[0] as header}
                <th class="text-left p-2 border">{header}</th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each csvData.slice(1) as row}
              <tr>
                {#each row as cell}
                  <td class="p-2 border">{cell}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </Card>

  {#if csvData.length > 0}
    <Card class="p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Step 2: Map Columns</h2>
      <div class="space-y-4">
        {#each csvData[0] as header}
          <div class="flex items-center gap-4">
            <span class="w-1/3 font-medium">{header}</span>
            <span>→</span>
            <select
              bind:value={columnMapping[header]}
              class="w-1/3 px-3 py-2 border rounded"
            >
              <option value="">Skip this column</option>
              {#each availableFields as field}
                <option value={field}>{field}</option>
              {/each}
            </select>
          </div>
        {/each}
      </div>
    </Card>

    <Button on:click={importCSV} size="lg">
      Import Data
    </Button>
  {/if}
</div>
```

**Database Schema:**
```sql
-- No new tables needed, uses existing track and metrics_daily tables
-- Add source field to track imports

ALTER TABLE metrics_daily ADD COLUMN IF NOT EXISTS source VARCHAR(50);
-- Values: 'spotify_api', 'youtube_api', 'csv_distrokid', 'csv_cd_baby', 'csv_custom'
```

**Success Metrics:**
- Artists can import data from DistroKid, CD Baby, TuneCore
- 90%+ successful imports (no errors)
- <5 minutes to map columns and import

---

## P1: Instagram Basic Display API (Week 2-3)

### Purpose
Track Instagram follower growth, engagement rate, and top posts.

### Technical Requirements

**API Documentation:** https://developers.facebook.com/docs/instagram-basic-display-api

**Authentication Flow:**
```python
# backend/app/services/integrations/instagram.py

import httpx
from typing import Any

class InstagramIntegration:
    """Instagram Basic Display API integration."""
    
    BASE_URL = "https://graph.instagram.com"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.client = httpx.AsyncClient()
    
    async def get_user_profile(self) -> dict[str, Any]:
        """
        Get user profile data.
        
        Returns:
            User profile (id, username, account_type, media_count)
        """
        url = f"{self.BASE_URL}/me"
        params = {
            "fields": "id,username,account_type,media_count",
            "access_token": self.access_token,
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_user_media(self, limit: int = 25) -> list[dict[str, Any]]:
        """
        Get user's recent media.
        
        Args:
            limit: Number of media items to fetch (max 25)
            
        Returns:
            List of media items (id, caption, media_type, media_url, timestamp, like_count, comments_count)
        """
        url = f"{self.BASE_URL}/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count",
            "limit": limit,
            "access_token": self.access_token,
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    
    async def get_insights(self) -> dict[str, Any]:
        """
        Get account insights (follower count, engagement rate).
        
        Note: Requires Instagram Business/Creator account
        
        Returns:
            Insights data
        """
        # Basic Display API doesn't provide follower count
        # Need to use Instagram Graph API (requires Business account)
        # For now, we'll scrape or use manual input
        raise NotImplementedError("Use Instagram Graph API for Business accounts")
```

**OAuth Flow:**
```python
# backend/app/api/routers/integrations.py

@router.get("/instagram/auth")
async def instagram_auth_redirect(
    redirect_uri: str = "https://music.quilty.app/integrations/instagram/callback"
) -> dict[str, str]:
    """
    Redirect user to Instagram OAuth page.
    
    Returns:
        Authorization URL
    """
    client_id = settings.INSTAGRAM_CLIENT_ID
    scope = "user_profile,user_media"
    
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&response_type=code"
    )
    
    return {"auth_url": auth_url}

@router.get("/instagram/callback")
async def instagram_auth_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict[str, str]:
    """
    Handle Instagram OAuth callback.
    
    Args:
        code: Authorization code from Instagram
        db: Database session
        user_id: Current user ID
        
    Returns:
        Success message
    """
    # Exchange code for access token
    client_id = settings.INSTAGRAM_CLIENT_ID
    client_secret = settings.INSTAGRAM_CLIENT_SECRET
    redirect_uri = "https://music.quilty.app/integrations/instagram/callback"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        response.raise_for_status()
        data = response.json()
    
    # Store access token
    access_token = data["access_token"]
    user_id_ig = data["user_id"]
    
    # Save to database
    # TODO: Create integration_credentials table
    
    return {"message": "Instagram connected successfully"}
```

**Rate Limits:**
- 200 requests/hour per user
- 200 requests/hour per app

**Fallback:**
- Manual input form (user enters follower count, engagement rate)
- Web scraping (use Playwright or Selenium)

**Success Metrics:**
- Artists can connect Instagram account
- Follower count updated daily
- Engagement rate calculated (likes + comments / followers)

---

## P1: TikTok Scraper (Week 3-4)

### Purpose
Track TikTok follower growth, video views, and viral content.

### Technical Requirements

**Challenge:** TikTok API has limited access (requires approval)

**Solution:** Web scraping with Playwright

**Implementation:**
```python
# backend/app/services/integrations/tiktok.py

from playwright.async_api import async_playwright
from typing import Any

class TikTokScraper:
    """TikTok profile scraper (no official API access)."""
    
    async def scrape_profile(self, username: str) -> dict[str, Any]:
        """
        Scrape TikTok profile data.
        
        Args:
            username: TikTok username (without @)
            
        Returns:
            Profile data (followers, following, likes, videos)
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to profile
                url = f"https://www.tiktok.com/@{username}"
                await page.goto(url, wait_until="networkidle")
                
                # Wait for profile to load
                await page.wait_for_selector('[data-e2e="followers-count"]', timeout=10000)
                
                # Extract data
                followers = await page.text_content('[data-e2e="followers-count"]')
                following = await page.text_content('[data-e2e="following-count"]')
                likes = await page.text_content('[data-e2e="likes-count"]')
                
                # Parse numbers (e.g., "1.2M" → 1200000)
                followers_count = self._parse_count(followers)
                following_count = self._parse_count(following)
                likes_count = self._parse_count(likes)
                
                return {
                    "username": username,
                    "followers": followers_count,
                    "following": following_count,
                    "likes": likes_count,
                    "scraped_at": datetime.utcnow().isoformat(),
                }
                
            finally:
                await browser.close()
    
    def _parse_count(self, count_str: str) -> int:
        """
        Parse TikTok count string (e.g., "1.2M" → 1200000).
        
        Args:
            count_str: Count string from TikTok
            
        Returns:
            Parsed integer count
        """
        count_str = count_str.strip().upper()
        
        if "M" in count_str:
            return int(float(count_str.replace("M", "")) * 1_000_000)
        elif "K" in count_str:
            return int(float(count_str.replace("K", "")) * 1_000)
        else:
            return int(count_str)
    
    async def scrape_video_stats(self, video_url: str) -> dict[str, Any]:
        """
        Scrape TikTok video stats.
        
        Args:
            video_url: Full TikTok video URL
            
        Returns:
            Video stats (views, likes, comments, shares)
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(video_url, wait_until="networkidle")
                
                # Extract stats
                views = await page.text_content('[data-e2e="video-views"]')
                likes = await page.text_content('[data-e2e="like-count"]')
                comments = await page.text_content('[data-e2e="comment-count"]')
                shares = await page.text_content('[data-e2e="share-count"]')
                
                return {
                    "video_url": video_url,
                    "views": self._parse_count(views),
                    "likes": self._parse_count(likes),
                    "comments": self._parse_count(comments),
                    "shares": self._parse_count(shares),
                    "scraped_at": datetime.utcnow().isoformat(),
                }
                
            finally:
                await browser.close()
```

**Dependencies:**
```toml
# backend/pyproject.toml

[tool.poetry.dependencies]
playwright = "^1.40.0"
```

**Installation:**
```bash
cd backend
poetry add playwright
poetry run playwright install chromium
```

**Rate Limiting:**
- Scrape max 1 profile per minute (avoid detection)
- Use rotating user agents
- Add random delays (2-5 seconds)

**Fallback:**
- Manual input form (user enters follower count, video views)
- TikTok API (if approved in future)

**Success Metrics:**
- Artists can track TikTok follower growth
- Video views updated daily
- Viral alert triggers when video hits 100K+ views

---

## P2: SubmitHub CSV Import (Week 5)

### Purpose
Track SubmitHub campaign performance and calculate ROI.

### Technical Requirements

**CSV Format (SubmitHub export):**
```csv
Track Name,Curator,Result,Date,Cost,Feedback
"My Song","Indie Playlist","Approved","2025-01-15","$3","Great track!"
"My Song","Chill Vibes","Rejected","2025-01-16","$3","Not a fit"
```

**Implementation:**
```python
# backend/app/services/integrations/submithub.py

async def import_submithub_campaign(
    csv_file: UploadFile,
    db: AsyncSession,
    user_id: int,
) -> dict[str, Any]:
    """
    Import SubmitHub campaign results via CSV.
    
    Args:
        csv_file: SubmitHub CSV export
        db: Database session
        user_id: Current user ID
        
    Returns:
        Import summary (campaigns imported, total cost, ROI)
    """
    df = pd.read_csv(csv_file.file)
    
    # Validate columns
    required_cols = ["Track Name", "Curator", "Result", "Date", "Cost"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {missing_cols}"
        )
    
    # Import campaigns
    imported = 0
    total_cost = 0.0
    approved = 0
    rejected = 0
    
    for _, row in df.iterrows():
        # Find track
        track = await find_track_by_title(
            db=db,
            user_id=user_id,
            title=row["Track Name"],
        )
        
        if not track:
            continue
        
        # Parse cost (e.g., "$3" → 3.0)
        cost = float(row["Cost"].replace("$", ""))
        total_cost += cost
        
        # Track result
        if row["Result"].lower() == "approved":
            approved += 1
            
            # Create playlist appearance record
            await create_playlist_appearance(
                db=db,
                track_id=track.id,
                playlist_name=row["Curator"],
                platform="submithub",
                added_at=row["Date"],
            )
        else:
            rejected += 1
    
    # Calculate ROI
    # Estimate: 1 playlist add = +1K streams = $3-5 revenue
    estimated_revenue = approved * 4.0  # $4 avg
    roi = ((estimated_revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    
    return {
        "imported": imported,
        "total_cost": total_cost,
        "approved": approved,
        "rejected": rejected,
        "estimated_revenue": estimated_revenue,
        "roi": roi,
    }
```

**Frontend Display:**
```typescript
// Show ROI on dashboard
// "You spent $150 on SubmitHub. Here's your ROI: +5K streams = $15 revenue (-90% ROI)"
```

**Success Metrics:**
- Artists can import SubmitHub campaign data
- ROI calculated automatically
- Insights: Which curators accept most, which genres work best

---

## P3: Facebook/Meta API (Week 6-7)

### Purpose
Track Facebook page likes, post engagement.

### Technical Requirements

**API Documentation:** https://developers.facebook.com/docs/graph-api

**Similar to Instagram implementation:**
- OAuth flow
- Access token storage
- Daily data sync

**Metrics:**
- Page likes
- Post reach
- Post engagement (likes, comments, shares)

**Success Metrics:**
- Artists can connect Facebook page
- Engagement metrics updated daily

---

## P3: Twitter API (Week 8)

### Purpose
Track Twitter followers, tweet engagement.

### Technical Requirements

**API Documentation:** https://developer.twitter.com/en/docs/twitter-api

**Free Tier Limits:**
- 500,000 tweets/month (read)
- 1,500 tweets/month (write)

**Metrics:**
- Follower count
- Tweet impressions
- Tweet engagement (likes, retweets, replies)

**Success Metrics:**
- Artists can connect Twitter account
- Follower growth tracked daily

---

## Database Schema Changes

### New Tables

**integration_credentials**
```sql
CREATE TABLE integration_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'instagram', 'tiktok', 'facebook', 'twitter'
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    platform_user_id VARCHAR(255),
    platform_username VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_integration_credentials_user_id ON integration_credentials(user_id);
CREATE INDEX idx_integration_credentials_platform ON integration_credentials(platform);
```

**social_media_metrics**
```sql
CREATE TABLE social_media_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'instagram', 'tiktok', 'facebook', 'twitter'
    followers INTEGER,
    following INTEGER,
    posts INTEGER,
    engagement_rate FLOAT,
    avg_likes INTEGER,
    avg_comments INTEGER,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform, date)
);

CREATE INDEX idx_social_media_metrics_user_id ON social_media_metrics(user_id);
CREATE INDEX idx_social_media_metrics_platform ON social_media_metrics(platform);
CREATE INDEX idx_social_media_metrics_date ON social_media_metrics(date);
```

**playlist_appearances** (already exists, extend)
```sql
ALTER TABLE playlist_appearances ADD COLUMN IF NOT EXISTS source VARCHAR(50);
-- Values: 'spotify_api', 'submithub', 'manual'

ALTER TABLE playlist_appearances ADD COLUMN IF NOT EXISTS campaign_cost DECIMAL(10, 2);
-- Cost of SubmitHub campaign (if applicable)
```

---

## Configuration

### Environment Variables

```bash
# .env

# Instagram
INSTAGRAM_CLIENT_ID=your_client_id
INSTAGRAM_CLIENT_SECRET=your_client_secret

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# Twitter
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# TikTok (if approved)
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
```

---

## Testing Plan

### CSV Import
- [ ] Test with DistroKid CSV
- [ ] Test with CD Baby CSV
- [ ] Test with TuneCore CSV
- [ ] Test with custom CSV
- [ ] Test with malformed CSV (error handling)

### Instagram
- [ ] Test OAuth flow
- [ ] Test profile data fetch
- [ ] Test media fetch
- [ ] Test token refresh
- [ ] Test error handling (invalid token, rate limit)

### TikTok
- [ ] Test profile scraping
- [ ] Test video stats scraping
- [ ] Test rate limiting
- [ ] Test error handling (profile not found, scraping blocked)

### SubmitHub
- [ ] Test CSV import
- [ ] Test ROI calculation
- [ ] Test playlist appearance creation

---

## Success Criteria

### Functionality
- [ ] Artists can import data from 3+ sources (CSV, Instagram, TikTok)
- [ ] Data syncs daily (automated)
- [ ] Multi-platform dashboard shows unified view
- [ ] ROI calculated for marketing campaigns

### Performance
- [ ] CSV import: <30 seconds for 1,000 rows
- [ ] API sync: <10 seconds per platform
- [ ] Scraping: <60 seconds per profile

### Reliability
- [ ] 95%+ uptime for integrations
- [ ] Graceful error handling (API failures, rate limits)
- [ ] Automatic retry with exponential backoff

### User Experience
- [ ] Clear instructions for each integration
- [ ] Visual feedback during import/sync
- [ ] Error messages are actionable
- [ ] Data displayed beautifully in dashboard

---

## Next Steps

1. **Week 1:** Implement CSV universal import
2. **Week 2-3:** Implement Instagram Basic Display API
3. **Week 3-4:** Implement TikTok scraper
4. **Week 5:** Implement SubmitHub CSV import
5. **Week 6-7:** Implement Facebook/Meta API (if time permits)
6. **Week 8:** Implement Twitter API (if time permits)

**Priority:** Focus on P0 and P1 integrations first. P2 and P3 can wait until after Product Hunt launch.

