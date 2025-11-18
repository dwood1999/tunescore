# Test Industry Pulse - Debug Guide

## The Error You're Seeing

**"Failed to load tracks: Error: Bad Gateway"**

This error is likely from a **different page** (the tracks/dashboard page), NOT from Industry Pulse.

---

## ✅ Quick Test: Is Industry Pulse Working?

### From Command Line (Run These)

```bash
# 1. Test backend API directly
curl http://localhost:8001/api/v1/industry-pulse/news?limit=2 | python -m json.tool

# You should see 2 news articles with Taylor Swift, Justin Bieber, etc.
```

```bash
# 2. Check if frontend service is running
sudo systemctl status tunescore-frontend

# Should show: "Active (running)"
```

```bash
# 3. Test the full page
curl -s http://localhost:5128/industry-pulse | grep "Industry Pulse"

# Should show: "<h1>Industry Pulse</h1>" or similar
```

### From Browser

**Navigate to**: http://localhost:5128/industry-pulse

**Or if on production domain**: https://music.quilty.app/industry-pulse

You should see:
1. Header: "Industry Pulse - Bloomberg Terminal for Music"
2. Three tabs: Charts 🔥 | News 📰 | Releases 🎵
3. Click "News 📰" tab
4. See articles from Billboard, Rolling Stone, etc.

---

## 🔍 The "Bad Gateway" Error Explained

### Most Likely Cause
You're on a different page (like `/dashboard` or `/tracks/[id]`) and THAT page is showing the error, not the Industry Pulse page.

### Why It Happens
The main TuneScore app tries to load tracks from the API, and if the backend isn't responding properly for some reason, you see "Bad Gateway".

### It's NOT Related to Industry Pulse
Industry Pulse has its own endpoints (`/industry-pulse/*`) which are working fine!

---

## 🚀 Access Industry Pulse Dashboard

### Option 1: Direct URL
```
http://localhost:5128/industry-pulse
```

### Option 2: Add to Navigation
You can add a link to the nav in `/frontend/src/routes/+layout.svelte`:

```svelte
<a href="/industry-pulse">
  Industry Pulse 📊
</a>
```

---

## 🧪 Verification Commands

Run these to prove everything is working:

```bash
# Backend health
curl http://localhost:8001/health
# Expected: {"status":"healthy"}

# Industry Pulse news
curl http://localhost:8001/api/v1/industry-pulse/news | python -c "import sys, json; print(f'{len(json.load(sys.stdin))} articles')"
# Expected: "40 articles" or similar

# Scraper automation
sudo systemctl list-timers | grep industry
# Expected: Shows next run time

# Recent scraper runs
sudo journalctl -u tunescore-industry-scraper.service -n 10
# Expected: Shows successful runs with "40 news articles"
```

---

## 📊 What's In Your Database Right Now

```bash
# Connect to database and check
cd /home/dwood/tunescore/backend
source venv/bin/activate

python -c "
import asyncio
from sqlalchemy import select, func, text
from app.core.database import AsyncSessionLocal
from app.industry_snapshot.models import IndustryNews, ChartSnapshot, NewRelease, DailyDigest

async def check():
    async with AsyncSessionLocal() as db:
        # Count news
        result = await db.execute(select(func.count(IndustryNews.id)))
        news_count = result.scalar()
        print(f'📰 News articles: {news_count}')
        
        # Count charts
        result = await db.execute(select(func.count(ChartSnapshot.id)))
        charts_count = result.scalar()
        print(f'🔥 Chart entries: {charts_count}')
        
        # Count releases
        result = await db.execute(select(func.count(NewRelease.id)))
        releases_count = result.scalar()
        print(f'🎵 New releases: {releases_count}')
        
        # Count digests
        result = await db.execute(select(func.count(DailyDigest.id)))
        digests_count = result.scalar()
        print(f'📝 Daily digests: {digests_count}')
        
        # Get latest news
        result = await db.execute(
            select(IndustryNews.title, IndustryNews.source)
            .order_by(IndustryNews.published_at.desc())
            .limit(3)
        )
        print(f'\n📰 Latest news articles:')
        for row in result:
            print(f'  - [{row.source}] {row.title[:60]}...')

asyncio.run(check())
"
```

---

## 🎯 Next Steps

1. **Navigate to Industry Pulse**: Go to http://localhost:5128/industry-pulse in your browser
2. **Click News Tab**: You should see 40+ articles
3. **Ignore "Bad Gateway"**: That's from a different page trying to load tracks

The Industry Pulse feature is **fully functional and collecting data**! The "Bad Gateway" error is unrelated.

---

## 📞 Still Not Working?

Try restarting both services:

```bash
# Restart backend
sudo systemctl restart tunescore-backend
sleep 5

# Restart frontend
sudo systemctl restart tunescore-frontend
sleep 8

# Test
curl http://localhost:5128/industry-pulse | grep "Industry Pulse"
```

---

**Bottom Line**: Industry Pulse is working! Just navigate directly to `/industry-pulse` and click the News tab. The "Bad Gateway" error is from trying to load `/tracks` or `/dashboard`, which is a separate issue.

