# TuneScore - Development Mode

This project is currently running in **development mode** (no systemd services).

## Quick Start

### Start Backend

```bash
cd /home/dwood/tunescore
./scripts/dev_start_backend.sh
```

Backend will run on: **http://127.0.0.1:8001**
- API Docs: http://127.0.0.1:8001/api/v1/docs
- Health: http://127.0.0.1:8001/api/v1/health

### Start Frontend

Open a new terminal:

```bash
cd /home/dwood/tunescore
./scripts/dev_start_frontend.sh
```

Frontend will run on: **http://localhost:5128**

## Access Points

### Direct Access (Development)
- **Frontend**: http://localhost:5128
- **Backend API**: http://127.0.0.1:8001
- **API Docs**: http://127.0.0.1:8001/api/v1/docs

### Via Nginx (Production-like)
Once both services are running, you can access via:
- **Frontend**: https://music.quilty.app
- **API**: https://music.quilty.app/api/v1/*
- **API Docs**: https://music.quilty.app/api/v1/docs

> **Note**: Nginx is still configured to proxy to these ports, so the site will work at `music.quilty.app` when both services are running.

## Development Features

### Backend
- ✅ Auto-reload on file changes
- ✅ Detailed error messages
- ✅ Debug mode enabled
- ✅ Logging to console

### Frontend
- ✅ Hot Module Replacement (HMR)
- ✅ Fast refresh on file changes
- ✅ Source maps for debugging
- ✅ TypeScript checking

## Running Both Services

### Option 1: Two Terminals
1. Terminal 1: `./scripts/dev_start_backend.sh`
2. Terminal 2: `./scripts/dev_start_frontend.sh`

### Option 2: Background Processes
```bash
# Start backend in background
./scripts/dev_start_backend.sh > logs/backend_dev.log 2>&1 &

# Start frontend in background
./scripts/dev_start_frontend.sh > logs/frontend_dev.log 2>&1 &

# View logs
tail -f logs/backend_dev.log
tail -f logs/frontend_dev.log
```

### Option 3: Using `tmux` or `screen`
```bash
# Create tmux session with backend and frontend
tmux new-session -d -s tunescore
tmux send-keys -t tunescore 'cd /home/dwood/tunescore && ./scripts/dev_start_backend.sh' Enter
tmux new-window -t tunescore
tmux send-keys -t tunescore 'cd /home/dwood/tunescore && ./scripts/dev_start_frontend.sh' Enter
tmux attach -t tunescore
```

## Stopping Services

Press `Ctrl+C` in each terminal, or:

```bash
# Kill backend
pkill -f "uvicorn.*8001"

# Kill frontend
pkill -f "vite.*5128"
```

## Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
ss -tlnp | grep 8001  # Backend
ss -tlnp | grep 5128  # Frontend

# Kill the process
pkill -f "uvicorn.*8001"
pkill -f "vite.*5128"
```

### Backend Won't Start
```bash
# Check Poetry environment
cd backend
poetry env info

# Reinstall dependencies if needed
poetry install

# Check database connection
poetry run python -c "from app.core.database import settings; print(settings.database_url)"
```

### Frontend Won't Start
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf .svelte-kit build
npm run build
```

## Environment Variables

Make sure `.env` file is configured:
```bash
cd /home/dwood/tunescore
cp env.template .env
# Edit .env with your settings
```

## Next Steps

1. ✅ Start backend: `./scripts/dev_start_backend.sh`
2. ✅ Start frontend: `./scripts/dev_start_frontend.sh`
3. ✅ Access: https://music.quilty.app (if Nginx is running)
4. ✅ Or access directly: http://localhost:5128

---

**Note**: Systemd services have been disabled. To re-enable them later:
```bash
sudo systemctl enable tunescore-backend tunescore-frontend
sudo systemctl start tunescore-backend tunescore-frontend
```

