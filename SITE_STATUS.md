# 🎉 TuneScore Site Status

**Last Updated**: November 2, 2025 @ 6:45 PM PST

## ✅ Site is ONLINE and Operational

- **URL**: https://music.quilty.app
- **Status**: HTTP 200 ✅
- **Response Time**: ~0.13s
- **SSL**: Active (Let's Encrypt)

## Service Status

### Backend API
- **Status**: ✅ ACTIVE
- **Service**: `tunescore-backend.service`
- **Port**: 8001 (localhost only)
- **Health**: https://music.quilty.app/api/v1/health
- **API Docs**: https://music.quilty.app/api/v1/docs
- **Auto-restart**: Enabled

### Frontend
- **Status**: ✅ ACTIVE
- **Service**: `tunescore-frontend.service`
- **Port**: 5128 (all interfaces)
- **Technology**: SvelteKit + Vite
- **Auto-restart**: Enabled

## What Was Fixed (Nov 2, 2025)

### Problem
- Site was returning 502 Bad Gateway errors
- Vite preview server (port 5128) had stopped running
- Only backend was running, causing nginx proxy failures

### Solution
1. ✅ Restarted backend service (tunescore-backend)
2. ✅ Restarted frontend Vite preview server
3. ✅ Created systemd service for frontend auto-recovery
4. ✅ Updated package.json preview script with correct flags
5. ✅ Verified nginx proxy configuration

## Quick Commands

### Check Service Status
```bash
sudo systemctl status tunescore-backend tunescore-frontend
```

### Restart Services
```bash
# Restart both services
sudo systemctl restart tunescore-backend tunescore-frontend

# Or individually
sudo systemctl restart tunescore-backend
sudo systemctl restart tunescore-frontend
```

### View Logs
```bash
# Backend logs
sudo journalctl -u tunescore-backend -f

# Frontend logs
sudo journalctl -u tunescore-frontend -f
tail -f /home/dwood/tunescore/logs/frontend.log

# Application logs
tail -f /home/dwood/tunescore/logs/*.log
```

### Quick Health Check
```bash
# Test frontend
curl -I https://music.quilty.app/

# Test API
curl https://music.quilty.app/api/v1/health

# Test track listing
curl https://music.quilty.app/api/v1/tracks/
```

## Systemd Services

Both services are configured to:
- ✅ Start automatically on boot
- ✅ Restart automatically if they crash
- ✅ Wait 10 seconds between restart attempts
- ✅ Log to systemd journal + application logs

## Architecture

```
Internet → Nginx (Plesk) → Port 5128 (Frontend - SvelteKit)
                         → Port 8001 (Backend - FastAPI)
```

### Nginx Configuration
- **Config File**: `/var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf`
- **Proxy Rules**:
  - `/` → http://127.0.0.1:5128 (Frontend)
  - `/api/` → http://127.0.0.1:8001 (Backend API)
- **Timeouts**: 300s for long-running audio processing
- **Max Upload**: 500MB for audio files

## Troubleshooting

### If site is down (502 Error)
```bash
# Check which service is down
sudo systemctl status tunescore-backend tunescore-frontend

# Restart both
sudo systemctl restart tunescore-backend tunescore-frontend

# Check logs for errors
sudo journalctl -u tunescore-backend -n 50
sudo journalctl -u tunescore-frontend -n 50
```

### If API is slow
```bash
# Check backend status
curl http://127.0.0.1:8001/api/v1/health

# Check database connection
sudo systemctl status postgresql

# Restart backend
sudo systemctl restart tunescore-backend
```

### If frontend assets won't load
```bash
# Rebuild frontend
cd /home/dwood/tunescore/frontend
npm run build

# Restart frontend service
sudo systemctl restart tunescore-frontend
```

## Monitoring

Current data:
- **13 tracks** in database
- **API**: Healthy
- **Database**: PostgreSQL (active)
- **Services**: Both running under systemd

---

**Need to update this document?**
```bash
nano /home/dwood/tunescore/SITE_STATUS.md
```

