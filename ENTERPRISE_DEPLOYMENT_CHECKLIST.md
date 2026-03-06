# Enterprise Upgrade - Deployment Checklist

## Pre-Deployment Verification

### Code Files ✓
```
backend/
  ├─ security/
  │  ├─ auth.py                 (450+ lines) - JWT + RBAC
  │  ├─ encryption.py           (250+ lines) - AES-256 encryption
  │  └─ __init__.py             - Module exports
  ├─ services/
  │  ├─ vector_search.py        (450+ lines) - Pinecone integration
  │  ├─ kafka_producer.py       (550+ lines) - Event streaming
  │  └─ blockchain_service.py   (250+ lines) - UPGRADED with NFT
  ├─ workers/
  │  ├─ verification_worker.py  (150+ lines) - Resume verification
  │  └─ blockchain_worker.py    (150+ lines) - Blockchain writes
  ├─ api/
  │  └─ ai_routes.py            (400+ lines) - AI endpoints
  ├─ load_test.py               (300+ lines) - Load testing
  └─ requirements.txt           (UPDATED with 30+ packages)

blockchain/
  ├─ VerifiedResumeNFT.sol      (300+ lines) - ERC-721 contract
  └─ ResumeVerificationRegistry.sol (existing)

root/
  ├─ RESEARCH_PAPER.md                      (4200+ words)
  ├─ DEPLOYMENT_GUIDE_ENTERPRISE.md         (2000+ lines)
  ├─ ARCHITECTURE_DIAGRAMS.md               (1200+ lines)
  ├─ ENTERPRISE_UPGRADE_SUMMARY.md          (this file ref)
  └─ docker-compose.enterprise.yml          (400+ lines)
```

### Verification Steps

#### Step 1: Check File Existence
- [ ] `backend/security/auth.py` exists (350+ lines)
- [ ] `backend/security/encryption.py` exists (250+ lines)
- [ ] `backend/services/vector_search.py` exists (450+ lines)
- [ ] `backend/services/kafka_producer.py` exists (550+ lines)
- [ ] `backend/workers/verification_worker.py` exists (150+ lines)
- [ ] `backend/workers/blockchain_worker.py` exists (150+ lines)
- [ ] `backend/api/ai_routes.py` exists (400+ lines)
- [ ] `blockchain/VerifiedResumeNFT.sol` exists (300+ lines)
- [ ] `backend/requirements.txt` has 30+ new packages
- [ ] `docker-compose.enterprise.yml` exists (400+ lines)

#### Step 2: Verify Code Quality
```bash
# Check Python syntax
python -m py_compile backend/security/auth.py
python -m py_compile backend/security/encryption.py
python -m py_compile backend/services/vector_search.py
python -m py_compile backend/services/kafka_producer.py
python -m py_compile backend/workers/verification_worker.py
python -m py_compile backend/workers/blockchain_worker.py
python -m py_compile backend/api/ai_routes.py
python -m py_compile backend/load_test.py

# Check imports
grep -n "from fastapi import" backend/api/ai_routes.py
grep -n "from cryptography" backend/security/encryption.py
grep -n "from kafka import" backend/services/kafka_producer.py
grep -n "from pinecone import" backend/services/vector_search.py
```

#### Step 3: Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Verify key packages
pip show fastapi
pip show pyjwt
pip show cryptography
pip show kafka-python
pip show pinecone
pip show web3
pip show locust
```

#### Step 4: Database Migration (if integrating)
```bash
# Initialize alembic (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Enterprise upgrade"

# Review migration file: alembic/versions/

# Apply migration
alembic upgrade head
```

#### Step 5: Docker Infrastructure
```bash
# Start services
docker-compose -f docker-compose.enterprise.yml up -d

# Verify all services running
docker-compose -f docker-compose.enterprise.yml ps

# Expected services (12 total):
# - postgres (healthy)
# - redis (healthy)
# - zookeeper (healthy)
# - kafka (healthy)
# - api (healthy)
# - worker-verification (healthy)
# - worker-blockchain (healthy)
# - frontend (healthy)
# - prometheus (healthy)
# - grafana (healthy)
# - nginx (healthy)
# - pgadmin (healthy)
# - adminer (healthy)
# - kafdrop (healthy)
```

#### Step 6: API Verification
```bash
# Test API health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
# or
curl http://localhost:8000/openapi.json | jq .

# Test AI endpoints signature
curl -X GET http://localhost:8000/api/ai/health

# Expected: 200 OK with version info
```

#### Step 7: Blockchain Setup (if using Polygon)
```bash
# Compile smart contracts
cd blockchain
npx hardhat compile

# Expected output: Compiled 2 Solidity files successfully

# Test deployment (testnet first)
npx hardhat run scripts/deploy.js --network mumbai

# Note contract addresses, update .env:
# SMART_CONTRACT_ADDRESS=0x...
# NFT_CONTRACT_ADDRESS=0x...
```

#### Step 8: Load Testing
```bash
# Start Locust web UI
locust -f backend/load_test.py --host=http://localhost:8000 --web

# Or run headless
locust -f backend/load_test.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless

# Expected: 2000+ req/sec, <5% error rate
```

#### Step 9: Security Verification
```bash
# Check JWT token generation
python -c "
from backend.security.auth import JWTManager
jwt_mgr = JWTManager()
token = jwt_mgr.create_access_token(sub='test@example.com', role='admin')
print(f'Access Token: {token[:50]}...')
"

