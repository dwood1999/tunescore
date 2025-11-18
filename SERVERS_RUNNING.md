# ✅ TuneScore Servers Running

## Status: ACTIVE

Both development servers are now running in the background.

### 🟢 Backend
- **Status**: Running
- **URL**: http://127.0.0.1:8002
- **API Docs**: http://127.0.0.1:8002/api/v1/docs
- **Health**: http://127.0.0.1:8002/health
- **Logs**: `logs/backend_dev.log`
- **Process**: Background (auto-reload enabled)

### 🟢 Frontend
- **Status**: Running  
- **URL**: http://localhost:5128
- **Network**: http://74.208.14.103:5128
- **Logs**: `logs/frontend_dev.log`
- **Process**: Background (HMR enabled)

## 🌐 Access Points

### Direct Access
- **Frontend**: http://localhost:5128
- **Backend API**: http://127.0.0.1:8002
- **API Docs**: http://127.0.0.1:8002/api/v1/docs

### Via Nginx (Production-like)
- **Frontend**: https://music.quilty.app
- **API**: https://music.quilty.app/api/v1/*
- **API Docs**: https://music.quilty.app/api/v1/docs

## 📝 Logs

View live logs:
```bash
# Backend logs
tail -f logs/backend_dev.log

# Frontend logs
tail -f logs/frontend_dev.log

# Both logs
tail -f logs/*.log
```

## 🛑 Stop Servers

To stop both servers:
```bash
./scripts/stop_dev.sh
```

Or manually:
```bash
pkill -f "uvicorn.*8001"  # Backend
pkill -f "vite.*5128"     # Frontend
```

## ⚠️ Notes

- Both servers have **auto-reload** enabled - changes will automatically refresh
- Servers are running in **background** - they will continue after you close your terminal
- To see output in real-time, check the log files or run in foreground terminals

## 🔍 Verify Status

Check if servers are running:
```bash
ps aux | grep -E "(uvicorn|vite)" | grep -E "(8001|5128)"
```

Check ports:
```bash
ss -tlnp | grep -E ":(8001|5128)"
```

---

**Servers are ready! Visit https://music.quilty.app to see the frontend! 🎉**

