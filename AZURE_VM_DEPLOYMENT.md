# 🚀 Tirum Backend - Azure VM Deployment Guide (SSH Access)

## Docker vs Without Docker - Which to Choose?

### **Recommendation: Use Docker**

Docker is strongly recommended because:

| Aspect | Docker | Without Docker |
|--------|--------|----------------|
| **Setup Time** | ⭐ ~30 minutes | ⭐⭐⭐ ~2-3 hours |
| **Dependency Management** | ✅ Automatic | ❌ Manual setup |
| **Database Setup** | ✅ One command | ❌ Manual PostgreSQL |
| **Redis Setup** | ✅ One command | ❌ Manual Redis |
| **Scaling** | ✅ Easy | ❌ Difficult |
| **Rollback** | ✅ Instant | ❌ Manual |
| **Environment Variables** | ✅ Centralized | ⚠️ Systemd env files |
| **Security** | ✅ Isolated | ⚠️ System-wide |

---

## 🐳 Option 1: Docker Deployment (Recommended)

### Prerequisites on Your Local Machine

1. ✅ SSH is integrated and working
2. ✅ Azure VM IP address
3. ✅ Your domain DNS pointing to VM (optional but recommended)

### Step 1: Configure Environment Variables

On your **local machine**:

```bash
cd Tirum/tirum_backend

# Create .env file with production values
cp .env.example .env
nano .env
```

Edit the `.env` file with your values:

```env
# REQUIRED - Change these!
DJANGO_SECRET_KEY=your-super-secret-key-at-least-50-characters-long
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-vm-ip

# Database Configuration
POSTGRES_DB=tirum_db
POSTGRES_USER=tirum_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Configuration  
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=secure_redis_password

# Security (update with your domain)
CSRF_TRUSTED_ORIGINS=https://your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### Step 2: Copy Files to Azure VM

```bash
# From your local machine
cd Tirum

# Copy the entire project to VM
scp -r tirum_backend nginx docker-compose.production.yml deploy-with-docker.sh azureuser@YOUR_VM_IP:~/

# Or using SSH config (if configured)
scp -r tirum_backend nginx docker-compose.production.yml deploy-with-docker.sh azureuser@your-vm-name.eastus.cloudapp.azure.com:~/
```

### Step 3: Connect to VM and Deploy

```bash
# SSH into your VM
ssh azureuser@YOUR_VM_IP

# Once connected to VM:
cd ~/tirum_backend

# Edit .env file on VM
nano .env
# (Enter your actual production values here)

# Make deployment script executable
chmod +x ../deploy-with-docker.sh

# Run deployment
../deploy-with-docker.sh
```

### Step 4: Access Your Application

After deployment completes:
- **API**: `http://YOUR_VM_IP/api/`
- **Admin**: `http://YOUR_VM_IP/admin/`
- **Health Check**: `http://YOUR_VM_IP/health/`

---

## 🔧 Option 2: Direct Deployment (Without Docker)

### Step 1: SSH into VM and Install Dependencies

```bash
ssh azureuser@YOUR_VM_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib redis-server libpq-dev

# Install Python packages
cd ~
mkdir -p tirum_backend
cd tirum_backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install gunicorn psycopg2-binary redis channels-redis django-cors-headers djangorestframework drf-spectacular pillow channels asgiref sqlparse django
```

### Step 2: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -i -u postgres

# Create database and user
psql
CREATE USER tirum_user WITH PASSWORD 'secure_password_here';
CREATE DATABASE tirum_db OWNER tirum_user;
ALTER USER tirum_user WITH SUPERUSER;
\q

# Exit postgres user
exit
```

### Step 3: Configure Redis

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Find and modify these lines:
# bind 127.0.0.1 ::1
# requirepass your_redis_password

# Restart Redis
sudo systemctl restart redis
```

### Step 4: Configure Nginx

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/tirum

# Add this configuration:
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host $host;
    }

    location /static/ {
        alias /home/azureuser/tirum_backend/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
    }
}

# Enable the site
sudo ln -s /etc/nginx/sites-available/tirum /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Configure Environment Variables

