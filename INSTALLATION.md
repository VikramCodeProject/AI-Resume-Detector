# Resume Truth Verification System - Installation & Setup Guide

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone & Setup

```bash
git clone <repo-url>
cd UsMiniProject
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your settings:

```bash
# Backend
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/resume_verify
REDIS_URL=redis://redis:6379
JWT_SECRET=your-secret-key-change-in-production

# APIs
GITHUB_API_KEY=your_github_token
LINKEDIN_API_KEY=your_linkedin_token

# Blockchain
ETH_RPC_URL=https://polygon-rpc.com
SMART_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=your_private_key
```

### 3. Start Services

```bash
# Using Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

---

## Full Development Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### ML Engine Setup

```bash
# Install ML dependencies
cd ml_engine
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# (Optional) Train custom models
python train_models.py
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start  # Runs on http://localhost:3000

# Build for production
npm run build
```

### Blockchain Setup

```bash
# Navigate to blockchain
cd blockchain

# Install Hardhat
npm install -g hardhat

# Compile contracts
hardhat compile

# Deploy to testnet
hardhat run scripts/deploy.js --network polygon-mumbai
```

---

## Database Setup

### PostgreSQL Initialization

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE resume_verify;
CREATE USER app_user WITH PASSWORD 'secure_password';
ALTER ROLE app_user SET client_encoding TO 'utf8';
ALTER ROLE app_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE app_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE resume_verify TO app_user;
\q

# Run migrations
cd backend
alembic upgrade head
```

### Redis Setup

```bash
# Start Redis
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:7
```

---

## API Usage Examples

### 1. User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "John Doe",
    "gdpr_consent": true
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### 3. Upload Resume

```bash
curl -X POST http://localhost:8000/api/resumes/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/resume.pdf"
```

### 4. Get Resume Details

```bash
curl http://localhost:8000/api/resumes/resume-123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Get Trust Score

```bash
curl http://localhost:8000/api/resumes/resume-123/trust-score \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## ML Model Training

### Prepare Training Data

```python
# Create dataset with labeled claims
# Format: CSV with columns: claim_text, claim_type, label (verified/doubtful/fake)

python ml_engine/prepare_data.py --input raw_data.csv --output processed_data.csv
```

### Train Models

```bash
cd ml_engine

# Train XGBoost classifier
python train_models.py \
  --model xgboost \
  --data processed_data.csv \
  --output_path ./models/xgboost_v1.pkl

# Train neural network
python train_models.py \
  --model neural_network \
  --data processed_data.csv \
  --output_path ./models/nn_v1.h5
```

### Evaluate Models

```bash
python evaluate_models.py \
  --model_path ./models/xgboost_v1.pkl \
  --test_data test_set.csv
```

---

## Blockchain Deployment

### Deploy Smart Contract

```bash
# Using Hardhat
cd blockchain

# Compile
npx hardhat compile

# Deploy to Polygon Mumbai testnet
npx hardhat run scripts/deploy.js --network mumbai

# Deploy to Ethereum mainnet
npx hardhat run scripts/deploy.js --network mainnet
```

### Verify Contract on Explorer

```bash
# Verify on Polygonscan
npx hardhat verify --network mumbai CONTRACT_ADDRESS

# Example
npx hardhat verify --network mumbai 0x1234...5678
```

### Interact with Contract

```python
from blockchain.blockchain_service import BlockchainServiceFactory

# Create service
service = BlockchainServiceFactory.create_service(network="polygon")

# Register claim
tx_hash = service.register_claim(
    claim_hash="0x...",
    trust_score=85,
    claim_text="Python",
    resume_hash="0x..."
)

# Verify claim
result = service.verify_claim("0x...")
print(result)

# Get statistics
stats = service.get_statistics()
print(stats)
```

---

## Testing

### Unit Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# ML pipeline tests
cd ml_engine
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Integration Tests

```bash
# End-to-end tests
pytest tests/integration/test_resume_flow.py -v
```

### Load Testing

```bash
# Using Apache JMeter or Locust
locust -f tests/load/locustfile.py -u 1000 -r 100 --headless -t 5m
```

---

## Production Deployment

### Docker Build

```bash
# Build backend image
docker build -t resume-verify-backend:1.0 ./backend

# Build frontend image
docker build -t resume-verify-frontend:1.0 ./frontend

# Push to registry
docker tag resume-verify-backend:1.0 your-registry/resume-verify-backend:1.0
docker push your-registry/resume-verify-backend:1.0
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace resume-verify

# Deploy services
kubectl apply -f k8s/postgres.yaml -n resume-verify
kubectl apply -f k8s/redis.yaml -n resume-verify
kubectl apply -f k8s/backend.yaml -n resume-verify
kubectl apply -f k8s/frontend.yaml -n resume-verify

# Check status
kubectl get pods -n resume-verify
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name resumeverify.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name resumeverify.com;

    ssl_certificate /etc/letsencrypt/live/resumeverify.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/resumeverify.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Environment Variables Reference

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |
| `JWT_SECRET` | `your-secret-key` | JWT signing key |
| `GITHUB_API_KEY` | `ghp_...` | GitHub personal access token |
| `ETH_RPC_URL` | `https://polygon-rpc.com` | Blockchain RPC endpoint |
| `SMART_CONTRACT_ADDRESS` | `0x...` | Deployed contract address |
| `PRIVATE_KEY` | `0x...` | Private key for transactions |
| `AWS_S3_BUCKET` | `resume-verify-prod` | S3 bucket name |
| `ENVIRONMENT` | `production` | Deployment environment |

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL
psql -U postgres -h localhost -d resume_verify

# Reset database
cd backend
alembic downgrade base
alembic upgrade head
```

### Redis Connection Issues

```bash
# Check Redis
redis-cli ping

# Clear cache
redis-cli FLUSHALL
```

### API Errors

```bash
# Check backend logs
docker logs resume-verify-backend

# View API documentation
http://localhost:8000/api/docs
```

### ML Model Issues

```bash
# Verify spaCy model
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"

# Check model files
ls -la ml_engine/models/
```

---

## Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_resume_user_id ON resumes(user_id);
CREATE INDEX idx_claim_resume_id ON claims(resume_id);
CREATE INDEX idx_verification_claim_id ON verifications(claim_id);

-- Enable connection pooling
-- In backend: use pgBouncer or SQLAlchemy connection pool
```

### Caching Strategy

```python
# Redis caching for API responses
from functools import wraps
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def cached(timeout=3600):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            result = cache.get(key)
            if result:
                return json.loads(result)
            result = await f(*args, **kwargs)
            cache.setex(key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### ML Model Optimization

```python
# Use model quantization
from onnx_tf.backend import prepare
# Convert to ONNX for faster inference
```

---

## Monitoring & Logging

### Application Monitoring

```bash
# Using Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Grafana dashboards
docker run -d -p 3000:3000 grafana/grafana
```

### Centralized Logging

```bash
# Using ELK Stack
docker-compose -f docker-compose.elk.yml up -d

# View logs
# Kibana: http://localhost:5601
```

---

## Support & Documentation

- **API Documentation:** http://localhost:8000/api/docs
- **GitHub Issues:** [Create an issue](https://github.com/your-repo/issues)
- **Discussion Forum:** [GitHub Discussions](https://github.com/your-repo/discussions)

For more information, see [ARCHITECTURE.md](ARCHITECTURE.md) and [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md).
