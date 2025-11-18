# TuneScore Plesk Setup Guide

This guide covers setting up TuneScore on a Plesk-managed server.

## Prerequisites

- Plesk Obsidian or later
- Domain configured in Plesk
- SSH access to server
- TuneScore backend installed at `/home/dwood/tunescore`

---

## Step 1: Configure Nginx in Plesk

### 1.1 Log into Plesk Panel

Navigate to: `https://your-server:8443`

### 1.2 Open Domain Settings

1. Go to **Websites & Domains**
2. Click on your domain (e.g., `tunescore.yourdomain.com`)
3. Click **Apache & Nginx Settings**

### 1.3 Add Nginx Directives

Scroll down to **Additional nginx directives** and paste this configuration:

```nginx
# TuneScore Backend Proxy Configuration

# Allow large file uploads (500MB for audio files)
client_max_body_size 500M;

# Extended timeouts for audio processing
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;

# Proxy all /api/ requests to FastAPI backend
location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}

# Upload endpoints - extra long timeouts
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
}

# Health checks - no logging
location /api/v1/health {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    access_log off;
}
```

### 1.4 Apply Changes

Click **OK** or **Apply** at the bottom of the page.

Plesk will automatically:
- Validate the Nginx configuration
- Reload Nginx if valid
- Show an error if there's a syntax problem

---

## Step 2: Set Up Systemd Service

### 2.1 Create Service File

```bash
sudo nano /etc/systemd/system/tunescore-backend.service
```

Paste this content (adjust paths if needed):

```ini
[Unit]
Description=TuneScore Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=dwood
Group=dwood
WorkingDirectory=/home/dwood/tunescore/backend
Environment="PATH=/home/dwood/.cache/pypoetry/virtualenvs/tunescore-backend-0udhgdCI-py3.12/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/dwood/.cache/pypoetry/virtualenvs/tunescore-backend-0udhgdCI-py3.12/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 2.2 Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tunescore-backend

# Start the service
sudo systemctl start tunescore-backend

# Check status
sudo systemctl status tunescore-backend
```

---

## Step 3: Configure SSL (Let's Encrypt)

### 3.1 Enable SSL in Plesk

