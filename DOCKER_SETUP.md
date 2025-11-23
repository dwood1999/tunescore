# TuneScore Docker Setup Guide

This guide explains how to run TuneScore in Docker containers, ensuring complete isolation from other applications on your server (like quilty.app).

## Why Docker?

Running TuneScore in Docker containers provides:
- **Complete isolation** from other applications on the same server
- **No dependency conflicts** - all dependencies are contained
- **Easy deployment** - consistent environment across development and production
- **Resource management** - better control over CPU, memory, and network
- **Security** - isolated processes with minimal privileges

## Architecture

TuneScore uses a multi-container architecture:

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (Host)                      │
│         Reverse Proxy for music.quilty.app          │
└────────────────┬────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────────┐
│Frontend│  │Backend │  │PostgreSQL  │
│Container│  │Container│  │Container  │
│:5128   │  │:8001   │  │:5433      │
└────────┘  └───┬────┘  └───────────┘
                │
            ┌───▼────┐
            │ Redis  │
            │:6380   │
            └────────┘
```

## Requirements

- Docker (20.10+)
- Docker Compose (v2.0+)
- 4GB+ RAM recommended
- 20GB+ disk space

## Quick Start

### 1. Initial Setup

```bash
cd /home/dwood/tunescore
./scripts/docker-setup.sh
```

This script will:
- Install Docker if not already installed
- Create `.env` file with secure passwords
- Create necessary directories

### 2. Configure Environment

Edit `.env` file and add your API keys (optional):

```bash
nano .env
```

Update these if you want AI features:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET`
- `YOUTUBE_API_KEY`

### 3. Start Services

```bash
./scripts/docker-start.sh
```

This will:
- Build all Docker containers
- Start all services
- Run database migrations
- Health check all containers

### 4. Configure Nginx

Copy the provided nginx configuration:

```bash
sudo cp infra/nginx/music.quilty.app.docker.conf /etc/nginx/sites-available/music.quilty.app
sudo ln -sf /etc/nginx/sites-available/music.quilty.app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Access TuneScore

- **Production**: https://music.quilty.app
- **Backend API**: https://music.quilty.app/api/v1/docs
- **Direct (localhost)**: http://localhost:5128

## Port Configuration

TuneScore uses different ports from quilty.app to avoid conflicts:

| Service    | Host Port | Container Port | Purpose           |
|------------|-----------|----------------|-------------------|
| Frontend   | 5128      | 5128          | Web UI            |
| Backend    | 8001      | 8001          | API               |
| PostgreSQL | 5433      | 5432          | Database          |
| Redis      | 6380      | 6379          | Cache             |

All ports are only exposed on `127.0.0.1` (localhost) for security.

## Management Scripts

### Start/Stop

```bash
# Start all services
./scripts/docker-start.sh

# Stop all services
./scripts/docker-stop.sh
```

### Logs

```bash
# View all logs
./scripts/docker-logs.sh

# View specific service logs
./scripts/docker-logs.sh backend
./scripts/docker-logs.sh frontend
./scripts/docker-logs.sh postgres
```

### Rebuild

```bash
# Rebuild all services
./scripts/docker-rebuild.sh

# Rebuild specific service
./scripts/docker-rebuild.sh backend
```

### Database Operations

```bash
# Run migrations
./scripts/docker-migrate.sh

# Create backup
./scripts/docker-backup.sh

# Restore from backup
./scripts/docker-restore.sh backups/tunescore_backup_20250123_120000.sql.gz
```

### Shell Access

```bash
# Backend shell
./scripts/docker-shell.sh backend

# Frontend shell
./scripts/docker-shell.sh frontend

# PostgreSQL psql
./scripts/docker-shell.sh postgres
```

## Updating Dependencies

### Backend (Python)

The backend dependencies are updated in `backend/pyproject.toml`. To apply updates:

```bash
./scripts/docker-rebuild.sh backend
```

### Frontend (Node.js)

The frontend dependencies are updated in `frontend/package.json`. To apply updates:

```bash
./scripts/docker-rebuild.sh frontend
```

## Security Features

### Container Security

- Non-root users in all containers
- Read-only filesystem where possible
- No unnecessary capabilities
- Private network (bridge)
- Health checks for all services

### Network Isolation

- Docker network: `172.20.0.0/16` (isolated from quilty.app)
- Services only expose ports to `127.0.0.1`
- Nginx reverse proxy handles public access
- Rate limiting on API endpoints

### Data Security

- Encrypted connections (SSL/TLS via nginx)
- Secure password generation
- Environment variables for secrets
- No secrets in Docker images
- Database backups with rotation

## Monitoring

### Check Service Status

```bash
docker compose ps
```

### Check Resource Usage

```bash
docker stats
```

### Check Logs

```bash
# Last 100 lines, follow mode
./scripts/docker-logs.sh

