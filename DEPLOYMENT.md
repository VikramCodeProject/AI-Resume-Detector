# 🚀 Production Deployment Guide

## Resume Truth Verification System - Production Deployment

**Last Updated:** February 20, 2026  
**Status:** ✅ Ready for Production Deployment

---

## 📋 Pre-Deployment Checklist

### Critical Security Items
- [ ] **Generate secure JWT secret**: Run `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] **Copy `.env.production` to `.env`** and replace ALL placeholder values
- [ ] **Never commit `.env` to Git** (already in `.gitignore`)
- [ ] **Obtain SSL/TLS certificates** (Let's Encrypt recommended)
- [ ] **Set up managed database** (AWS RDS, DigitalOcean, or similar)
- [ ] **Configure cloud storage** (AWS S3 or equivalent)

### Optional but Recommended
- [ ] Set up monitoring (Sentry, DataDog, or CloudWatch)
- [ ] Configure automated backups
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure CDN for frontend (CloudFlare, AWS CloudFront)
- [ ] Set up log aggregation (ELK Stack, Splunk)

---

## 🎯 Deployment Options

### Option 1: Docker Compose (Simple, Single Server)

**Best for:** Small-scale deployments, demos, internal tools  
**Time:** 10-15 minutes  
**Cost:** $5-20/month (single VPS)

#### Steps:

1. **Provision a server:**
   - DigitalOcean Droplet ($6/month)
   - AWS EC2 t3.small
   - Linode, Vultr, or Hetzner

2. **Install dependencies:**
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose git

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

3. **Clone and configure:**
```bash
git clone https://github.com/yourusername/UsMiniProject.git
cd UsMiniProject

# Copy production environment
cp .env.production .env

# Edit with your secrets
nano .env
```

4. **Generate JWT secret:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy output and paste into .env as JWT_SECRET
```

5. **Deploy:**
```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Check logs
docker-compose logs -f

# Verify health
curl http://localhost:8000/api/health
```

6. **Set up reverse proxy (nginx):**
```bash
sudo apt install nginx certbot python3-certbot-nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/resume-verify
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/resume-verify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

7. **Done!** Visit https://yourdomain.com

---

### Option 2: Cloud Platform (Managed, Easy)

**Best for:** Quick deployment, no DevOps experience needed  
**Time:** 15-30 minutes  
**Cost:** $15-50/month

#### A. Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create resume-verify-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ENVIRONMENT=production
heroku config:set GITHUB_API_KEY=your_token_here

# Deploy
git push heroku main

# Open app
heroku open
```

#### B. Railway.app

1. Visit https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add PostgreSQL and Redis services
5. Set environment variables in dashboard
6. Deploy automatically on git push

#### C. Render.com

1. Visit https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL and Redis services
6. Set environment variables
7. Deploy

---

### Option 3: Kubernetes (Enterprise Scale)

**Best for:** Large deployments, high availability, auto-scaling  
**Time:** 2-4 hours  
**Cost:** $100+/month

#### Prerequisites:
- Kubernetes cluster (EKS, GKE, AKS, or self-hosted)
- `kubectl` CLI installed
- Docker images pushed to registry

#### Steps:

1. **Build and push images:**
```bash
# Backend
docker build -t yourusername/resume-verify-backend:latest ./backend
docker push yourusername/resume-verify-backend:latest

# Frontend
docker build -t yourusername/resume-verify-frontend:latest ./frontend
docker push yourusername/resume-verify-frontend:latest
```

2. **Create Kubernetes manifests** (see `k8s/` folder)

3. **Deploy:**
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

4. **Set up ingress controller and SSL:**
```bash
# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply certificate issuer
kubectl apply -f k8s/certificate-issuer.yaml
```

---

### Option 4: AWS (Full Production)

**Best for:** Enterprise deployments, compliance requirements  
**Time:** 3-5 hours  
**Cost:** $200+/month

