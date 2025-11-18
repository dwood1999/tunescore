# 🔧 Fix music.quilty.app - Step by Step

## Current Status
✅ Backend running on localhost:8001  
❌ Nginx proxy not configured in Plesk  
❌ API returns 404 at https://music.quilty.app/api/v1/health  

## Solution: Add Nginx Directives in Plesk

### Step 1: Log into Plesk
1. Go to: **https://music.quilty.app:8443**
2. Or find your Plesk URL (usually `https://your-server-ip:8443`)
3. Log in with your credentials

### Step 2: Open Domain Settings
1. In Plesk, go to **Websites & Domains**
2. Find and click on **music.quilty.app**
3. Click **Apache & Nginx Settings** (or **Web Server Settings**)

### Step 3: Add Nginx Directives
1. Scroll down to **Additional nginx directives** section
2. If you see existing directives, add these AFTER them (don't delete existing ones)
3. **Copy and paste this entire block:**

```nginx
# TuneScore API Proxy Configuration
client_max_body_size 500M;
client_body_timeout 600s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;

# Proxy all API requests to backend
location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
    proxy_request_buffering off;
}

# Upload endpoint with extended timeouts
location /api/v1/tracks/upload {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    client_body_timeout 600s;
}

# Health check (no logging)
location /api/v1/health {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    access_log off;
}
```

### Step 4: Apply Changes
1. Click **OK** or **Apply** at the bottom
2. Plesk will test the configuration
3. If there's an error, it will show you - fix any syntax errors
4. If successful, Plesk will reload Nginx automatically

### Step 5: Test
After adding the directives, test:

```bash
# Test health endpoint
curl https://music.quilty.app/api/v1/health

# Expected: {"status":"healthy","service":"tunescore-api","timestamp":"..."}
```

Or open in browser:
- **API Docs**: https://music.quilty.app/api/v1/docs
- **Health Check**: https://music.quilty.app/api/v1/health

---

## Alternative: If Nginx Directives Don't Work

### Option 1: Use Plesk "Rewrite Rules"

In Plesk, some versions use "Rewrite Rules" instead. Try:

1. **Websites & Domains** > **music.quilty.app** > **Apache & Nginx Settings**
2. Look for **Rewrite Rules** or **Additional directives for HTTP**
3. Add the proxy configuration there

### Option 2: Create .htaccess (for Apache)

If Plesk is using Apache instead of Nginx:

```apache
<IfModule mod_proxy.c>
    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:8001/api/
    ProxyPassReverse /api/ http://127.0.0.1:8001/api/
</IfModule>
```

### Option 3: Check Plesk Version

Some Plesk versions put Nginx settings in different places:
- **Obsidian (18+)**: Apache & Nginx Settings > Additional nginx directives
- **Onyx (17)**: Web Server Settings > Additional nginx directives
- **Earlier**: May be under "Additional directives for nginx"

---

## Troubleshooting

### Still Getting 404?

1. **Check backend is running:**
   ```bash
   curl http://localhost:8001/api/v1/health
   sudo systemctl status tunescore-backend
   ```

2. **Check Nginx configuration:**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

3. **Check Plesk error logs:**
   - In Plesk: **Logs** > **Error Log**
   - Or via SSH: `sudo tail -f /var/log/nginx/error.log`

4. **Restart services:**
   ```bash
   sudo systemctl restart nginx
   sudo systemctl restart tunescore-backend
   ```

### 502 Bad Gateway?

This means Nginx can see backend but can't connect:

1. **Check backend is listening on 127.0.0.1:8001:**
   ```bash
   sudo netstat -tlnp | grep 8001
   ```

2. **Backend should show:**
   ```
   tcp        0      0 127.0.0.1:8001          0.0.0.0:*               LISTEN      ...
   ```

3. **If it shows 0.0.0.0:8001, that's okay too**

### 413 Request Entity Too Large?

Increase `client_max_body_size` in Nginx directives:
```nginx
client_max_body_size 1000M;  # Increase to 1GB
```

### Configuration Test Failed?

1. Check for syntax errors (missing semicolons, braces, etc.)
2. Remove all directives temporarily
3. Add them back one section at a time
4. Test after each addition

---

## Quick Test Script

Run this after adding directives:

```bash
#!/bin/bash
echo "Testing TuneScore API on music.quilty.app..."
echo ""
echo "1. Testing health endpoint:"
curl -s https://music.quilty.app/api/v1/health | python3 -m json.tool
echo ""
echo "2. Testing API docs:"
curl -s -I https://music.quilty.app/api/v1/docs | head -1
echo ""
echo "3. If both work, you're good to go! 🎉"
```

---

## What Should Work After This

✅ https://music.quilty.app/api/v1/health  
✅ https://music.quilty.app/api/v1/docs  
✅ https://music.quilty.app/api/v1/openapi.json  
✅ All API endpoints under /api/v1/*  

---

**Need help?** Check the logs:
- Backend: `sudo journalctl -u tunescore-backend -n 50`
- Nginx: `sudo tail -f /var/log/nginx/error.log`