# Specific service
./scripts/docker-logs.sh backend
```

## Troubleshooting

### Services Won't Start

```bash
# Check if ports are already in use
sudo netstat -tulpn | grep -E '5128|8001|5433|6380'

# View detailed logs
./scripts/docker-logs.sh

# Check Docker status
sudo systemctl status docker
```

### Database Connection Issues

```bash
# Check if PostgreSQL is healthy
docker compose ps postgres

# Connect to database manually
./scripts/docker-shell.sh postgres
```

### Out of Disk Space

```bash
# Remove old images and containers
docker system prune -a

# Remove old database backups
cd backups && ls -t | tail -n +8 | xargs rm
```

### Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER backend/files backend/logs logs backups
```

## Migration from Non-Docker Setup

If you were running TuneScore without Docker:

### 1. Stop Old Services

```bash
sudo systemctl stop tunescore-backend
pkill -f "vite preview"
```

### 2. Backup Database

```bash
pg_dump tunescore > /tmp/tunescore_migration.sql
```

### 3. Start Docker Setup

```bash
./scripts/docker-start.sh
```

### 4. Restore Database

```bash
cat /tmp/tunescore_migration.sql | docker compose exec -T postgres psql -U tunescore tunescore
```

### 5. Disable Old Services (Optional)

```bash
sudo systemctl disable tunescore-backend
```

## Performance Tuning

### Increase Container Resources

Edit `docker-compose.yml` and add resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Optimize PostgreSQL

The Docker setup includes optimized PostgreSQL settings in `docker-compose.yml`:
- Increased shared buffers
- Connection pooling
- WAL optimization
- Statistics tracking

## Backup Strategy

### Automated Backups

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * cd /home/dwood/tunescore && ./scripts/docker-backup.sh >> logs/backup.log 2>&1
```

### Backup Rotation

- Daily backups: kept for 7 days
- Weekly backups: kept for 30 days
- Monthly backups: kept for 1 year

Implement in cron:

```bash
# Weekly backup (Sundays at 3 AM)
0 3 * * 0 cd /home/dwood/tunescore && ./scripts/docker-backup.sh && mv backups/tunescore_backup_* backups/weekly/

# Monthly backup (1st of month at 4 AM)
0 4 1 * * cd /home/dwood/tunescore && ./scripts/docker-backup.sh && mv backups/tunescore_backup_* backups/monthly/
```

## Support

For issues:
1. Check logs: `./scripts/docker-logs.sh`
2. Verify services: `docker compose ps`
3. Check nginx: `sudo nginx -t && sudo tail -f /var/log/nginx/music.quilty.app.error.log`

## Production Checklist

Before going live:

- [ ] Update `.env` with production values
- [ ] Change default passwords
- [ ] Configure SSL certificates
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Test restore procedure
- [ ] Set up monitoring
- [ ] Configure firewall rules
- [ ] Review nginx rate limits
- [ ] Test health checks
- [ ] Document any customizations

## Development vs Production

### Development Mode

```bash
# Use docker-compose.dev.yml (if created)
docker compose -f docker-compose.dev.yml up
```

### Production Mode

```bash
# Use standard docker-compose.yml
./scripts/docker-start.sh
```

Key differences:
- Production uses optimized builds
- Development mounts source code as volumes
- Production has stricter security settings
- Development includes debug tools

## Next Steps

1. Review and update `.env` file
2. Run `./scripts/docker-start.sh`
3. Configure nginx reverse proxy
4. Set up SSL certificates
5. Test the application
6. Configure automated backups
7. Set up monitoring

For more information, see:
- `README.md` - General project overview
- `README_DEV.md` - Development guidelines
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend documentation

