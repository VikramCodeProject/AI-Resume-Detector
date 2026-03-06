# System Architecture Diagrams

## 1. High-Level Enterprise Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL WORLD                                 │
├────────────────────────────────────────────────────────────────────────────┤
│  GitHub API  │  LinkedIn API  │  Certificate Issuers  │  Polygon Blockchain │
└────────────────────┬──────────────────────────────────┬──────────────────────┘
                     │                                  │
                     │         HTTPS/TLS                │
                     ▼                                  ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           CDN / DDoS PROTECTION                             │
│                        (CloudFlare / AWS Shield)                            │
└────────────────────┬──────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER (Nginx / HAProxy)                        │
├────────────────────────────────────────────────────────────────────────────┤
│  - TLS Termination     - Rate Limiting (10 req/s)   - CORS Validation      │
│  - Health Checks       - Request Logging            - DDoS Mitigation      │
└────────────────────┬──────────────────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ API Pod │ │ API Pod │ │ API Pod │  (Scale 2-20 pods)
    │  (8000) │ │  (8000) │ │  (8000) │  - Auto-scaling: CPU/Memory thresholds
    └─────────┘ └─────────┘ └─────────┘  - Rolling updates: 0-downtime deployments
         │────────────┬────────────│
         │            │            │
         ▼            ▼            ▼
    ┌─────────────────────────────────────────┐
    │     FASTAPI APPLICATION SERVER          │
    ├─────────────────────────────────────────┤
    │  - Authentication (JWT + RBAC)          │
    │  - Rate Limiting (SLowAPI)              │
    │  - Request Validation (Pydantic)        │
    │  - Gzip Compression                     │
    │  - CORS Headers                         │
    │  - OpenAPI Documentation                │
    └─────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
  API         SERVICE         WORKER
  ROUTES      LAYER           QUEUE
  
  ├─ POST      ├─ Vector     ├─ Kafka
  │ /resume/   │  Search       Producer
  │ upload     │              │
  │            ├─ Blockchain  ├─ Event
  ├─ GET       │  Service     │  Publishing
  │ /resume/   │              │
  │ {id}       ├─ GitHub      └─ Async
  │            │  Analyzer     Processing
  │ /ai/       │              
  │ similarity ├─ OCR        
  │            │  Service     
  └─ POST      │              
    /ai/nft    ├─ Encryption  
    -cert      │  Manager     
               │              
               └─ LLM Service 
