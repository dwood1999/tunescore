# TuneScore - Development Quick Reference

## 🚀 Start Development Servers

### Backend (Terminal 1)
```bash
./scripts/dev_start_backend.sh
```
Runs on: http://127.0.0.1:8001

### Frontend (Terminal 2)
```bash
./scripts/dev_start_frontend.sh
```
Runs on: http://localhost:5128

## 🛑 Stop All Servers
```bash
./scripts/stop_dev.sh
```

## 🌐 Access

- **Local**: http://localhost:5128
- **Via Nginx**: https://music.quilty.app (when both services running)

## 📝 Notes

- Systemd services are **disabled** (dev mode only)
- Auto-reload enabled for both frontend and backend
- Check `DEV_MODE.md` for detailed instructions

