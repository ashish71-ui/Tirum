#!/bin/bash

# 🚀 Tirum Backend - Docker Deployment Script for Azure VM

set -e

echo "=========================================="
echo "🐳 Tirum Backend - Docker Deployment"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "Step 1: Checking Docker..."
if command -v docker &> /dev/null; then
    print_status "Docker installed: $(docker --version)"
else
    print_error "Docker not found"
    exit 1
fi

echo ""
echo "Step 2: Starting Docker service..."
sudo systemctl start docker 2>/dev/null || true
print_status "Docker service running"

# Check if we're in Tirum directory or tirum_backend
if [ -f "docker-compose.yml" ]; then
    PROJECT_DIR="$(pwd)"
elif [ -f "../docker-compose.yml" ]; then
    PROJECT_DIR="$(pwd)/.."
else
    PROJECT_DIR="$HOME/Tirum/tirum_backend"
fi

echo ""
echo "Step 3: Setting up directories..."
mkdir -p $PROJECT_DIR/postgres_data
mkdir -p $PROJECT_DIR/redis_data
mkdir -p $PROJECT_DIR/staticfiles
mkdir -p $PROJECT_DIR/media
print_status "Directories ready"

echo ""
echo "Step 4: Checking environment..."
if [ -f "$PROJECT_DIR/.env" ]; then
    print_status ".env file found - using existing configuration"
else
    print_warning ".env not found - please create it!"
    echo "Create $PROJECT_DIR/.env with your settings"
    exit 1
fi

echo ""
echo "Step 5: Stopping containers..."
cd $PROJECT_DIR
sudo docker compose down 2>/dev/null || true
print_status "Containers stopped"

echo ""
echo "Step 6: Building and starting containers..."
print_warning "This may take a few minutes..."

sudo docker compose build --no-cache
sudo docker compose up -d

echo ""
echo "Step 7: Waiting for services..."
sleep 15

echo ""
echo "Step 8: Running migrations..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if sudo docker compose exec -T backend python manage.py migrate --noinput 2>/dev/null; then
        print_status "Migrations completed"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Waiting for database... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 3
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_warning "Migration timed out - run manually later"
fi

echo ""
echo "Step 9: Creating admin user..."
sudo docker compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@yourdomain.com', 'admin123')
    print('Admin created')
else:
    print('Admin exists')
" 2>/dev/null || print_warning "Could not create admin"

echo ""
echo "Step 10: Collecting static files..."
sudo docker compose exec -T backend python manage.py collectstatic --noinput 2>/dev/null || true
print_status "Static files ready"

echo ""
echo "Step 11: Verifying deployment..."
sleep 5

echo ""
echo "Container Status:"
sudo docker compose ps

echo ""
HEALTH_CHECK=$(curl -s http://localhost/health/ 2>/dev/null || echo '{"status":"unhealthy"}')
echo "Health check: $HEALTH_CHECK"

VM_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Access your app:"
echo "   API:    http://$VM_IP/api/"
echo "   Admin:  http://$VM_IP/admin/"
echo "   Health: http://$VM_IP/health/"
echo ""
echo "📝 Commands:"
echo "   Logs:   sudo docker compose logs -f"
echo "   Restart: sudo docker compose restart"
echo "   Stop:   sudo docker compose down"
echo "=========================================="
