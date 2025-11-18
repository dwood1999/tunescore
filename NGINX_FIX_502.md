# Fix 502 Bad Gateway Error

## Issue
Getting `502 Bad Gateway` when accessing `https://music.quilty.app/tracks/17`

## Root Cause
Nginx reverse proxy is not correctly configured to proxy to the frontend preview server.

## Current Status

### ✅ Working:
- Preview server running on port **5128** (PID: 3919512)
- Server accessible at `http://localhost:5128` ✅
- Server listening on `0.0.0.0:5128` (all interfaces) ✅
- Backend running on port **8001** ✅
- Vite config updated to proxy `/api` to port **8001** ✅

### ⚠️ Needs Fix:
- Nginx configuration needs to proxy to `http://127.0.0.1:5128`

## Solution

### Step 1: Check Nginx Configuration

```bash
# View the nginx config (requires sudo)
sudo cat /etc/nginx/plesk.conf.d/vhosts/music.quilty.app.conf
```

### Step 2: Update Proxy Configuration

The nginx config should have a `proxy_pass` directive pointing to the frontend server:

```nginx
location / {
    proxy_pass http://127.0.0.1:5128;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

### Step 3: Reload Nginx

After updating the config:

```bash
# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

## Alternative: Check Current Proxy Target

If nginx is already configured but pointing to wrong port:

```bash
# Check what port nginx is trying to proxy to
sudo grep -A 5 "proxy_pass" /etc/nginx/plesk.conf.d/vhosts/music.quilty.app.conf
```

If it's pointing to a different port (e.g., 3000, 5173, etc.), update it to `http://127.0.0.1:5128`.

## Verify Fix

After reloading nginx:

```bash
# Test locally
curl -I http://localhost:5128/tracks/17

# Test via nginx (should work after fix)
curl -I https://music.quilty.app/tracks/17
```

## Date: November 17, 2025
## Status: ⚠️ Requires Nginx Configuration Update

