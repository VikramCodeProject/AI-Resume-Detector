-- Claim and verification persistence

CREATE TABLE IF NOT EXISTS claims (
    id VARCHAR(36) PRIMARY KEY,
    resume_id VARCHAR(36) NOT NULL,
    claim_type VARCHAR(50) NOT NULL,
    claim_text TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_results (
    id VARCHAR(36) PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL,
    source VARCHAR(64) NOT NULL,
    score DOUBLE PRECISION NOT NULL DEFAULT 0,
    evidence_json TEXT NOT NULL DEFAULT '{}',
    verified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_claims_resume_id ON claims(resume_id);
CREATE INDEX IF NOT EXISTS idx_verification_results_claim_id ON verification_results(claim_id);
