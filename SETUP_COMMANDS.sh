#!/bin/bash
# TuneScore Setup Commands for music.quilty.app
# Run these commands one by one

echo "=== TuneScore Setup for music.quilty.app ==="
echo ""
echo "Step 1: Install systemd service"
echo "Run this command:"
echo ""
echo "sudo cp /tmp/tunescore-backend.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable tunescore-backend && sudo systemctl start tunescore-backend"
echo ""
echo "---"
echo ""
echo "Step 2: Check service status"
echo "sudo systemctl status tunescore-backend"
echo ""
echo "---"
echo ""
echo "Step 3: Test backend"
echo "curl http://localhost:8001/api/v1/health"
echo ""
echo "---"
echo ""
echo "Step 4: Add these Nginx directives in Plesk"
echo "(Websites & Domains > music.quilty.app > Apache & Nginx Settings > Additional nginx directives)"
echo ""
cat << 'NGINX'
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
NGINX
echo ""
echo "---"
echo ""
echo "Step 5: Test through domain"
echo "curl https://music.quilty.app/api/v1/health"
echo ""
echo "Step 6: Open API docs"
echo "https://music.quilty.app/api/v1/docs"

