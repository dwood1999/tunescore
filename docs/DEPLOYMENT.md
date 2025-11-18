# TuneScore Deployment Guide

This guide covers deploying TuneScore to production using systemd services.

## Prerequisites

- Ubuntu/Debian Linux server
- PostgreSQL 14+ installed
- Python 3.12+ installed
- Poetry installed
- FFmpeg installed
- Nginx or Caddy (optional, for reverse proxy)

## Initial Setup

### 1. Clone and Setup Project

```bash
cd /home/dwood
git clone <repository-url> tunescore
cd tunescore
```

### 2. Install Dependencies

```bash
cd backend
poetry install --no-dev
```

### 3. Configure Environment

```bash
cp env.template .env
nano .env
```

Required configuration:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Random secret key for JWT tokens
- `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` (optional)
- `YOUTUBE_API_KEY` (optional)

### 4. Initialize Database

```bash
# Create database
createdb -U dwood tunescore

# Run migrations
cd backend
poetry run alembic upgrade head
```

## Systemd Services

### 1. Install Backend Service

```bash
# Copy service file
sudo cp infra/systemd/tunescore-backend.service /etc/systemd/system/

# Update paths in service file if needed
sudo nano /etc/systemd/system/tunescore-backend.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable tunescore-backend
sudo systemctl start tunescore-backend

# Check status
sudo systemctl status tunescore-backend
```

### 2. Install Backup Service and Timer

```bash
# Copy service and timer files
sudo cp infra/systemd/tunescore-backup.service /etc/systemd/system/
sudo cp infra/systemd/tunescore-backup.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable tunescore-backup.timer
sudo systemctl start tunescore-backup.timer

# Check timer status
sudo systemctl list-timers tunescore-backup.timer
```

### 3. Test Backup Manually

```bash
# Run backup manually
./scripts/backup_db.sh

# Check backup files
ls -lh backups/
```

## Log Rotation

### Install Logrotate Configuration

```bash
# Copy logrotate config
sudo cp infra/logrotate/tunescore /etc/logrotate.d/

# Test configuration
sudo logrotate -d /etc/logrotate.d/tunescore

# Force rotation (optional)
sudo logrotate -f /etc/logrotate.d/tunescore
```

## Reverse Proxy (Nginx)

### Install Nginx Configuration

Create `/etc/nginx/sites-available/tunescore`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Increase timeouts for audio processing
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;

    # Increase max body size for audio uploads
    client_max_body_size 500M;

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        # Frontend (when implemented)
        proxy_pass http://localhost:5128;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/tunescore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Health Checks

The API provides several health check endpoints:

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with dependency checks
- `GET /api/v1/health/ready` - Kubernetes-style readiness probe
- `GET /api/v1/health/live` - Kubernetes-style liveness probe
- `GET /api/v1/metrics` - Basic metrics

### Check Service Status

```bash
# Backend status
sudo systemctl status tunescore-backend

# View logs
sudo journalctl -u tunescore-backend -f

# Check health endpoint
curl http://localhost:8001/api/v1/health/detailed
```

### Monitor Backups

```bash
# Check backup timer
sudo systemctl status tunescore-backup.timer

# View backup logs
cat logs/backup.log

# List backups
ls -lh backups/
```

## Backup and Restore

### Manual Backup

```bash
./scripts/backup_db.sh
```

### Restore from Backup

```bash
# List available backups
./scripts/restore_db.sh

# Restore specific backup
./scripts/restore_db.sh backups/tunescore_backup_20251031_020000.sql.gz
```

### Backup Schedule

- **Daily**: 2:00 AM (keeps last 7 days)
- **Weekly**: Sunday 2:00 AM (keeps last 4 weeks)
- **Monthly**: 1st of month 2:00 AM (keeps last 12 months)

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
sudo journalctl -u tunescore-backend -n 50

# Check database connection
psql -U dwood tunescore -c "SELECT 1"

# Check environment
cd backend
poetry run python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
psql -U dwood -l | grep tunescore

# Test connection
psql -U dwood tunescore -c "SELECT version()"
```

### Audio Processing Fails

```bash
# Check FFmpeg installation
ffmpeg -version

# Install if missing
sudo apt install ffmpeg

# Check storage directory permissions
ls -ld /home/dwood/tunescore/files
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep uvicorn

# Restart service
sudo systemctl restart tunescore-backend

# Check for memory leaks in logs
sudo journalctl -u tunescore-backend | grep -i memory
```

## Performance Tuning

### Database Connection Pool

Edit `.env`:

```bash
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### Uvicorn Workers

For production, run with multiple workers:

Edit `/etc/systemd/system/tunescore-backend.service`:

```ini
ExecStart=/path/to/uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Rate Limiting

Adjust in `app/middleware/rate_limit.py` if needed.

## Security Checklist

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall (ufw/iptables)
- [ ] Set up fail2ban for SSH protection
- [ ] Restrict database access to localhost
- [ ] Enable PostgreSQL SSL connections
- [ ] Set proper file permissions (chmod 600 .env)
- [ ] Configure CORS origins for production domain
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular backup testing
- [ ] Keep dependencies updated

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

### Update Dependencies

```bash
cd backend
poetry update
poetry run alembic upgrade head
sudo systemctl restart tunescore-backend
```

### Database Maintenance

```bash
# Vacuum database
psql -U dwood tunescore -c "VACUUM ANALYZE"

# Check database size
psql -U dwood tunescore -c "SELECT pg_size_pretty(pg_database_size('tunescore'))"

# Check table sizes
psql -U dwood tunescore -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC"
```

## Monitoring and Alerts

### Set Up Monitoring

Consider using:
- **Prometheus + Grafana** for metrics
- **Sentry** for error tracking
- **Uptime Robot** for uptime monitoring
- **CloudWatch/DataDog** for comprehensive monitoring

### Custom Alerts

Monitor these metrics:
- API response times
- Error rates
- Database connection pool usage
- Disk space
- Memory usage
- Backup success/failure

---

*Last Updated: October 31, 2025*