#### Architecture:
- **ECS Fargate**: Container hosting
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed cache
- **S3**: File storage
- **CloudFront**: CDN
- **ALB**: Load balancer
- **Route 53**: DNS
- **ACM**: SSL certificates

#### Setup Guide:

1. **Create VPC and subnets**
2. **Set up RDS PostgreSQL instance**
3. **Create ElastiCache Redis cluster**
4. **Create S3 bucket for resume storage**
5. **Create ECS cluster and task definitions**
6. **Set up Application Load Balancer**
7. **Configure Auto Scaling**
8. **Set up CloudWatch monitoring**
9. **Configure CloudFront for frontend**

*Detailed AWS setup guide available in `docs/aws-deployment.md`*

---

## 🔒 Security Hardening

### Environment Variables
```bash
# Generate all secrets securely
JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Set in production environment
export JWT_SECRET=$JWT_SECRET
export SECRET_KEY=$SECRET_KEY
```

### Database
- Use managed service (RDS, managed PostgreSQL)
- Enable SSL/TLS connections
- Regular automated backups
- Use connection pooling
- Set up read replicas for scaling

### API Keys
- Use environment variables, never hardcode
- Rotate keys regularly
- Use least-privilege access
- Monitor API usage

### Firewall Rules
```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

### SSL/TLS
```bash
# Let's Encrypt (free)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://yourdomain.com/api/health

# Expected response:
{"status": "healthy", "version": "1.0.0"}
```

### Logs
```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend
```

### Monitoring Tools
- **Sentry**: Error tracking
- **DataDog**: Infrastructure monitoring
- **Prometheus + Grafana**: Metrics and dashboards
- **CloudWatch**: AWS native monitoring

### Backup Strategy
```bash
# Database backup
pg_dump -h your-db-host -U postgres resume_verify > backup.sql

# Automated with cron
0 2 * * * /usr/local/bin/backup-script.sh
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to server
        run: |
          ssh user@your-server 'cd /app && git pull && docker-compose up -d --build'
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection failed → Check DATABASE_URL
# - Port already in use → Change port mapping
# - Missing dependencies → Rebuild: docker-compose build --no-cache
```

### Frontend won't load
```bash
# Check if backend is accessible
curl http://localhost:8000/api/health

# Check CORS settings in backend/main.py
# Ensure ALLOWED_ORIGINS includes your frontend URL
```

### Database connection errors
```bash
# Test connection
psql -h your-db-host -U postgres -d resume_verify

# Check if database exists
psql -h your-db-host -U postgres -l
```

### High memory usage
```bash
# Check container stats
docker stats

# Limit resources in docker-compose.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## 📈 Performance Optimization

### Backend
- Enable connection pooling
- Use Redis for caching
- Implement rate limiting
- Optimize database queries
- Use async processing with Celery

### Frontend
- Enable gzip compression (nginx)
- Use CDN for static assets
- Implement code splitting
- Optimize images
- Enable browser caching

### Database
- Create indexes on frequently queried columns
- Use connection pooling (pgbouncer)
- Monitor slow queries
- Regular VACUUM and ANALYZE

---

## 📞 Support Resources

- **Documentation**: See `DOCUMENTATION_INDEX.md`
- **API Reference**: http://yourdomain.com/api/docs
- **GitHub Issues**: Report bugs and issues
- **Community**: Join our Discord/Slack

---

## ✅ Post-Deployment Verification

Run these checks after deployment:

```bash
# 1. Health check
curl https://yourdomain.com/api/health

# 2. User registration
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# 3. Login
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# 4. Load test (optional)
ab -n 1000 -c 10 https://yourdomain.com/api/health
```

---

## 🎉 You're Live!

Congratulations! Your Resume Verification System is now deployed and running in production.

**Next Steps:**
- Monitor logs and metrics
- Set up alerts for errors
- Regular security updates
- Scale as needed

**Happy deploying! 🚀**
