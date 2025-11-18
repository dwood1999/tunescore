# Frontend Setup for TuneScore

## ✅ Completed Steps

1. ✅ SvelteKit frontend scaffolded with TypeScript and Tailwind
2. ✅ Basic pages created (home, upload, dashboard, track details)
3. ✅ API client configured
4. ✅ Frontend built successfully
5. ✅ Systemd service file created

## 📋 Remaining Steps

### 1. Install and Start Frontend Service

```bash
cd /home/dwood/tunescore

# Install the systemd service
sudo cp /tmp/tunescore-frontend.service /etc/systemd/system/tunescore-frontend.service
sudo systemctl daemon-reload
sudo systemctl enable tunescore-frontend
sudo systemctl start tunescore-frontend
sudo systemctl status tunescore-frontend
```

### 2. Update Nginx Configuration

Edit the Plesk Nginx config file:

```bash
sudo nano /var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf
```

**Find this section** (currently redirects root to API docs):
```nginx
location / {
    rewrite ^/$ https://music.quilty.app/api/v1/docs permanent;
}
```

**Replace it with** (proxy to frontend):
```nginx
# Frontend (SvelteKit) - proxies to port 5128
location / {
    proxy_pass http://127.0.0.1:5128;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    
    # WebSocket support for HMR
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_cache_bypass $http_upgrade;
}
```

**Keep the `/api/` location block as-is** - it should already proxy to the backend:
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host music.quilty.app;
    # ... rest of config
}
```

### 3. Reload Nginx

```bash
sudo systemctl reload nginx
```

### 4. Verify

- Frontend: https://music.quilty.app (should show the TuneScore homepage)
- API: https://music.quilty.app/api/v1/health (should still work)
- API Docs: https://music.quilty.app/api/v1/docs (should still work)

## 🔧 Development Mode

To run the frontend in development mode (with hot reload):

```bash
cd /home/dwood/tunescore/frontend
npm run dev
```

This will start on `http://localhost:5128` (accessible via Nginx proxy when configured).

## 📝 Architecture

- **Frontend**: SvelteKit running on port 5128
- **Backend**: FastAPI running on port 8001
- **Nginx**: Proxies `/api/*` → backend, `/` → frontend
- **Static Files**: Served by SvelteKit Node adapter

## 🐛 Troubleshooting

### Frontend not loading
- Check service status: `sudo systemctl status tunescore-frontend`
- Check logs: `sudo journalctl -u tunescore-frontend -f`
- Verify port 5128 is listening: `ss -tlnp | grep 5128`

### API calls failing
- Ensure `/api/` location in Nginx proxies to port 8001
- Check backend is running: `sudo systemctl status tunescore-backend`
- Test backend directly: `curl http://127.0.0.1:8001/api/v1/health`

### Build issues
```bash
cd /home/dwood/tunescore/frontend
rm -rf node_modules .svelte-kit build
npm install
npm run build
```

