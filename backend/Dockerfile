# Multi-stage Dockerfile for Resume Verification Backend
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory for structured file logs
RUN mkdir -p /app/logs

# Expose Render default port
EXPOSE 10000

# Health check (uses Render PORT when available)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c "python -c \"import os,requests; p=os.getenv('PORT','10000'); requests.get(f'http://localhost:{p}/api/health', timeout=5)\"" || exit 1

# Run the application on Render-assigned port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 2"]
