#!/bin/bash
# Railway Build Script
# This tells Railway how to build the FastAPI backend for production

echo "🔨 Building Resume Verification System for Railway..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Download NLP model
echo "🤖 Downloading NLP model..."
python -m spacy download en_core_web_sm

# Return to root
cd ..

echo "✅ Build complete! Ready to start server..."