```

## 2. Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION LAYER                            │
├──────────────────────────────────────────────────────────────────────┤
│  React Frontend (3000)  │  Mobile App  │  Third-party API Clients   │
└──────────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS
                           ▼
         ┌─────────────────────────────────────┐
         │   API Gateway (FastAPI + Nginx)     │
         ├─────────────────────────────────────┤
         │ - Authentication (JWT Verify)       │
         │ - Authorization (RBAC Check)        │
         │ - Rate Limiting                     │
         └─────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   ┌──────────┐      ┌──────────┐     ┌──────────┐
   │ UPLOAD   │      │VERIFY    │     │ QUERY    │
   │ HANDLER  │      │HANDLER   │     │HANDLER   │
   └────┬─────┘      └────┬─────┘     └────┬─────┘
        │                 │                 │
        │ Validate        │                 │ Get from
        │ & Encrypt       │                 │ PostgreSQL
        │                 │                 │  or Cache
        ▼                 ▼                 ▼
    ┌────────────────────────────────────────┐
    │  S3 (Resume Storage)                   │
    │  - Encrypted at rest (AES-256)         │
    │  - Versioning enabled                  │
    │  - Access via presigned URLs           │
    └────────────────────────────────────────┘
         │
         │ Publish event
         ▼
    ┌────────────────────────────────────────┐
    │  KAFKA (Event Bus)                     │
    ├────────────────────────────────────────┤
    │  resume_uploaded_topic                 │
    │  ├─ Partition 1 (resumes 0-33%)        │
    │  ├─ Partition 2 (resumes 33-66%)       │
    │  └─ Partition 3 (resumes 66-100%)      │
    └─┬──┬──┬──────────────────────────────────┘
      │  │  │
      │  │  └─ Retention: 30 days
      │  │  └─ Replication: 1
      │  │  └─ Compression: Snappy
      │  │
   ┌──▼──▼──▼──────────────────────────────┐
   │  CONSUMER GROUPS                       │
   ├────────────────────────────────────────┤
   │  verification-group:                   │
   │    ├─ Verification Worker 1            │
   │    ├─ Verification Worker 2            │
   │    └─ Verification Worker N            │
   │                                        │
   │  blockchain-group:                     │
   │    ├─ Blockchain Worker 1              │
   │    └─ Blockchain Worker 2              │
   └─┬────────────────────────────────────┘
     │
     ├─ Parallel Processing
     ├─ Horizontal Scaling
     ├─ Auto-Commit Offsets
     └─ Fault Tolerance
     
     ▼ (Each Worker)
   ┌──────────────────────────────────────┐
   │  VERIFICATION PIPELINE                │
   ├──────────────────────────────────────┤
   │  1. Resume Parsing (PyPDF2)           │
   │  2. Claim Extraction (SpaCy + BERT)   │
   │  3. Parallel Verification:            │
   │     ├─ GitHub Analysis                │
   │     ├─ LinkedIn Matching              │
   │     ├─ Certificate OCR                │
   │     ├─ Timeline Validation            │
   │     └─ Skill Assessment               │
   │  4. Feature Engineering               │
   │  5. ML Classification (XGBoost)       │
   │  6. SHAP Explanation                  │
   └──────────┬──────────────────────────┘
              │
              │ Write results
              ▼
         ┌─────────────────────────────┐
         │  PostgreSQL Database        │
         ├─────────────────────────────┤
         │  Tables:                    │
         │  - users (authentication)   │
         │  - resumes (stored PDFs)    │
         │  - claims (extracted data)  │
         │  - verifications (results)  │
         │  - blockchain_records(hashes)
         │  - audit_logs (GDPR)        │
         └──────────┬──────────────────┘
                    │
                    │ Also update cache
                    ▼
              ┌────────────────┐
              │ Redis Cache    │
              ├────────────────┤
              │ Keys:          │
              │ user:{id}      │
              │ resume:{id}    │
              │ verify:{id}    │
              │ TTL: 3600 sec  │
              └────────────────┘
     
     ▼ (Blockchain Worker)
   ┌──────────────────────────────────────┐
   │  BLOCKCHAIN INTEGRATION               │
   ├──────────────────────────────────────┤
   │  1. Calculate SHA-256 hash            │
   │  2. Create transaction:               │
   │     - storeResumeHash()               │
   │     - mintVerifiedResumeNFT()         │
   │  3. Sign with private key             │
   │  4. Send to Polygon RPC               │
   │  5. Wait for confirmation (256 blocks)│
   │  6. Store tx_hash in DB               │
   └──────────────────────────────────────┘
              │
              ▼
         ┌─────────────────────────────┐
         │  Polygon Blockchain         │
         ├─────────────────────────────┤
         │  ResumeVerificationRegistry │
         │  ├─ Immutable records       │
         │  ├─ Gas: $0.01-0.05 per tx  │
         │  └─ Finality: 2 seconds     │
         │                             │
         │  VerifiedResumeNFT          │
         │  ├─ ERC-721 certificates    │
         │  ├─ transferable            │
         │  └─ queryable on OpenSea    │
         └────────────────────────────┘
```

## 3. Vector Database Architecture

