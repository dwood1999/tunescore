# ✅ music.quilty.app - Fully Configured (Pattern: dwood.quilty.app)

## 🎯 Status: OPERATIONAL

### ✅ What's Working:

1. **API Endpoints**: All working at `https://music.quilty.app/api/v1/*`
2. **Health Check**: ✅ `https://music.quilty.app/api/v1/health`
3. **API Docs**: ✅ `https://music.quilty.app/api/v1/docs`
4. **Root Redirect**: Configured to redirect `/` → `/api/v1/docs`

---

## 📋 Configuration Pattern (Matches dwood.quilty.app)

### Nginx Config Location
**File**: `/var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf`

**Pattern**: Same structure as `dwood.quilty.app`:
- Root location handles redirects
- `/api/` location proxies to backend
- Uses same proxy header patterns
- Extended timeouts for large uploads

### Current Configuration:

```nginx
# Root redirects to API docs
location / {
	return 301 /api/v1/docs;
}

# API endpoints proxy to backend (port 8001)
location /api/ {
	proxy_pass http://127.0.0.1:8001;
	proxy_set_header Host 127.0.0.1:8001;
	proxy_set_header X-Real-IP $remote_addr;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header X-Forwarded-Proto $scheme;
	proxy_set_header X-Forwarded-Host $host;
	
	proxy_http_version 1.1;
	proxy_connect_timeout 300s;
	proxy_send_timeout 300s;
	proxy_read_timeout 300s;
	client_max_body_size 500M;
	proxy_buffering off;
	proxy_request_buffering off;
}
```

---

## 🔄 Comparison with dwood.quilty.app

| Aspect | dwood.quilty.app | music.quilty.app |
|--------|------------------|------------------|
| **Root** | Proxies to port 5127 (frontend) | Redirects to `/api/v1/docs` |
| **API** | Proxies to port 8027 | Proxies to port 8001 |
| **Config Location** | `/var/www/vhosts/system/dwood.quilty.app/conf/vhost_nginx.conf` | `/var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf` |
| **Pattern** | Frontend + Backend | API-only (no frontend yet) |
| **Max Body Size** | 100M | 500M (for audio files) |
| **Timeouts** | 180s | 300s (for audio processing) |

---

## ✅ Verified Working Endpoints

```bash
# Health check
curl https://music.quilty.app/api/v1/health
# Returns: {"status":"healthy","service":"tunescore-api","timestamp":"..."}

# API docs
curl -I https://music.quilty.app/api/v1/docs
# Returns: HTTP/1.1 200 OK

# Root redirect
curl -I https://music.quilty.app/
# Returns: HTTP/1.1 301 Moved Permanently
# Location: https://music.quilty.app/api/v1/docs
```

---

## 🔧 Management

### View Config
```bash
sudo cat /var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf
```

### Edit Config
```bash
sudo nano /var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf
```

### Test & Reload
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Check Backend
```bash
sudo systemctl status tunescore-backend
curl http://localhost:8001/api/v1/health
```

---

## 📝 Notes

1. **Root Redirect**: Browser may cache the old Plesk page. Hard refresh (Ctrl+F5) or clear cache.
2. **API Endpoints**: All working correctly via curl and direct access.
3. **Pattern Match**: Configuration follows the exact same pattern as dwood.quilty.app.
4. **Future**: When frontend is added, root can proxy to frontend like dwood.quilty.app does.

---

## 🚀 Quick Test

```bash
# Test all endpoints
curl https://music.quilty.app/api/v1/health
curl https://music.quilty.app/api/v1/docs
curl -I https://music.quilty.app/
```

**All endpoints verified working!** ✅

---

*Configuration completed: October 31, 2025*
*Pattern: dwood.quilty.app*
*Status: OPERATIONAL*

