# Industry Pulse - Quick Start Guide

## 🚀 Getting Started (5 Minutes)

### 1. Verify Installation
```bash
# Check database tables exist
cd /home/dwood/tunescore/backend
source venv/bin/activate
alembic current
# Should show: 46c90ae0ff06 (head) - add_industry_snapshot_tables
```

### 2. Run Manual Scraper Test
```bash
python scripts/run_industry_scraper.py
# Should collect 40+ news articles in ~10 seconds
```

### 3. Test API Endpoints
```bash
# Get news
curl http://localhost:8001/api/v1/industry-pulse/news?limit=3 | jq

# Get digest (may be empty if no AI keys configured in runtime)
curl http://localhost:8001/api/v1/industry-pulse/digest | jq

# Get charts
curl http://localhost:8001/api/v1/industry-pulse/charts | jq
```

### 4. View Frontend
Navigate to: **http://localhost:5128/industry-pulse**

---

## 🔧 Enable Automated Scraping

### Install Systemd Timer
```bash
sudo cp infra/systemd/tunescore-industry-scraper.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tunescore-industry-scraper.timer
sudo systemctl start tunescore-industry-scraper.timer
```

### Check Status
```bash
# Timer status
sudo systemctl status tunescore-industry-scraper.timer

# View recent runs
sudo journalctl -u tunescore-industry-scraper.service -n 50 --no-pager

# Manually trigger
sudo systemctl start tunescore-industry-scraper.service
```

---

## 🐛 Troubleshooting

### No News Articles Collected
**Check**: RSS feed connectivity
```bash
curl -I https://www.musicbusinessworldwide.com/feed/
# Should return 200 OK
```

### AI Digest Not Generating
**Fix**: Ensure AI API keys are set in `/home/dwood/tunescore/backend/.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
```

Then restart backend:
```bash
sudo systemctl restart tunescore-backend
```

### Charts Empty
**Known Issue**: Spotify public charts endpoint changed. Will be fixed in Phase 2.

### Frontend Not Loading
**Check backend is running**:
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy"}
```

---

## 📊 Understanding the Data

### News Categories
- **M&A**: Mergers & acquisitions, catalog sales
- **Signings**: Artist signings, label deals
- **Platform**: Spotify/Apple/TikTok updates
- **Legal**: Copyright, royalty changes
- **Tech**: New tools, AI music
- **Market**: Industry economics

### Impact Scores (0-10)
- **Creator**: Relevance to artists/producers
- **Developer**: Relevance to A&R/scouts
- **Monetizer**: Relevance to execs/investors

### Chart Movement Indicators
- **▲ Green**: Track moving up
- **▼ Red**: Track moving down
- **● Gray**: No movement or new entry

---

## 🎯 Quick Tasks

### Force Immediate Scraper Run
```bash
cd /home/dwood/tunescore/backend && python scripts/run_industry_scraper.py
```

### Check Latest News Count
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM industry_news WHERE created_at > NOW() - INTERVAL '24 hours';"
```

### View Scraper Logs
```bash
tail -f /home/dwood/tunescore/logs/industry_scraper.log
```

### Clear Old Data (30+ days)
```bash
psql $DATABASE_URL -c "DELETE FROM industry_news WHERE created_at < NOW() - INTERVAL '30 days';"
```

---

## 📖 API Examples

### Get Today's Digest
```bash
curl "http://localhost:8001/api/v1/industry-pulse/digest" | jq '.summary_text'
```

### Get News for Creators
```bash
curl "http://localhost:8001/api/v1/industry-pulse/news?user_tier=creator&limit=5" | jq
```

### Get Chart Movers
```bash
curl "http://localhost:8001/api/v1/industry-pulse/charts/movers?platform=spotify" | jq '.risers[0:3]'
```

### Get Notable Releases
```bash
curl "http://localhost:8001/api/v1/industry-pulse/releases?notable_only=true" | jq
```

---

## 🔐 Security Notes

- All API keys stored in `.env` (never committed)
- Cost governors prevent runaway AI costs
- Rate limiting via systemd timer randomization
- No PII logged (structlog guards sensitive data)

---

## 📞 Support

**Documentation**: `/home/dwood/tunescore/INDUSTRY_PULSE_IMPLEMENTATION.md`  
**Logs**: `/home/dwood/tunescore/logs/`  
**Issues**: Check known issues in implementation doc

---

**Status**: Phase 1 MVP Complete ✅  
**Last Updated**: November 2, 2025