```
┌────────────────────────────────────────────────────────┐
│         SEMANTIC SIMILARITY DETECTION SYSTEM          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Resume Text  ─►  SentenceTransformers ─────┐         │
│  "Python       (all-MiniLM-L6-v2)           │         │
│   engineer     384-dimensional               │         │
│   5 YOE")      embedding vectors             ▼         │
│                                        ┌─────────────┐ │
│                                        │  Pinecone   │ │
│                                        │  Vector DB  │ │
│                                        ├─────────────┤ │
│  Vector Search │                       │ Index:      │ │
│  Query:        │────────────────────►  │ - 10K+      │ │
│  [0.23,        │  Cosine Similarity    │   resumes   │ │
│   0.45,        │                       │ - 384D      │ │
│   ...0.78]     │  Find K=10             │ - HNSW      │ │
│                │  nearest neighbors     │   algorithm │ │
│                │                        └─────────────┘ │
│           ┌────────────────────────────────────────┐   │
│           │ Similar Resumes with Scores            │   │
│           ├────────────────────────────────────────┤   │
│           │ 1. resume_123: 0.92 (92% similar)      │   │
│           │ 2. resume_456: 0.87 (87% similar)      │   │
│           │ 3. resume_789: 0.81 (81% similar)      │   │
│           │ ... (up to K results)                  │   │
│           └────────────────────────────────────────┘   │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ PLAGIARISM DETECTION LOGIC                      │  │
│  ├─────────────────────────────────────────────────┤  │
│  │ IF similarity >= 0.95:                          │  │
│  │    result = CRITICAL (Plagiarized)              │  │
│  │                                                 │  │
│  │ IF similarity in [0.85, 0.95):                  │  │
│  │    result = HIGH RISK (Review required)         │  │
│  │                                                 │  │
│  │ IF similarity in [0.70, 0.85):                  │  │
│  │    result = MEDIUM (Investigate)                │  │
│  │                                                 │  │
│  │ IF similarity < 0.70:                           │  │
│  │    result = LOW (Appears authentic)             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ AI-GENERATED RESUME DETECTION                   │  │
│  ├─────────────────────────────────────────────────┤  │
│  │ GPT-generated resumes show patterns:             │  │
│  │ - Too many high-similarity matches (0.8-0.95)   │  │
│  │ - Unusual word distributions                    │  │
│  │ - Perfect grammar/formatting consistency        │  │
│  │ - Generic achievement descriptions              │  │
│  │                                                 │  │
│  │ Risk Score = f(similarity_pattern, linguistic) │  │
│  │ Range: [0.0 (authentic) to 1.0 (AI-generated)]  │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

## 4. Machine Learning Pipeline

```
                    ┌─────────────────────────────┐
                    │   RESUME UPLOADED           │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  1. PARSE RESUME    │
                    ├────────────────────┤
                    │ - Extract text      │
                    │ - Clean formatting  │
                    │ - Segment sections  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────────┐
                    │ 2. EXTRACT CLAIMS      │
                    ├──────────────────────┤
                    │ NER (SpaCy):          │
                    │ - PERSON, ORG, GPE    │
                    │ - SKILL, EDUCATION    │
                    │                       │
                    │ BERT (Transformers):  │
                    │ - Ambiguous claims    │
                    │ - Relationships       │
                    └──────────┬──────────────┘
                               │
    ┌──────────────────────────┼──────────────────────────┐
    │                          │                          │
    ▼                          ▼                          ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ GitHub      │         │ LinkedIn    │         │ Certificate │
│ Analyzer    │         │ Matcher     │         │ OCR         │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ - Repos     │         │ - Education │         │ - Tesseract │
│ - Languages │         │ - Companies │         │ - Font Check│
│ - Commits   │         │ - Timeline  │         │ - Metadata  │
│ → Score     │         │ → Score     │         │ → Score     │
└────┬────────┘         └────┬────────┘         └────┬────────┘
     │                       │                       │
     │ 0-1 score            │ 0-1 score            │ 0-1 score
     │                       │                       │
     └───────────────────────┼───────────────────────┘
                             │
                ┌────────────▼────────────┐
                │ 3. FEATURE ENGINEERING  │
                ├────────────────────────┤
                │ Combine 12 signals:    │
                │ - GitHub score         │
                │ - LinkedIn score       │
                │ - Certificate score    │
                │ - Timeline consistency │
                │ - Skill validation     │
                │ - Text similarity      │
                │ - Entity confidence    │
                │ - Language quality     │
                │ - Embedding distance   │
                │ - Temporal logic       │
                │ - Company validity     │
                │ - Education validity   │
                │ → Feature Vector       │
                └────────────┬───────────┘
                             │
                ┌────────────▼────────────────────┐
                │ 4. ML CLASSIFICATION            │
                ├────────────────────────────────┤
                │ XGBoost Binary Classifier      │
                │                                │
                │ Input: [12-dim feature vector]│
                │ Output: P(resume_authentic)    │
                │ Threshold: 0.75                │
                │ → Classification               │
                │ → Confidence Score             │
                └────────────┬────────────────────┘
                             │
                ┌────────────▼────────────┐
                │ 5. SHAP EXPLANATION     │
                ├────────────────────────┤
                │ Feature Importance:    │
                │ - Which 3 features     │
                │   most influenced      │
                │   decision?            │
                │ - How much each helped?│
                │ → Human-readable       │
                │   explanation          │
                └────────────┬───────────┘
                             │
                ┌────────────▼────────────┐
                │ 6. TRUST SCORE          │
                ├────────────────────────┤
                │ score = 100 * P(auth)  │
                │ Range: [0, 100]        │
                │ 0-50:  Fraudulent      │
                │ 50-75: Suspicious      │
                │ 75-85: Likely Authentic│
                │ 85+:   Verified        │
                └────────────┬───────────┘
                             │
                ┌────────────▼────────────┐
                │ RESULT                  │
                ├────────────────────────┤
                │ - Score: 87.3%          │
                │ - Status: VERIFIED      │
                │ - Confidence: 95%       │
                │ - Explanation: ...      │
                │ → Store in DB           │
                │ → Write to Blockchain   │
                │ → Send to Frontend      │
                └────────────────────────┘
