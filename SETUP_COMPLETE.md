# ✅ TuneScore Setup Complete for music.quilty.app

## 🎉 What's Been Done

### ✅ Backend Service
- **Status**: Running on port 8001
- **Service**: tunescore-backend.service (enabled, will start on boot)
- **Health Check**: http://localhost:8001/api/v1/health ✓

### ✅ Automated Backups
- **Service**: tunescore-backup.timer (enabled)
- **Schedule**: Daily at 2:00 AM
- **Retention**: 7 daily, 4 weekly, 12 monthly backups
- **Location**: /home/dwood/tunescore/backups/

### ✅ Files Created
- Systemd service: `/etc/systemd/system/tunescore-backend.service`
- Backup service: `/etc/systemd/system/tunescore-backup.service`
- Backup timer: `/etc/systemd/system/tunescore-backup.timer`

---

## 🔧 Final Step: Configure Plesk Nginx

### Add These Directives in Plesk:

1. Log into Plesk
2. Go to: **Websites & Domains** > **music.quilty.app** > **Apache & Nginx Settings**
3. Scroll to: **Additional nginx directives**
4. Paste this:

```nginx
client_max_body_size 500M;
client_body_timeout 600s;
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

location /api/v1/health {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    access_log off;
}
```

5. Click **OK**

---

## 🧪 Test the Setup

After adding Nginx directives in Plesk:

```bash
# Test through domain
curl https://music.quilty.app/api/v1/health

# Expected output:
# {"status":"healthy","service":"tunescore-api","timestamp":"..."}
```

### Open API Documentation
https://music.quilty.app/api/v1/docs

---

## 📊 Service Management

### Check Status
```bash
sudo systemctl status tunescore-backend
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u tunescore-backend -f

# Application logs
tail -f /home/dwood/tunescore/logs/api_prompts.log
```

### Restart Service
```bash
sudo systemctl restart tunescore-backend
```

### Stop Service
```bash
sudo systemctl stop tunescore-backend
```

---

## 💾 Backup Management

### Check Backup Timer
```bash
sudo systemctl list-timers tunescore-backup.timer
```

### Run Manual Backup
```bash
/home/dwood/tunescore/scripts/backup_db.sh
```

### List Backups
```bash
ls -lh /home/dwood/tunescore/backups/
```

### Restore from Backup
```bash
/home/dwood/tunescore/scripts/restore_db.sh /home/dwood/tunescore/backups/tunescore_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 🔒 SSL Configuration (Optional)

If not already done in Plesk:

1. Go to: **Websites & Domains** > **music.quilty.app** > **SSL/TLS Certificates**
2. Click **Get it free** (Let's Encrypt)
3. Enter email and click **Get it free**
4. Enable HTTPS redirect in **Hosting Settings**

---

## 📝 Quick Reference

**Domain**: music.quilty.app  
**Backend Port**: 8001 (localhost only)  
**API Base**: https://music.quilty.app/api/v1  
**API Docs**: https://music.quilty.app/api/v1/docs  
**Health Check**: https://music.quilty.app/api/v1/health  

**Service**: tunescore-backend.service  
**Logs**: /home/dwood/tunescore/logs/  
**Backups**: /home/dwood/tunescore/backups/  

---

## ✅ Setup Checklist

- [x] Backend service installed and running
- [x] Service enabled to start on boot
- [x] Automated backups configured (daily at 2:00 AM)
- [x] Backup retention configured (7/4/12)
- [ ] Nginx directives added in Plesk (👈 DO THIS NOW)
- [ ] SSL certificate enabled (if not already)
- [ ] Test API through domain

---

## 🎯 What's Working

✅ Backend API running on localhost:8001  
✅ Database connection working  
✅ Health checks responding  
✅ Systemd service managing backend  
✅ Automated nightly backups  
✅ Service will auto-start on reboot  

**Next**: Add Nginx directives in Plesk to proxy requests from music.quilty.app to the backend!

---

*Setup completed: October 31, 2025*
*Backend version: 0.1.0*

