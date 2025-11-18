# Nginx Setup Guide for TuneScore

This guide covers setting up Nginx as a reverse proxy for TuneScore.

## Prerequisites

- Ubuntu/Debian Linux server
- TuneScore backend running on port 8001
- Domain name pointing to your server (optional, for SSL)

## Installation

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Verify Nginx is Running

```bash
sudo systemctl status nginx
```

## Configuration

### 1. Copy Configuration File

```bash
# Copy the TuneScore Nginx config
sudo cp /home/dwood/tunescore/infra/nginx/tunescore.conf /etc/nginx/sites-available/tunescore

# Edit the configuration
sudo nano /etc/nginx/sites-available/tunescore
```

### 2. Update Domain Name

Replace `tunescore.yourdomain.com` with your actual domain name in the config file:

```nginx
server_name tunescore.yourdomain.com;
```

If you don't have a domain, you can use your server's IP address or `localhost`.

### 3. Enable the Site

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/tunescore /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default
```

### 4. Test Configuration

```bash
sudo nginx -t
```

You should see:
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 5. Reload Nginx

```bash
sudo systemctl reload nginx
```

## SSL Setup with Let's Encrypt

### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
sudo certbot --nginx -d tunescore.yourdomain.com
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

### 3. Auto-Renewal

Certbot automatically sets up a cron job for renewal. Test it:

```bash
sudo certbot renew --dry-run
```

### 4. Update Nginx Config

After getting the certificate, update the SSL paths in `/etc/nginx/sites-available/tunescore`:

```nginx
ssl_certificate /etc/letsencrypt/live/tunescore.yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/tunescore.yourdomain.com/privkey.pem;
ssl_trusted_certificate /etc/letsencrypt/live/tunescore.yourdomain.com/chain.pem;
```

Then reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Configuration for Development (No SSL)

If you're setting up for development without SSL, use this simplified config:

```nginx
server {
    listen 80;
    server_name localhost;

    client_max_body_size 500M;
    
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:5128;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Testing

### 1. Test Backend API

```bash
# Without Nginx (direct to backend)
curl http://localhost:8001/api/v1/health

# Through Nginx
curl http://tunescore.yourdomain.com/api/v1/health
```

### 2. Test Upload

```bash
curl -X POST "http://tunescore.yourdomain.com/api/v1/tracks/upload" \
  -F 'track_data={"title":"Test","artist_name":"Test Artist"}' \
  -F "audio_file=@test.mp3"
```

### 3. Check Logs

```bash
# Nginx access log
sudo tail -f /var/log/nginx/tunescore_access.log

# Nginx error log
sudo tail -f /var/log/nginx/tunescore_error.log

# Backend logs
tail -f /home/dwood/tunescore/logs/api_prompts.log
```

## Rate Limiting

The configuration includes three rate limiting zones:

1. **API endpoints**: 300 requests/minute
2. **Auth endpoints**: 50 requests/minute
3. **Upload endpoints**: 10 requests/minute

When rate limit is exceeded, Nginx returns HTTP 429 (Too Many Requests).

### Adjust Rate Limits

Edit `/etc/nginx/sites-available/tunescore`:

```nginx
# Change these values as needed
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=300r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=50r/m;
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;
```

Then reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Troubleshooting

### Nginx Won't Start

```bash
# Check configuration
sudo nginx -t

# Check error log
sudo tail -50 /var/log/nginx/error.log

# Check if port 80/443 is already in use
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### 502 Bad Gateway

This means Nginx can't connect to the backend.

```bash
# Check if backend is running
curl http://localhost:8001/api/v1/health

# Check backend logs
tail -f /home/dwood/tunescore/logs/api_prompts.log

# Restart backend
sudo systemctl restart tunescore-backend
```

### 413 Request Entity Too Large

Increase `client_max_body_size`:

```nginx
client_max_body_size 1000M;  # Increase to 1GB
```

### 504 Gateway Timeout

Increase timeout values:

```nginx
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;
```

### SSL Certificate Issues

```bash
# Check certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check SSL configuration
sudo nginx -t
```

## Security Best Practices

### 1. Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Or if using firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. Fail2Ban for DDoS Protection

```bash
# Install fail2ban
sudo apt install fail2ban

# Create jail for Nginx
sudo nano /etc/fail2ban/jail.local
```

Add:

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/tunescore_error.log
maxretry = 5
findtime = 600
bantime = 3600
```

Restart fail2ban:

```bash
sudo systemctl restart fail2ban
```

### 3. Hide Nginx Version

Add to `/etc/nginx/nginx.conf` in the `http` block:

```nginx
server_tokens off;
```

### 4. Enable ModSecurity (Optional)

For advanced WAF protection:

```bash
sudo apt install libnginx-mod-security
```

## Performance Tuning

### 1. Enable Gzip Compression

Add to `/etc/nginx/nginx.conf`:

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
```

### 2. Optimize Worker Processes

In `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_connections 1024;
```

### 3. Enable HTTP/2

Already enabled in the TuneScore config:

```nginx
listen 443 ssl http2;
```

## Monitoring

### 1. Enable Nginx Status Page

Add to your config:

```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

Check status:

```bash
curl http://localhost/nginx_status
```

### 2. Log Analysis

```bash
# Most accessed endpoints
sudo awk '{print $7}' /var/log/nginx/tunescore_access.log | sort | uniq -c | sort -rn | head -20

# Response codes
sudo awk '{print $9}' /var/log/nginx/tunescore_access.log | sort | uniq -c | sort -rn

# Top IPs
sudo awk '{print $1}' /var/log/nginx/tunescore_access.log | sort | uniq -c | sort -rn | head -20
```

### 3. Real-time Monitoring

```bash
# Watch access log
sudo tail -f /var/log/nginx/tunescore_access.log

# Watch error log
sudo tail -f /var/log/nginx/tunescore_error.log
```

## Maintenance

### Reload Configuration

```bash
# Test config first
sudo nginx -t

# Reload (no downtime)
sudo systemctl reload nginx
```

### Restart Nginx

```bash
sudo systemctl restart nginx
```

### View Logs

```bash
# Access log
sudo tail -f /var/log/nginx/tunescore_access.log

# Error log
sudo tail -f /var/log/nginx/tunescore_error.log
```

### Rotate Logs

Nginx logs are automatically rotated by logrotate. Config is in:
```
/etc/logrotate.d/nginx
```

## Complete Setup Checklist

- [ ] Install Nginx
- [ ] Copy and configure tunescore.conf
- [ ] Update domain name in config
- [ ] Enable site (symlink to sites-enabled)
- [ ] Test configuration (`nginx -t`)
- [ ] Reload Nginx
- [ ] Set up SSL with Let's Encrypt (production)
- [ ] Configure firewall
- [ ] Set up fail2ban (optional)
- [ ] Test API endpoints through Nginx
- [ ] Test file uploads
- [ ] Monitor logs
- [ ] Set up monitoring/alerting

---

*Last Updated: October 31, 2025*

