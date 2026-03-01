# Quick Start Guide - Resume Authenticity Detection

Get up and running in 5 minutes! ⚡

## Prerequisites

- Python 3.10 or higher installed
- Command line access (Terminal/PowerShell/CMD)
- Internet connection for downloading packages

---

## Step 1: Setup Environment (2 minutes)

Open your terminal and navigate to the project directory:

```bash
cd c:/Users/ACER/Desktop/UsMiniProject/ml_pipeline
```

Create and activate a virtual environment:

**Windows (PowerShell/CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

---

## Step 2: Install Dependencies (2 minutes)

Install all required packages:

```bash
pip install -r requirements.txt
```

Download NLTK data:
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt'); nltk.download('omw-1.4')"
```

Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

---

## Step 3: Generate Sample Dataset (30 seconds)

```bash
python generate_sample_dataset.py
```

This creates `data/resume_dataset.csv` with 1000 synthetic resumes.

---

## Step 4: Run the Pipeline (1 minute)

Execute the full ML pipeline:

```bash
python main.py --dataset ./data/resume_dataset.csv
```

**That's it!** The pipeline will:
- ✅ Preprocess data
- ✅ Train 4 ML models (Logistic Regression, Random Forest, XGBoost, Neural Network)
- ✅ Evaluate models
- ✅ Perform cross-validation
- ✅ Log experiments to MLflow
- ✅ Generate visualizations
- ✅ Save models and results

---

## Step 5: View Results

### Check Output Files

**Trained Models:**
```bash
ls models/
```

**Visualizations:**
```bash
ls artifacts/
# - Confusion matrices
# - Model comparison plots
```

**Evaluation Reports:**
```bash
ls results/
# - CSV comparison table
# - Detailed classification reports
```

### View MLflow Dashboard

Start MLflow UI:
```bash
mlflow ui
```

Open in browser: [http://localhost:5000](http://localhost:5000)

**Features:**
- Compare all model runs
- View metrics and parameters
- Download trained models
- Inspect confusion matrices

---

## Expected Output (Sample)

```
================================================================================
RESUME AUTHENTICITY DETECTION - ML PIPELINE
================================================================================
Dataset: ./data/resume_dataset.csv
Experiment: Resume_Authenticity_Experiment
Random State: 42
================================================================================

STEP 1: DATA PREPROCESSING
Total Records: 1000
Training samples: 800
Testing samples: 200
✓ Preprocessing completed successfully

STEP 2: MODEL TRAINING
Training Logistic_Regression...
  Training completed in 2.34 seconds
Training Random_Forest...
  Training completed in 8.91 seconds
Training XGBoost...
  Training completed in 5.67 seconds
Training Neural_Network...
  Training completed in 12.45 seconds
✓ Model training completed successfully

STEP 3: MODEL EVALUATION
              Model  Accuracy  F1-Score (Macro)
           XGBoost    0.9450            0.9425
     Random_Forest    0.9300            0.9277
   Neural_Network    0.9100            0.9077
Logistic_Regression 0.8850            0.8825

Best Model: XGBoost
F1-Score: 0.9425
✓ Model evaluation completed successfully

PIPELINE EXECUTION COMPLETED SUCCESSFULLY
Total Duration: 156.78 seconds (2.61 minutes)
Results saved in: ./results, ./models, ./artifacts
MLflow UI: Run 'mlflow ui' and open http://localhost:5000
```

---

## Advanced Usage

### Custom Dataset

If you have your own dataset:

```bash
python main.py --dataset /path/to/your/dataset.csv
```

**Required CSV format:**
```csv
resume_text,label
"Resume text here...",Authentic
"Another resume...",Exaggerated
"Fake resume...",Fake
```

### Custom Configuration

```bash
python main.py \
    --dataset ./data/resume_dataset.csv \
    --test-size 0.25 \
    --max-features 3000 \
    --cv-folds 10 \
    --experiment-name My_Experiment
```

**Available Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `--dataset` | Path to CSV dataset | `./data/resume_dataset.csv` |
| `--experiment-name` | MLflow experiment name | `Resume_Authenticity_Experiment` |
| `--test-size` | Test set proportion | `0.2` |
| `--max-features` | Max TF-IDF features | `5000` |
| `--cv-folds` | Cross-validation folds | `5` |
| `--random-state` | Random seed | `42` |

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### Issue: "NLTK data not found"

**Solution:**
```bash
python -c "import nltk; nltk.download('all')"
```

### Issue: "Dataset not found"

**Solution:**
```bash
# Generate sample dataset first
python generate_sample_dataset.py
```

### Issue: MLflow UI not opening

**Solution:**
```bash
# Check if port 5000 is available
mlflow ui --port 5001
# Then open http://localhost:5001
```

---

## Next Steps

1. **Experiment with your own resume data**
   - Prepare your CSV file with `resume_text` and `label` columns
   - Run the pipeline with your dataset

2. **Tune hyperparameters**
   - Edit `src/train.py` to modify model parameters
   - Run multiple experiments with different configs

3. **Add custom models**
   - Import your model in `src/train.py`
   - Add to the `_initialize_models` method

4. **Deploy the best model**
   - Load saved model from `models/` directory
   - Create inference script or API
   - See README.md for deployment guide

5. **Explore MLflow**
   - Compare different runs
   - Track experiment history
   - Download models for deployment

---

## Getting Help

- 📖 **Full Documentation:** See [README.md](README.md)
- 🐛 **Issues:** Check execution logs in `pipeline_run_*.log`
- 💬 **Questions:** Review code comments in `src/` modules
- 🔍 **Examples:** Check function docstrings with `help(function_name)`

---

## Performance Expectations

**On typical laptop (8GB RAM, 4-core CPU):**

| Task | Duration |
|------|----------|
| Dataset preprocessing (1000 samples) | ~10 seconds |
| Model training (4 models) | ~30 seconds |
| Model evaluation | ~5 seconds |
| Cross-validation | ~60 seconds |
| MLflow logging | ~20 seconds |
| **Total pipeline** | **~2-3 minutes** |

**For larger datasets (10,000+ samples):**
- Expect 10-20 minutes for full pipeline
- Consider reducing `max_features` for faster processing
- Use fewer cross-validation folds (`--cv-folds 3`)

---

## Success Checklist

After running the pipeline, verify:

- ✅ `models/` directory contains 4 `.joblib` files
- ✅ `artifacts/` has confusion matrix PNG files
- ✅ `results/` has CSV and TXT report files
- ✅ `mlruns/` directory exists with experiment data
- ✅ Console shows "PIPELINE EXECUTION COMPLETED SUCCESSFULLY"
- ✅ MLflow UI opens at http://localhost:5000

---

**🎉 Congratulations! You're now running production-grade ML pipelines!**

For more advanced usage, custom models, and deployment instructions, see [README.md](README.md).
