#!/bin/bash
# Update Plesk Nginx config to serve frontend on port 5128

NGINX_CONF="/var/www/vhosts/system/music.quilty.app/conf/vhost_nginx.conf"

if [ ! -f "$NGINX_CONF" ]; then
    echo "Error: Nginx config file not found: $NGINX_CONF"
    exit 1
fi

# Create backup
sudo cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"

# Check if frontend location already exists
if sudo grep -q "location / {" "$NGINX_CONF" && ! sudo grep -q "proxy_pass http://127.0.0.1:5128" "$NGINX_CONF"; then
    echo "Updating root location to proxy to frontend..."
    
    # Create temp file with new config
    sudo sed -i.bak \
        -e 's|location / {|# Frontend (SvelteKit) - proxies to port 5128\n    location / {\n        proxy_pass http://127.0.0.1:5128;|' \
        -e '/proxy_pass http:\/\/127.0.0.1:5128;/a\
        proxy_http_version 1.1;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
        proxy_set_header X-Forwarded-Host $host;\
        \
        # WebSocket support for HMR\
        proxy_set_header Upgrade $http_upgrade;\
        proxy_set_header Connection "upgrade";\
        proxy_cache_bypass $http_upgrade;' \
        "$NGINX_CONF"
    
    # Remove old redirect
    sudo sed -i.bak '/rewrite.*\/api\/v1\/docs permanent/d' "$NGINX_CONF"
    
    echo "✅ Nginx config updated"
else
    echo "Frontend proxy already configured or root location not found"
fi

# Reload Nginx
echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "✅ Done! Frontend should be accessible at https://music.quilty.app"

