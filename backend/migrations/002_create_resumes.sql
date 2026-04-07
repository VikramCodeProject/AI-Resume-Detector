-- Resume metadata and trust score persistence

CREATE TABLE IF NOT EXISTS resumes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'processing',
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_duration_seconds DOUBLE PRECISION NOT NULL DEFAULT 10,
    trust_overall_score DOUBLE PRECISION NULL,
    trust_verified_count INTEGER NULL,
    trust_doubtful_count INTEGER NULL,
    trust_fake_count INTEGER NULL,
    trust_generated_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_status ON resumes(status);