```bash
# Create systemd service environment file
sudo nano /etc/systemd/system/tirum.service

[Unit]
Description=Tirum Django Backend
After=network.target

[Service]
User=azureuser
Group=www-data
WorkingDirectory=/home/azureuser/tirum_backend
Environment="PATH=/home/azureuser/tirum_backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=tirum_backend.settings"
Environment="DJANGO_SECRET_KEY=your-secret-key"
Environment="DEBUG=False"
Environment="ALLOWED_HOSTS=your-domain.com"
Environment="POSTGRES_DB=tirum_db"
Environment="POSTGRES_USER=tirum_user"
Environment="POSTGRES_PASSWORD=your-password"
Environment="POSTGRES_HOST=localhost"
Environment="POSTGRES_PORT=5432"
ExecStart=/home/azureuser/tirum_backend/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    tirum_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Step 6: Run Migrations and Collect Static Files

```bash
cd /home/azureuser/tirum_backend
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable tirum
sudo systemctl start tirum
```

---

## 📋 Quick Deployment Steps (Docker - Recommended)

### On Your Local Machine:

```bash
# 1. Configure .env file
cd Tirum/tirum_backend
cp .env.example .env
nano .env
# Edit: DJANGO_SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD

# 2. Copy files to VM
cd Tirum
scp -r tirum_backend nginx docker-compose.production.yml deploy-with-docker.sh azureuser@YOUR_VM_IP:~/

# 3. SSH to VM
ssh azureuser@YOUR_VM_IP

# 4. On VM:
cd ~/tirum_backend
nano .env  # Verify/enter values

# 5. Run deployment
chmod +x ../deploy-with-docker.sh
../deploy-with-docker.sh
```

### On Azure VM:

The `deploy-with-docker.sh` script will:
1. ✅ Install Docker & Docker Compose
2. ✅ Create necessary directories
3. ✅ Build and start all containers (PostgreSQL, Redis, Backend, Nginx)
4. ✅ Run database migrations
5. ✅ Create superuser
6. ✅ Show you the application URL

---

## 🔐 Essential Security Steps After Deployment

### 1. Configure Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Set Up SSL with Let's Encrypt (Free)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Configure Automatic Restarts

```bash
# Docker containers auto-restart with restart: unless-stopped
# For VM-level, ensure Docker starts on boot:
sudo systemctl enable docker
```

### 4. Set Up Backups

```bash
# Add to crontab for daily database backup
crontab -e

# Add this line:
0 2 * * * pg_dump -U tirum_user tirum_db > /home/azureuser/backups/tirum_$(date +\%Y\%m\%d).sql
```

---

## 📝 What Your .env File Does

The `.env` file is the **heart of your production configuration**. Here's what each setting does:

```env
# Django Security
DJANGO_SECRET_KEY=         # 🔐 Encrypts sessions & CSRF tokens. MUST be secret!
DEBUG=False                # 🚫 Turns off debug mode (security requirement)

# Allowed Hosts
ALLOWED_HOSTS=             # 🌐 Domains/IPs that can access your API

# Database Connection
POSTGRES_DB=               # Database name
POSTGRES_USER=             # Database username
POSTGRES_PASSWORD=         # 🔐 Database password
POSTGRES_HOST=db           # Docker service name (internal)
POSTGRES_PORT=5432         # PostgreSQL default port

# Redis Connection
REDIS_HOST=redis           # Docker service name (internal)
REDIS_PORT=6379            # Redis default port
REDIS_PASSWORD=            # 🔐 Redis password

# Security Headers
CSRF_TRUSTED_ORIGINS=      # Domains trusted for CSRF
CORS_ALLOWED_ORIGINS=      # Domains allowed for CORS requests
```

**Effect on Docker Deployment:**
- Docker Compose reads `.env` automatically ✅
- All containers share the same environment ✅
- No need to configure each service separately ✅

---

## 🆘 Troubleshooting

### Containers not starting?

```bash
# Check container status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs

# Check specific service
docker-compose -f docker-compose.production.yml logs backend
```

### Database connection error?

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.production.yml logs db

# Test connection
docker-compose -f docker-compose.production.yml exec db psql -U tirum_user -d tirum_db
```

### Can't access the application?

```bash
# Check if nginx is running
docker-compose -f docker-compose.production.yml logs nginx

# Test locally on VM
curl http://localhost/health/

# Check firewall
sudo ufw status
```

---

## 📞 Quick Commands Reference

```bash
# View all containers
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart all services
docker-compose -f docker-compose.production.yml restart

# Stop all services
docker-compose -f docker-compose.production.yml down

# Update and redeploy
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --build

# Create backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U tirum_user tirum_db > backup.sql
```

---

## ✅ Your Next Steps

1. **Copy the project to your VM** using `scp`
2. **Configure your `.env` file** with real production values
3. **Run the deployment script** on your VM
4. **Configure SSL** using Let's Encrypt
5. **Set up backups** for your database

The Docker approach is much simpler and more reliable for production! 🎉
