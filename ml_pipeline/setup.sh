#!/bin/bash
# Resume Authenticity Detection - Automated Setup Script for Linux/Mac
# This script sets up the complete ML pipeline environment

echo "================================================================================"
echo "RESUME AUTHENTICITY DETECTION - AUTOMATED SETUP"
echo "================================================================================"
echo ""

# Check Python installation
echo "[1/7] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi
python3 --version
echo ""

# Create virtual environment
echo "[2/7] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created successfully"
fi
echo ""

# Activate virtual environment
echo "[3/7] Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"
echo ""

# Upgrade pip
echo "[4/7] Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "[5/7] Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"
echo ""

# Download NLTK data
echo "[6/7] Downloading NLTK data..."
python3 -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('punkt', quiet=True); nltk.download('omw-1.4', quiet=True); print('NLTK data downloaded')"
echo ""

# Download spaCy model
echo "[7/7] Downloading spaCy model..."
python3 -m spacy download en_core_web_sm
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p data models artifacts results
echo "Directories created"
echo ""

echo "================================================================================"
echo "SETUP COMPLETED SUCCESSFULLY!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Generate sample dataset:"
echo "     python generate_sample_dataset.py"
echo ""
echo "  3. Run the ML pipeline:"
echo "     python main.py --dataset ./data/resume_dataset.csv"
echo ""
echo "  4. View results in MLflow UI:"
echo "     mlflow ui"
echo "     Then open http://localhost:5000 in your browser"
echo ""
echo "For more information, see README.md or QUICKSTART.md"
echo "================================================================================"
echo ""
