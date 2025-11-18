# Plesk Configuration for music.quilty.app

## Step 1: Add Nginx Directives in Plesk

1. Log into Plesk: `https://your-server:8443`
2. Go to: **Websites & Domains**
3. Find **music.quilty.app**
4. Click **Apache & Nginx Settings**
5. Scroll down to **Additional nginx directives**
6. Paste this configuration:

```nginx
# TuneScore API Proxy Configuration for music.quilty.app
client_max_body_size 500M;
client_body_timeout 600s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
send_timeout 300s;

# Proxy all /api/ requests to TuneScore backend
location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Request-ID $request_id;
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

# Health check endpoint
location /api/v1/health {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    access_log off;
}
```

7. Click **OK** to apply

## Step 2: Set Up Systemd Service

Run these commands via SSH:

```bash
# Create systemd service file
echo 'p3ter[thiel]' | sudo -S tee /etc/systemd/system/tunescore-backend.service > /dev/null << 'EOF'
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
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo 'p3ter[thiel]' | sudo -S systemctl daemon-reload

# Enable service
echo 'p3ter[thiel]' | sudo -S systemctl enable tunescore-backend

# Start service
echo 'p3ter[thiel]' | sudo -S systemctl start tunescore-backend

# Check status
echo 'p3ter[thiel]' | sudo -S systemctl status tunescore-backend
```

## Step 3: Update CORS Settings

Update the `.env` file to allow music.quilty.app:

```bash
cd /home/dwood/tunescore
nano .env
```

Add/update these lines:
```
BACKEND_CORS_ORIGINS=https://music.quilty.app,http://music.quilty.app,http://localhost:5128
FRONTEND_URL=https://music.quilty.app
```

Then restart the backend:
```bash
echo 'p3ter[thiel]' | sudo -S systemctl restart tunescore-backend
```

## Step 4: Enable SSL in Plesk

1. In Plesk, go to **Websites & Domains**
2. Click **music.quilty.app**
3. Click **SSL/TLS Certificates**
4. Click **Get it free** (Let's Encrypt)
5. Enter your email
6. Check **Secure the domain and its www subdomain**
7. Click **Get it free**

Then enable HTTPS redirect:
1. Go to **Hosting Settings**
2. Check **Permanent SEO-safe 301 redirect from HTTP to HTTPS**
3. Click **OK**

## Step 5: Test Everything

```bash
# Test backend directly
curl http://localhost:8001/api/v1/health

# Test through domain
curl https://music.quilty.app/api/v1/health

# Test API docs
# Open in browser: https://music.quilty.app/api/v1/docs
```

## Troubleshooting

If you get 502 Bad Gateway:
```bash
# Check if backend is running
echo 'p3ter[thiel]' | sudo -S systemctl status tunescore-backend

# Check logs
echo 'p3ter[thiel]' | sudo -S journalctl -u tunescore-backend -n 50

# Restart backend
echo 'p3ter[thiel]' | sudo -S systemctl restart tunescore-backend
```

If you get permission errors:
```bash
# Check file permissions
ls -la /home/dwood/tunescore/

# Fix if needed
echo 'p3ter[thiel]' | sudo -S chown -R dwood:dwood /home/dwood/tunescore/
```