1. In Plesk, go to **Websites & Domains**
2. Click on your domain
3. Click **SSL/TLS Certificates**
4. Click **Install** or **Get it free** (for Let's Encrypt)
5. Select **Let's Encrypt**
6. Check **Secure the domain and its www subdomain**
7. Enter your email address
8. Click **Get it free** or **Install**

### 3.2 Enable HTTPS Redirect

1. Go back to **Websites & Domains**
2. Click **Hosting Settings**
3. Check **Permanent SEO-safe 301 redirect from HTTP to HTTPS**
4. Click **OK**

---

## Step 4: Configure Firewall (if needed)

If you have a firewall enabled, make sure ports are open:

```bash
# For UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# For firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## Step 5: Test the Setup

### 5.1 Test Backend Directly

```bash
curl http://localhost:8001/api/v1/health
```

Expected output:
```json
{"status":"healthy","service":"tunescore-api","timestamp":"..."}
```

### 5.2 Test Through Nginx

```bash
curl https://tunescore.yourdomain.com/api/v1/health
```

### 5.3 Test API Documentation

Open in browser:
```
https://tunescore.yourdomain.com/api/v1/docs
```

### 5.4 Test File Upload

```bash
curl -X POST "https://tunescore.yourdomain.com/api/v1/tracks/upload" \
  -F 'track_data={"title":"Test Song","artist_name":"Test Artist"}' \
  -F "audio_file=@test.mp3"
```

---

## Step 6: Set Up Automated Backups

### 6.1 Create Backup Service

```bash
sudo cp /home/dwood/tunescore/infra/systemd/tunescore-backup.service /etc/systemd/system/
sudo cp /home/dwood/tunescore/infra/systemd/tunescore-backup.timer /etc/systemd/system/
```

### 6.2 Enable Backup Timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable tunescore-backup.timer
sudo systemctl start tunescore-backup.timer

# Check timer status
sudo systemctl list-timers tunescore-backup.timer
```

---

## Troubleshooting

### Backend Not Starting

```bash
# Check service status
sudo systemctl status tunescore-backend

# View logs
sudo journalctl -u tunescore-backend -n 50

# Check if port 8001 is in use
sudo netstat -tlnp | grep 8001
```

### 502 Bad Gateway

This means Nginx can't connect to the backend.

```bash
# Check if backend is running
curl http://localhost:8001/api/v1/health

# Restart backend
sudo systemctl restart tunescore-backend

# Check Plesk error logs
sudo tail -f /var/log/nginx/error.log
```

### 413 Request Entity Too Large

Increase `client_max_body_size` in Plesk Nginx directives:

```nginx
client_max_body_size 1000M;  # Increase to 1GB
```

### 504 Gateway Timeout

Increase timeout values in Plesk Nginx directives:

```nginx
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;
```

### SSL Certificate Issues

In Plesk:
1. Go to **SSL/TLS Certificates**
2. Click **Reissue Certificate**
3. Or use **Renew** if certificate is expiring

### Nginx Configuration Error

If Plesk shows "Nginx configuration test failed":

1. Check for syntax errors in your directives
2. Remove the directives temporarily
3. Click **OK** to apply
4. Add directives back one section at a time
5. Test after each addition

---

## Advanced Configuration

### Enable Rate Limiting

Add to **Additional nginx directives** (at the top):

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=300r/m;
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;

# Then in location blocks:
location /api/ {
    limit_req zone=api_limit burst=50 nodelay;
    # ... rest of proxy config
}

location /api/v1/tracks/upload {
    limit_req zone=upload_limit burst=2 nodelay;
    # ... rest of proxy config
}
```

### Enable Gzip Compression

Plesk usually has this enabled by default. To verify, check:

**Tools & Settings > Apache & Nginx Settings > Nginx Settings**

Make sure these are enabled:
- Gzip compression
- Gzip compression level: 6

### Custom Error Pages

In Plesk:
1. Go to **Websites & Domains**
2. Click your domain
3. Click **Custom Error Documents**
4. Customize 502, 503, 504 pages

---

## Monitoring

### View Logs

```bash
# Backend logs
tail -f /home/dwood/tunescore/logs/api_prompts.log

# Systemd logs
sudo journalctl -u tunescore-backend -f

# Nginx access logs (Plesk)
sudo tail -f /var/log/nginx/access_log

# Nginx error logs (Plesk)
sudo tail -f /var/log/nginx/error.log
```

### Check Service Status

```bash
# Backend service
sudo systemctl status tunescore-backend

# Backup timer
sudo systemctl status tunescore-backup.timer
```

### Monitor Resource Usage

```bash
# CPU and memory
top

# Disk space
df -h

# Database size
psql -U dwood tunescore -c "SELECT pg_size_pretty(pg_database_size('tunescore'));"
```

---

## Maintenance

### Update Application

```bash
cd /home/dwood/tunescore
git pull
cd backend
poetry install --no-dev
poetry run alembic upgrade head
sudo systemctl restart tunescore-backend
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart tunescore-backend

# Restart Nginx (through Plesk)
# Or via command line:
sudo systemctl restart nginx
```

### Manual Backup

```bash
/home/dwood/tunescore/scripts/backup_db.sh
```

---

## Plesk-Specific Tips

### 1. Use Plesk File Manager

For quick file edits:
- Go to **Files** in Plesk
- Navigate to `/home/dwood/tunescore`
- Edit configuration files directly

### 2. Use Plesk Scheduler

Instead of systemd timers, you can use Plesk's scheduler:
1. Go to **Websites & Domains**
2. Click **Scheduled Tasks**
3. Add task:
   - Command: `/home/dwood/tunescore/scripts/backup_db.sh`
   - Schedule: Daily at 2:00 AM

### 3. Monitor in Plesk

- **Statistics** - View traffic and bandwidth
- **Logs** - View access and error logs
- **Resource Usage** - Monitor CPU/RAM/Disk

### 4. Security in Plesk

- **Security Advisor** - Check security recommendations
- **Firewall** - Configure ModSecurity rules
- **Fail2Ban** - Enable automatic IP blocking

---

## Complete Setup Checklist

- [ ] Add Nginx directives in Plesk
- [ ] Create and enable systemd service
- [ ] Test backend is accessible
- [ ] Configure SSL certificate
- [ ] Enable HTTPS redirect
- [ ] Test API endpoints through domain
- [ ] Set up automated backups
- [ ] Configure monitoring
- [ ] Test file uploads
- [ ] Document any custom settings

---

## Quick Reference

**Plesk Panel**: `https://your-server:8443`

**Nginx Directives**: Websites & Domains > Domain > Apache & Nginx Settings

**SSL Settings**: Websites & Domains > Domain > SSL/TLS Certificates

**Logs**: Websites & Domains > Domain > Logs

**File Manager**: Files

**Backend Service**: `sudo systemctl status tunescore-backend`

**Backend Logs**: `tail -f /home/dwood/tunescore/logs/api_prompts.log`

**API Docs**: `https://yourdomain.com/api/v1/docs`

---

*Last Updated: October 31, 2025*

