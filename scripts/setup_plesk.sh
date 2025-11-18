#!/bin/bash
# Automated Plesk setup script for TuneScore on music.quilty.app

set -e

SUDO_PASS='p3ter[thiel]'
DOMAIN="music.quilty.app"

echo "🚀 Setting up TuneScore for $DOMAIN..."

# Step 1: Create systemd service
echo "📝 Creating systemd service..."
echo "$SUDO_PASS" | sudo -S tee /etc/systemd/system/tunescore-backend.service > /dev/null << 'EOF'
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

# Step 2: Reload systemd
echo "🔄 Reloading systemd..."
echo "$SUDO_PASS" | sudo -S systemctl daemon-reload

# Step 3: Enable service
echo "✅ Enabling tunescore-backend service..."
echo "$SUDO_PASS" | sudo -S systemctl enable tunescore-backend

# Step 4: Update .env with correct CORS
echo "🔧 Updating CORS configuration..."
cd /home/dwood/tunescore

# Backup existing .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update or add CORS settings
if grep -q "BACKEND_CORS_ORIGINS=" .env; then
    sed -i "s|BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN,http://localhost:5128|g" .env
else
    echo "BACKEND_CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN,http://localhost:5128" >> .env
fi

if grep -q "FRONTEND_URL=" .env; then
    sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=https://$DOMAIN|g" .env
else
    echo "FRONTEND_URL=https://$DOMAIN" >> .env
fi

# Step 5: Start the service
echo "🚀 Starting tunescore-backend service..."
echo "$SUDO_PASS" | sudo -S systemctl start tunescore-backend

# Step 6: Wait a moment for service to start
sleep 3

# Step 7: Check status
echo "📊 Checking service status..."
echo "$SUDO_PASS" | sudo -S systemctl status tunescore-backend --no-pager || true

# Step 8: Test backend
echo ""
echo "🧪 Testing backend..."
if curl -s http://localhost:8001/api/v1/health > /dev/null; then
    echo "✅ Backend is responding!"
    curl -s http://localhost:8001/api/v1/health | python3 -m json.tool
else
    echo "❌ Backend is not responding. Check logs:"
    echo "   sudo journalctl -u tunescore-backend -n 50"
fi

# Step 9: Create backup service and timer
echo ""
echo "💾 Setting up automated backups..."
echo "$SUDO_PASS" | sudo -S cp /home/dwood/tunescore/infra/systemd/tunescore-backup.service /etc/systemd/system/
echo "$SUDO_PASS" | sudo -S cp /home/dwood/tunescore/infra/systemd/tunescore-backup.timer /etc/systemd/system/
echo "$SUDO_PASS" | sudo -S systemctl daemon-reload
echo "$SUDO_PASS" | sudo -S systemctl enable tunescore-backup.timer
echo "$SUDO_PASS" | sudo -S systemctl start tunescore-backup.timer

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add Nginx directives in Plesk:"
echo "   - Go to Websites & Domains > $DOMAIN > Apache & Nginx Settings"
echo "   - Add the directives from: infra/nginx/plesk-minimal.conf"
echo ""
echo "2. Enable SSL in Plesk:"
echo "   - Go to SSL/TLS Certificates"
echo "   - Get Let's Encrypt certificate"
echo ""
echo "3. Test the setup:"
echo "   curl https://$DOMAIN/api/v1/health"
echo "   Open: https://$DOMAIN/api/v1/docs"
echo ""
echo "📝 View logs:"
echo "   sudo journalctl -u tunescore-backend -f"
echo "   tail -f /home/dwood/tunescore/logs/api_prompts.log"

