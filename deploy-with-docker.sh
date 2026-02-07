#!/bin/bash

# 🚀 Tirum Backend - Docker Deployment Script for Azure VM
# This script installs Docker and deploys your application

set -e  # Exit on any error

echo "=========================================="
echo "🐳 Tirum Backend - Docker Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    print_warning "This script works best with sudo privileges"
fi

# Step 1: Check if Docker is installed
echo ""
echo "Step 1: Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_status "Docker is already installed: $(docker --version)"
    DOCKER_INSTALLED=true
else
    print_warning "Docker is not installed. Installing now..."
    DOCKER_INSTALLED=false
fi

# Step 2: Install Docker if needed
if [ "$DOCKER_INSTALLED" = false ]; then
    echo ""
    echo "Step 2: Installing Docker..."

    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_status "Docker installed successfully: $(docker --version)"
    print_status "Docker Compose installed: $(docker compose version)"
fi

# Step 3: Start Docker service
echo ""
echo "Step 3: Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker
print_status "Docker service is running"

# Step 4: Create project directories
echo ""
echo "Step 4: Setting up project directories..."
PROJECT_DIR="/home/$USER/tirum_backend"

if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    print_error "Please copy the project files to the VM first!"
    echo ""
    echo "Run this on your LOCAL machine:"
    echo "  cd Tirum"
    echo "  scp -r tirum_backend nginx docker-compose.yml deploy-with-docker.sh azureuser@YOUR_VM_IP:~/"
    exit 1
fi

# Create directories for persistent data
mkdir -p $PROJECT_DIR/postgres_data
mkdir -p $PROJECT_DIR/redis_data
mkdir -p $PROJECT_DIR/staticfiles
mkdir -p $PROJECT_DIR/media

print_status "Directories created"

# Step 5: Configure Environment
echo ""
echo "Step 5: Configuring environment..."

ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp $PROJECT_DIR/.env.example $ENV_FILE
        print_status "Created .env from .env.example"
        print_warning "Please edit $ENV_FILE with your production values!"
        echo ""
        echo "Required settings to change:"
        echo "  - DJANGO_SECRET_KEY"
        echo "  - POSTGRES_PASSWORD"
        echo "  - REDIS_PASSWORD"
        echo ""
        echo "Run: nano $ENV_FILE"
        echo ""
        read -p "Press Enter after editing the .env file to continue..."
    else
        print_error ".env.example not found!"
        exit 1
    fi
else
    print_status "Using existing .env file"
fi

# Step 6: Stop existing containers
echo ""
echo "Step 6: Stopping existing containers..."
cd $PROJECT_DIR
sudo docker compose -f docker-compose.yml down 2>/dev/null || true
print_status "Existing containers stopped"

# Step 7: Build and start containers
echo ""
echo "Step 7: Building and starting containers..."
print_warning "This may take a few minutes on first run..."

# Build images
sudo docker compose -f docker-compose.yml build --no-cache

# Start services
sudo docker compose -f docker-compose.yml up -d

# Step 8: Wait for services to be ready
echo ""
echo "Step 8: Waiting for services to be ready..."
sleep 10

# Step 9: Run database migrations
echo ""
echo "Step 9: Running database migrations..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if sudo docker compose -f docker-compose.yml exec -T backend python manage.py migrate --noinput 2>/dev/null; then
        print_status "Database migrations completed successfully"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Waiting for database... (attempt $RETRY_COUNT/$MAX_RETRIES)"
        sleep 3
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_warning "Database migration timed out. The database might still be starting up."
    print_warning "Run 'docker compose -f docker-compose.yml exec backend python manage.py migrate' manually later."
fi

# Step 10: Create superuser (optional)
echo ""
echo "Step 10: Creating superuser..."
echo "Creating admin user with default credentials..."
echo "(Change the password after first login!)"

sudo docker compose -f docker-compose.yml exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@yourdomain.com', 'admin123')
    print('Admin user created successfully')
else:
    print('Admin user already exists')
" 2>/dev/null || print_warning "Could not create admin user. Create it manually later."

# Step 11: Collect static files
echo ""
echo "Step 11: Collecting static files..."
sudo docker compose -f docker-compose.yml exec -T backend python manage.py collectstatic --noinput 2>/dev/null || true
print_status "Static files collected"

# Step 12: Verify deployment
echo ""
echo "Step 12: Verifying deployment..."
sleep 5

# Check container status
echo ""
echo "Container Status:"
sudo docker compose -f docker-compose.yml ps

# Test health endpoint
echo ""
echo "Testing health endpoint..."
HEALTH_CHECK=$(curl -s http://localhost/health/ 2>/dev/null || echo '{"status":"unhealthy"}')
echo "Health check response: $HEALTH_CHECK"

# Get IP address
VM_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

# Summary
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Your application is now accessible at:"
echo "   - Main URL: http://$VM_IP"
echo "   - API:      http://$VM_IP/api/"
echo "   - Admin:    http://$VM_IP/admin/"
echo "   - Health:   http://$VM_IP/health/"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:    docker compose -f docker-compose.yml logs -f"
echo "   Restart:      docker compose -f docker-compose.yml restart"
echo "   Stop:         docker compose -f docker-compose.yml down"
echo "   Update:       docker compose -f docker-compose.yml up -d --build"
echo ""
echo "🔐 Security Recommendations:"
echo "   1. Change admin password immediately!"
echo "   2. Configure SSL with Let's Encrypt: sudo certbot --nginx"
echo "   3. Set up firewall: sudo ufw allow ssh && sudo ufw enable"
echo ""
echo "📁 Files Location: $PROJECT_DIR"
echo "=========================================="
