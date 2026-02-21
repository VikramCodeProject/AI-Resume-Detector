"""
Celery configuration and async task handlers
"""
from celery import Celery, Task
from celery.schedules import crontab
import os
import logging

logger = logging.getLogger(__name__)

# Redis configuration from environment
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Initialize Celery
celery_app = Celery(
    'resume_verification',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Periodic tasks (optional)
celery_app.conf.beat_schedule = {
    'cleanup-old-uploads': {
        'task': 'tasks.cleanup_old_uploads',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}

class CallbackTask(Task):
    """Task with callback on completion"""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True

# ===================== TASKS =====================

@celery_app.task(bind=True, base=CallbackTask, name='tasks.process_resume')
def process_resume(self, resume_id: str, file_path: str):
    """
    Async task to process uploaded resume
    Extracts claims, runs verification, and ML classification
    """
    try:
        logger.info(f"Processing resume: {resume_id}")
        
        # Import here to avoid circular imports
        from ml_engine.pipeline import ResumeParser, ClaimExtractor, FeatureEngineer, MLClassifier
        from ml_engine.verification_engines import VerificationEngineOrchestrator
        
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'parsing'})
        
        # 1. Parse resume
        parser = ResumeParser()
        raw_text = parser.parse(file_path)
        if not raw_text:
            raise ValueError("Failed to extract text from resume")
        
        logger.info(f"Extracted {len(raw_text)} characters from resume")
        
        # 2. Extract claims
        self.update_state(state='PROGRESS', meta={'status': 'extracting_claims'})
        extractor = ClaimExtractor()
        claims = extractor.extract(raw_text)
        logger.info(f"Extracted {len(claims)} claims from resume")
        
        # 3. Run verifications in parallel
        self.update_state(state='PROGRESS', meta={'status': 'verifying'})
        orchest = VerificationEngineOrchestrator()
        verified_claims = orchest.parallel_verify(claims)
        
        # 4. Build features and predict
        self.update_state(state='PROGRESS', meta={'status': 'ml_classification'})
        engineer = FeatureEngineer()
        feature_vectors = engineer.build_features(verified_claims)
        
        classifier = MLClassifier()
        predictions = classifier.predict(feature_vectors)
        
        # 5. Calculate trust score
        trust_score = calculate_trust_score(predictions)
        
        logger.info(f"Resume processing completed with trust score: {trust_score}")
        
        return {
            'resume_id': resume_id,
            'claims_count': len(claims),
            'trust_score': trust_score,
            'status': 'completed'
        }
        
    except Exception as e:
        logger.exception(f"Error processing resume {resume_id}: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(name='tasks.verify_github')
def verify_github(claim_id: str, username: str):
    """Verify GitHub profile claims"""
    try:
        from ml_engine.verification_engines import GitHubAnalyzer
        
        analyzer = GitHubAnalyzer()
        score = analyzer.verify({'claim_text': username})
        
        logger.info(f"GitHub verification for {username}: {score}")
        return {'claim_id': claim_id, 'github_score': score}
    except Exception as e:
        logger.exception(f"GitHub verification error: {e}")
        raise

@celery_app.task(name='tasks.cleanup_old_uploads')
def cleanup_old_uploads():
    """Clean up old uploaded files (24+ hours old)"""
    import os
    from datetime import datetime, timedelta
    
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        return {'cleaned': 0}
    
    cutoff_time = datetime.now() - timedelta(days=1)
    cleaned = 0
    
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned += 1
                    logger.info(f"Deleted old file: {filename}")
                except Exception as e:
                    logger.error(f"Error deleting {filename}: {e}")
    
    return {'cleaned': cleaned}

def calculate_trust_score(predictions):
    """Calculate overall trust score from predictions"""
    if not predictions:
        return 50.0
    
    verified = sum(1 for p in predictions if p.get('prediction') == 'verified')
    doubtful = sum(1 for p in predictions if p.get('prediction') == 'doubtful')
    fake = sum(1 for p in predictions if p.get('prediction') == 'fake')
    
    total = len(predictions)
    
    # Weighted scoring
    score = (
        (verified / total * 100) * 0.8 +  # Verified claims weighted 80%
        (doubtful / total * 100) * 0.4 +  # Doubtful claims weighted 40%
        ((total - fake) / total * 100) * 0.2  # Non-fake claims weighted 20%
    ) / 3
    
    return min(100.0, max(0.0, score))
