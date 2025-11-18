# TuneScore Plesk Quick Start

## 🚀 5-Minute Setup

### Step 1: Add Nginx Directives in Plesk

1. Log into Plesk: `https://your-server:8443`
2. Go to: **Websites & Domains** > **Your Domain** > **Apache & Nginx Settings**
3. Scroll to **Additional nginx directives**
4. Paste this:

```nginx
# TuneScore Backend Proxy
client_max_body_size 500M;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;

location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}

location /api/v1/tracks/upload {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
}
```

5. Click **OK**

### Step 2: Start Backend Service

```bash
# SSH into your server
ssh dwood@your-server

# Start backend
cd /home/dwood/tunescore
./scripts/start_backend.sh
```

### Step 3: Enable SSL

1. In Plesk: **Websites & Domains** > **Your Domain** > **SSL/TLS Certificates**
2. Click **Get it free** (Let's Encrypt)
3. Enter email and click **Get it free**
4. Enable HTTPS redirect in **Hosting Settings**

### Step 4: Test

```bash
curl https://yourdomain.com/api/v1/health
```

Open in browser:
```
https://yourdomain.com/api/v1/docs
```

---

## 📋 Common Commands

```bash
# Check backend status
sudo systemctl status tunescore-backend

# View logs
tail -f /home/dwood/tunescore/logs/api_prompts.log

# Restart backend
sudo systemctl restart tunescore-backend

# Backup database
./scripts/backup_db.sh

# Run migrations
./scripts/migrate.sh upgrade
```

---

## 🔧 Troubleshooting

**502 Bad Gateway?**
```bash
# Check if backend is running
curl http://localhost:8001/api/v1/health

# Restart backend
sudo systemctl restart tunescore-backend
```

**Upload fails?**
- Increase `client_max_body_size` in Plesk Nginx directives

**Timeout errors?**
- Increase timeout values in Plesk Nginx directives

---

## 📚 Full Documentation

- **Plesk Setup**: `docs/PLESK_SETUP.md`
- **API Reference**: `docs/API.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Quick Start**: `QUICKSTART.md`

---

## ✅ Setup Checklist

- [ ] Add Nginx directives in Plesk
- [ ] Start backend service
- [ ] Enable SSL certificate
- [ ] Test API endpoint
- [ ] Test file upload
- [ ] Set up automated backups

---

**Need Help?** See `docs/PLESK_SETUP.md` for detailed instructions.