```

## 5. Kubernetes Deployment Architecture

```
┌──────────────────────────────────────┐
│      AWS / GCP / Azure / On-Prem      │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐   │
│  │   KUBERNETES CLUSTER         │   │
│  ├──────────────────────────────┤   │
│  │                              │   │
│  │  ┌────────────────────────┐  │   │
│  │  │  Ingress Controller    │  │   │
│  │  │  (Nginx / Traefik)     │  │   │
│  │  └────────────┬───────────┘  │   │
│  │               │              │   │
│  │  ┌────────────▼───────────┐  │   │
│  │  │ Load Balancer Service  │  │   │
│  │  │ ├─ api.example.com     │  │   │
│  │  │ ├─ api-internal        │  │   │
│  │  │ └─ metrics.example.com │  │   │
│  │  └────────────┬───────────┘  │   │
│  │               │              │   │
│  │  ┌────────────▼───────────────────────┐   │
│  │  │      NODE POOL (Auto-scaling)       │   │
│  │  ├───────────────────────────────────┤   │
│  │  │                                   │   │
│  │  │  ┌──────────┐ ┌──────────┐       │   │
│  │  │  │  Node 1  │ │  Node 2  │ ...  │   │
│  │  │  │          │ │          │       │   │
│  │  │  │ ┌─────┐  │ │ ┌─────┐  │       │   │
│  │  │  │ │API  │  │ │ │API  │  │       │   │
│  │  │  │ │Pod 1│  │ │ │Pod 2│  │       │   │
│  │  │  │ └─────┘  │ │ └─────┘  │       │   │
│  │  │  │ ┌─────┐  │ │ ┌─────┐  │       │   │
│  │  │  │ │Verify│ │ │ │Block│  │       │   │
│  │  │  │ │Worker│ │ │ │chain│  │       │   │
│  │  │  │ └─────┘  │ │ │Worker│  │       │   │
│  │  │  └──────────┘ └──────────┘       │   │
│  │  │                                   │   │
│  │  └───────────────────────────────────┘   │
│  │                                      │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │  STATEFUL SERVICES           │   │   │
│  │  ├──────────────────────────────┤   │   │
│  │  │                              │   │   │
│  │  │ PostgreSQL StatefulSet       │   │   │
│  │  │ ├─ Persistent Volume Claim   │   │   │
│  │  │ └─ Backup: Daily snapshots   │   │   │
│  │  │                              │   │   │
│  │  │ Redis Cluster                │   │   │
│  │  │ ├─ 3 master nodes            │   │   │
│  │  │ └─ 3 replica nodes           │   │   │
│  │  │                              │   │   │
│  │  │ Kafka StatefulSet            │   │   │
│  │  │ ├─ 3 brokers                 │   │   │
│  │  │ └─ Zookeeper consensus       │   │   │
│  │  └──────────────────────────────┘   │   │
│  │                                      │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │  MONITORING STACK            │   │   │
│  │  ├──────────────────────────────┤   │   │
│  │  │ Prometheus + Grafana         │   │   │
│  │  │ Datadog / New Relic (opt)    │   │   │
│  │  │ Alert Manager                │   │   │
│  │  │ Loki (Logging)               │   │   │
│  │  └──────────────────────────────┘   │   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## View Diagrams

These diagrams can be rendered as Mermaid diagrams for interactive viewing. For best visualisation, use a markdown viewer that supports Mermaid (GitHub, GitLab, etc).

