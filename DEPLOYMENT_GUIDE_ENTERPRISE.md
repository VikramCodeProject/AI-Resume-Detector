# Enterprise Resume Verification Platform - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Blockchain Setup](#blockchain-setup)
6. [Production Configuration](#production-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

```bash
# Core
- Docker :>=20.10
- Docker Compose >=1.29
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

# Optional (for production)
- Kubernetes 1.25+
- Helm 3.0+
- AWS CLI / Azure CLI
- Polygon RPC endpoint
- Pinecone API account
- GitHub/LinkedIn API keys
```

### Environment Variables

Create `.env` file in project root:

```bash
# ===== CORE APPLICATION =====
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# ===== DATABASE =====
DATABASE_URL=postgresql://postgres:secure_password@postgres:5432/resume_verify
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# ===== REDIS & CACHE =====
REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600

# ===== JWT & SECURITY =====
JWT_SECRET=your-secret-key-min-32-chars-production-only
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7
ENCRYPTION_KEY=encryption-key-min-32-chars production-only

# ===== EXTERNAL APIs =====
GITHUB_API_KEY=ghp_xxxxxxxxxxxxxxxxxxxx
LINKEDIN_API_KEY=your-linkedin-token
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx

# ===== VECTOR DATABASE (Pinecone) =====
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=resume-verification

# ===== EVENT STREAMING (Kafka) =====
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_COMPRESSION_TYPE=snappy

# ===== BLOCKCHAIN =====
ETH_RPC_URL=https://polygon-rpc.com
BLOCKCHAIN_NETWORK=polygon
SMART_CONTRACT_ADDRESS=0x...
NFT_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...  # DO NOT COMMIT IN PRODUCTION
GAS_PRICE_GWEI=150

# ===== AWS S3 (Resume Storage) =====
AWS_S3_BUCKET=resume-verify-prod
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# ===== FRONTEND =====
FRONTEND_URL=https://app.example.com
VITE_API_URL=https://api.example.com
VITE_API_TIMEOUT=30000

# ===== MONITORING =====
PROMETHEUS_PORT=9090
GRAFANA_PASSWORD=secure_password

# ===== RATE LIMITING =====
RATE_LIMIT=10/minute
MAX_UPLOAD_SIZE_MB=10
MAX_RESUMES_PER_USER=50
```

---

## Local Development Setup

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/resume-verification.git
cd resume-verification

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2. Start Local Services

```bash
# Terminal 1: PostgreSQL + Redis + Kafka
docker-compose up -d postgres redis kafka

# Wait for services to start
sleep 10

# Terminal 2: FastAPI Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Verification Worker
python workers/verification_worker.py

# Terminal 4: Blockchain Worker
python workers/blockchain_worker.py

# Terminal 5: React Frontend
cd frontend
npm run dev

# Terminal 6: Celery Worker (optional)
celery -A tasks worker --loglevel=info
```

### 3. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:5173
```

---

## Docker Deployment

### 1. Build Docker Images

```bash
# Backend
docker build -t resume-verify-backend:latest -f backend/Dockerfile backend/

# Frontend
docker build -t resume-verify-frontend:latest -f frontend/Dockerfile frontend/

# Tag for registry
docker tag resume-verify-backend:latest gcr.io/your-project/resume-verify-backend:latest
docker tag resume-verify-frontend:latest gcr.io/your-project/resume-verify-frontend:latest
```

### 2. Push to Registry

```bash
# Google Cloud
gcloud auth configure-docker
docker push gcr.io/your-project/resume-verify-backend:latest
docker push gcr.io/your-project/resume-verify-frontend:latest

# Or AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag resume-verify-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/resume-verify-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/resume-verify-backend:latest
```

### 3. Deploy with Docker Compose

```bash
docker-compose -f docker-compose.production.yaml up -d

# View logs
docker-compose logs -f backend

# Scale services
docker-compose up -d --scale api=3 --scale worker-verification=3 --scale worker-blockchain=2
```

---

## Kubernetes Deployment

### 1. Create Kubernetes Manifest

**k8s/backend-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-verify-backend
  labels:
    app: resume-verify
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      component: backend
  template:
    metadata:
      labels:
        component: backend
    spec:
      containers:
      - name: api
        image: gcr.io/your-project/resume-verify-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-secret
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: resume-verify-backend
spec:
  selector:
    component: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 2. Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace resume-verify

# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=redis-url=$REDIS_URL \
  --from-literal=jwt-secret=$JWT_SECRET \
  -n resume-verify

# Deploy
kubectl apply -f k8s/ -n resume-verify

# Verify
kubectl get pods -n resume-verify
kubectl get svc -n resume-verify

# View logs
kubectl logs -f deployment/resume-verify-backend -n resume-verify
```

### 3. Auto-Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resume-verify-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Blockchain Setup

### 1. Deploy Smart Contracts

```bash
# Install Hardhat
npm install --save-dev hardhat @openzeppelin/contracts

# Compile
npx hardhat compile

# Test
npx hardhat test

# Deploy to Polygon Testnet
npx hardhat run scripts/deploy.js --network mumbai

# Deploy to Polygon Mainnet
npx hardhat run scripts/deploy.js --network polygon
```

### 2. Verify on PolygonoScan

```bash
# Flatten contract
npx hardhat flatten blockchain/ResumeVerificationRegistry.sol > Flattened.sol

# Verify
npx hardhat verify \
  --network polygon \
  --contract contracts/ResumeVerificationRegistry.sol:ResumeVerificationRegistry \
  ADDRESS_FROM_DEPLOYMENT
```

### 3. Update .env with Contract Addresses

```bash
SMART_CONTRACT_ADDRESS=0x...
NFT_CONTRACT_ADDRESS=0x...
```

---

## Production Configuration

### 1. SSL/TLS Certificate

```bash
# Using Let's Encrypt with Certbot
certbot certonly --standalone -d api.example.com -d app.example.com

# Or use AWS Certificate Manager
aws acm request-certificate --domain-name api.example.com
```

### 2. Nginx Reverse Proxy

**nginx.conf:**

```nginx
upstream backend {
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Database Backup

```bash
# Automated daily backup
0 2 * * * pg_dump -U postgres resume_verify | gzip > /backups/resume_verify_$(date +\%Y\%m\%d).sql.gz

# Store in S3
aws s3 sync /backups s3://resume-verify-backups/
```

### 4. CDN Configuration (CloudFlare)

```
- DNS: Point api.example.com to Nginx server
- SSL: Full (strict)
- Cache: Aggressive for static assets
- Rate Limit: 10 requests/second
- Web Application Firewall: Enable OWASP rules
```

---

## Monitoring & Logging

### 1. Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['localhost:8000']
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
  - job_name: 'kafka'
    static_configs:
      - targets: ['localhost:9308']
```

### 2. Grafana Dashboards

Key metrics to monitor:

```
- API Response Latency (p50, p95, p99)
- Error Rate (5xx, 4xx)
- Throughput (req/sec)
- Worker Queue Depth
- Database Connection Pool
- Cache Hit Rate
- Blockchain Gas Used
- Vector DB Query Time
```

### 3. Centralized Logging (ELK Stack)

```bash
# Shipping logs to Elasticsearch
# In main.py:
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Logstash pipeline:
input {
  docker {
    host => "unix:///var/run/docker.sock"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "resume-verify-%{+YYYY.MM.dd}"
  }
}
```

### 4. Alerting Rules

```yaml
# alert.rules.yml
groups:
  - name: resume_verify
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"
        
    - alert: SlowVerification
      expr: histogram_quantile(0.95, verification_time) > 5000
      for: 10m
      annotations:
        summary: "Verification latency high"
        
    - alert: KafkaLag
      expr: kafka_consumer_lag > 10000
      for: 5m
      annotations:
        summary: "Kafka consumer lagging"
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Timeout**

```bash
# Check PostgreSQL
docker logs postgres

# Verify connection string
psql $DATABASE_URL -c "SELECT 1"

# Restart container with increased resources
docker-compose restart postgres
```

**2. Kafka Topic Missing**

```bash
# List topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Create topic
docker exec kafka kafka-topics --create --topic resume-upload-topic \
  --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

**3. Blockchain Transaction Failure**

```bash
# Check gas price
curl https://polygon-rpc.com \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0", "method":"eth_gasPrice", "params":[], "id":1}'

# Increase gas price in config
GAS_PRICE_GWEI=200
```

**4. Vector DB Connection Error**

```bash
# Test Pinecone connection
from pinecone import init
init(api_key="YOUR_KEY", environment="us-east-1")
index = Index("resume-verification")
index.describe_index_stats()
```

### Performance Tuning

```bash
# Increase PostgreSQL connections
shared_buffers = 256MB
max_connections = 100

# Optimize Redis
maxmemory 512mb
maxmemory-policy allkeys-lru

# Increase Kafka throughput
num.network.threads=8
num.io.threads=8
socket.send.buffer.bytes=102400
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Set strong JWT_SECRET (32+ chars, random)
- [ ] Enable SSL/TLS for all endpoints
- [ ] Configure CORS only for trusted domains
- [ ] Set up database backups (daily, encrypted)
- [ ] Enable audit logging for all modifications
- [ ] Configure rate limiting
- [ ] Set up intrusion detection (Fail2ban)
- [ ] Regular security scanning (Trivy, SonarQube)
- [ ] Rotate API keys monthly
- [ ] Implement GDPR data deletio process
- [ ] Test disaster recovery plan quarterly

---

## Support & Documentation

- API Docs: https://api.example.com/docs
- Architecture: See ARCHITECTURE.md
- Research Paper: See RESEARCH_PAPER.md
- Issues: GitHub Issues
- Email: support@example.com