# Check encryption
python -c "
from backend.security.encryption import EncryptionManager
enc_mgr = EncryptionManager()
encrypted = enc_mgr.encrypt('secret data')
decrypted = enc_mgr.decrypt(encrypted)
print(f'Encryption test: {'PASS' if decrypted == 'secret data' else 'FAIL'}')"
```

#### Step 10: Monitoring Dashboard
```bash
# Access Grafana
open http://localhost:3001

# Login: admin / admin

# Import dashboards:
# 1. API Performance Dashboard
# 2. ML Pipeline Metrics
# 3. Blockchain Status
# 4. System Health

# Key metrics to check:
# - Request latency (p50, p95, p99)
# - Throughput (req/sec)
# - Error rate (%)
# - Kafka lag
# - Vector DB latency
# - Blockchain write time
```

---

## Deployment Workflows

### Local Development (5 Terminals)

**Terminal 1: Data Services**
```bash
docker-compose -f docker-compose.enterprise.yml up -d postgres redis kafka zookeeper
```

**Terminal 2: Backend API**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3: Verification Worker**
```bash
cd backend
python -m workers.verification_worker
```

**Terminal 4: Blockchain Worker**
```bash
cd backend
python -m workers.blockchain_worker
```

**Terminal 5: Frontend**
```bash
cd frontend
npm install
npm run dev  # Vite on :3000
```

### Production Deployment (Docker Compose)

```bash
# Build all images
docker-compose -f docker-compose.enterprise.yml build

# Start all services
docker-compose -f docker-compose.enterprise.yml up -d

# Check logs
docker-compose -f docker-compose.enterprise.yml logs -f

# Scale workers
docker-compose -f docker-compose.enterprise.yml up -d --scale worker-verification=3

# Stop all
docker-compose -f docker-compose.enterprise.yml down
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace resume-verify

# Deploy all resources
kubectl apply -f k8s/ -n resume-verify

# Check deployments
kubectl get deployments -n resume-verify

# View pods
kubectl get pods -n resume-verify

# Access API (port-forward)
kubectl port-forward svc/api 8000:8000 -n resume-verify

# Scale workers
kubectl scale deployment worker-verification --replicas=3 -n resume-verify

# View logs
kubectl logs -f deployment/api -n resume-verify
```

---

## Common Issues & Solutions

### Issue: Kafka Connection Error
```
Error: [Errno 111] Connection refused
```
**Solution:**
```bash
# Ensure Kafka is running
docker-compose -f docker-compose.enterprise.yml up -d kafka zookeeper

# Wait 15 seconds for Kafka to start
sleep 15

# Verify Kafka
docker-compose exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### Issue: Pinecone Connection Failed
```
Error: Invalid Pinecone API Key
```
**Solution:**
```bash
# Check .env has PINECONE_API_KEY
grep PINECONE_API_KEY .env

# Get key from https://www.pinecone.io
# Update .env and restart

docker-compose -f docker-compose.enterprise.yml restart api
```

### Issue: Smart Contract Deployment Failed
```
Error: PRIVATE_KEY not set
```
**Solution:**
```bash
# Check .env has valid private key
grep PRIVATE_KEY .env

# Format: Must be 64 hex characters (0x prefix not required)
# Example: f1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Ensure account has ETH for gas
# Polygon Mumbai testnet: https://faucet.polygon.technology/
```

### Issue: Vector DB Query Timeout
```
Error: Pinecone query exceeded timeout
```
**Solution:**
- Reduce query vector dimensions
- Set smaller top_k (10 → 5)
- Remove filters / simplify queries
- Check Pinecone quota status

### Issue: High Error Rate in Load Test
```
Error: >5% failed requests
```
**Solution:**
```bash
# Check API logs
docker-compose -f docker-compose.enterprise.yml logs api

# Check Kafka lag
docker-compose exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group resume-verification-group \
  --describe

# Scale up workers
docker-compose -f docker-compose.enterprise.yml up -d --scale worker-verification=5

# Reduce concurrent users in Locust
```

---

## Success Criteria Checklist

- [ ] All 12 services healthy (docker-compose ps)
- [ ] API responds to /health endpoint
- [ ] JWT tokens can be generated & validated
- [ ] Kafka topics created (8 topics)
- [ ] Vector DB connection established
- [ ] Smart contracts compiled & deployed
- [ ] Load test achieves >1000 req/sec
- [ ] Error rate <1%
- [ ] Latency p95 <10 seconds
- [ ] Grafana dashboards show metrics
- [ ] Security headers present (curl -I http://localhost:8000)
- [ ] CORS configured for frontend
- [ ] Database has all tables (select * from information_schema.tables)
- [ ] SSL/TLS ready (cert files present)

---

## Quick Links

- **API Docs:** http://localhost:8000/docs
- **Grafana Metrics:** http://localhost:3001 (admin/admin)
- **Kafka UI:** http://localhost:9001 (Kafdrop)
- **Database Admin:** http://localhost:5050 (pgadmin) or http://localhost:8080 (Adminer)
- **Research Paper:** See `RESEARCH_PAPER.md`
- **Deployment Guide:** See `DEPLOYMENT_GUIDE_ENTERPRISE.md`
- **Architecture:** See `ARCHITECTURE_DIAGRAMS.md`

---

## Contact & Support

For issues with:
- **FastAPI/Python:** Check `backend/main.py` and raise issues with stack trace
- **Kafka:** Check `DEPLOYMENT_GUIDE_ENTERPRISE.md` Kafka section
- **Blockchain:** Check `blockchain/` folder and `blockchain_service.py`
- **Vector DB:** Check Pinecone dashboard at https://console.pinecone.io
- **Docker:** Check docker-compose logs with `docker logs container_name`

---

**Status:** ✅ Ready for Deployment
**Last Updated:** March 6, 2026
**Version:** Enterprise 1.0
