#!/bin/bash
# TuneScore Docker Setup Script
# This script sets up the Docker environment for TuneScore

set -e

echo "🎵 TuneScore Docker Setup"
echo "========================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed. Please log out and back in for group changes to take effect."
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo "✅ Docker Compose installed."
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.docker.template .env
    
    # Generate secure passwords
    POSTGRES_PASS=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update .env with generated values
    sed -i "s/POSTGRES_PASSWORD=changeme_generate_secure_password/POSTGRES_PASSWORD=$POSTGRES_PASS/" .env
    sed -i "s/SECRET_KEY=changeme_generate_secure_secret_key/SECRET_KEY=$SECRET_KEY/" .env
    
    echo "✅ Created .env file with generated passwords."
    echo "⚠️  Please review and update .env with your API keys if needed."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/logs backend/files logs backups
chmod 755 backend/logs backend/files logs backups

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update .env file with your API keys"
echo "2. Run: ./scripts/docker-start.sh"
echo ""

