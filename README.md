# 🚀 Tirum Backend - Production Deployment Guide

## 📁 Project Structure

```
Tirum/
├── docker-compose.yml          # ✅ Production Docker Compose (USE THIS)
├── deploy-with-docker.sh       # ✅ Automated deployment script for Azure VM
├── AZURE_VM_DEPLOYMENT.md     # ✅ Complete deployment guide
│
├── tirum_backend/             # Django Backend
│   ├── .env.example           # Environment template
│   ├── .env                   # Your production environment (create this)
│   ├── Dockerfile.production  # Production Docker image
│   ├── requirements.txt       # Python dependencies
│   ├── manage.py
│   ├── tirum_backend/
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py           # URL routing
│   │   └── wsgi.py
│   └── ...
│
└── nginx/                     # Nginx Web Server
    ├── default.conf           # Nginx configuration
    └── Dockerfile             # Nginx Docker image
```

---

## 🏠 Local Development vs 🚀 Production

| Feature | Local Development | Production |
|---------|------------------|------------|
| **Command** | `python manage.py runserver` | `docker compose up -d` |
| **Database** | SQLite | PostgreSQL |
| **Server** | Django dev server | Gunicorn + Nginx |
| **Debug** | Enabled (`DEBUG=True`) | Disabled (`DEBUG=False`) |
| **Environment** | `.env` with dev values | `.env` with production values |

---

## 🚀 Quick Deployment to Azure VM

### Step 1: Configure Environment (Local Machine)

```bash
cd Tirum/tirum_backend

# Create .env file
cp .env.example .env
nano .env

# Edit these values:
# DJANGO_SECRET_KEY=your-super-secret-key
# POSTGRES_PASSWORD=your-password
# REDIS_PASSWORD=your-redis-password
# ALLOWED_HOSTS=your-vm-ip,your-domain.com
```

### Step 2: Copy Files to VM

```bash
cd Tirum

# Copy to Azure VM
scp -r tirum_backend nginx docker-compose.yml deploy-with-docker.sh azureuser@YOUR_VM_IP:~/
```

### Step 3: Deploy on VM

```bash
# SSH into VM
ssh azureuser@YOUR_VM_IP

# Configure .env on VM
cd ~/tirum_backend
nano .env

# Run deployment
chmod +x ../deploy-with-docker.sh
../deploy-with-docker.sh
```

---

## 📋 Essential Docker Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build

# View status
docker compose ps
```

---

## 🔧 Configuration Files

### `.env` Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_SECRET_KEY` | Django secret key (keep secure!) | ✅ Yes |
| `DEBUG` | Debug mode (False for production) | ✅ Yes |
| `ALLOWED_HOSTS` | Allowed domain/IPs | ✅ Yes |
| `POSTGRES_DB` | Database name | ✅ Yes |
| `POSTGRES_USER` | Database username | ✅ Yes |
| `POSTGRES_PASSWORD` | Database password | ✅ Yes |
| `POSTGRES_HOST` | Database host (db) | ✅ Yes |
| `POSTGRES_PORT` | Database port (5432) | ✅ Yes |
| `REDIS_HOST` | Redis host (redis) | ✅ Yes |
| `REDIS_PORT` | Redis port (6379) | ✅ Yes |
| `REDIS_PASSWORD` | Redis password | ✅ Yes |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins | ✅ Yes |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | ✅ Yes |

---

## 🛡️ Post-Deployment SecurityChange admin password**

1. ** at `/admin/`
2. **Set up SSL** with Let's Encrypt:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```
3. **Configure firewall**:
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

---

## 📞 Support

- See `AZURE_VM_DEPLOYMENT.md` for detailed deployment instructions
- See `.env.example` for all configuration options
