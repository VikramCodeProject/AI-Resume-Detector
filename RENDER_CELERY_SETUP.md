# Adding Celery Worker to Render

## Problem
Background jobs (resume verification, ML analysis) won't process without a Celery worker.

## Solution

### Option 1: Add Worker to render.yaml

Add this service to your `render.yaml`:

```yaml
- type: worker
  name: resume-verify-worker
  runtime: python
  plan: free
  buildCommand: cd backend && pip install -r requirements.txt
  startCommand: cd backend && celery -A tasks worker --loglevel=info --concurrency=2
  envVars:
    - key: DATABASE_URL
      fromService:
        type: pserv
        name: resume-verify-db
        property: connectionString
    - key: REDIS_URL
      fromService:
        type: redis
        name: resume-verify-redis
        property: connectionString
    - key: ENVIRONMENT
      value: production
    # Add all other secrets from backend service
```

### Option 2: Use Render Background Workers

1. Go to Render Dashboard
2. Click **"New"** → **"Background Worker"**
3. Connect same repository
4. Set:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && celery -A tasks worker --loglevel=info`
   - **Environment:** Copy all variables from backend service

### Option 3: Use Render Cron Jobs (for periodic tasks)

If you only need scheduled verification checks:

```yaml
- type: cron
  name: resume-verify-scheduler
  runtime: python
  schedule: "*/15 * * * *"  # Every 15 minutes
  buildCommand: cd backend && pip install -r requirements.txt
  startCommand: cd backend && python run_scheduled_tasks.py
```

## Testing Worker

After adding worker:

```bash
# Check worker logs in Render Dashboard
# Should see: "celery@worker ready"

# Test with Python script:
from celery import Celery
app = Celery('tasks', broker='redis://your-redis-url')
result = app.send_task('tasks.verify_resume', args=[resume_id])
```

## Cost Consideration

- Free tier: 750 hours/month total (shared across all services)
- 4 services (DB, Redis, Backend, Frontend) = ~500 hours/month
- Adding worker = ~250 hours/month remaining
- **Recommendation:** Upgrade to paid plan ($7/month per service) for production
