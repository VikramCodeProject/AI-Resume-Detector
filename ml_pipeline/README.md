# Resume Authenticity Detection - Production ML Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MLflow](https://img.shields.io/badge/MLflow-Enabled-orange.svg)](https://mlflow.org/)

## 🎯 Project Overview

**Resume Authenticity Detection** is an enterprise-grade machine learning pipeline that classifies resumes into three categories:

- ✅ **Authentic**: Genuine resumes with verifiable claims
- ⚠️ **Exaggerated**: Resumes with inflated or embellished claims
- ❌ **Fake**: Fraudulent resumes with false information

This production-ready system implements clean architecture principles, comprehensive experiment tracking with MLflow, and benchmarks multiple state-of-the-art ML algorithms.

---

## 🏗️ Architecture

```
ml_pipeline/
│
├── data/                          # Dataset storage
│   └── resume_dataset.csv         # Input dataset
│
├── src/                           # Source code modules
│   ├── preprocess.py             # Data preprocessing & feature engineering
│   ├── train.py                  # Model training & cross-validation
│   ├── evaluate.py               # Model evaluation & visualization
│   └── mlflow_logger.py          # MLflow experiment tracking
│
├── models/                        # Saved trained models
├── artifacts/                     # Generated visualizations & reports
├── results/                       # Evaluation results & comparisons
├── mlruns/                        # MLflow tracking data
│
├── main.py                        # Pipeline orchestrator
├── requirements.txt               # Python dependencies
├── generate_sample_dataset.py    # Sample data generator
└── README.md                      # This file
```

---

## 🚀 Features

### 1. **Data Preprocessing Pipeline**
- ✅ Automated null value handling
- ✅ Text normalization (lowercasing, special character removal)
- ✅ NLP preprocessing (stopword removal, lemmatization)
- ✅ TF-IDF vectorization with configurable features (default: 5000)
- ✅ Stratified train-test splitting (80/20)
- ✅ Comprehensive dataset statistics reporting

### 2. **Multi-Model Benchmarking**
Trains and evaluates **4 state-of-the-art algorithms**:

| Model | Description | Key Hyperparameters |
|-------|-------------|---------------------|
| **Logistic Regression** | Linear baseline with L2 regularization | C=1.0, max_iter=1000 |
| **Random Forest** | Ensemble of 200 decision trees | max_depth=20, class_weight='balanced' |
| **XGBoost** | Gradient boosting with early stopping | n_estimators=200, learning_rate=0.1 |
| **Neural Network (MLP)** | 3-layer deep neural network | layers=(128,64,32), early_stopping=True |

### 3. **Comprehensive Evaluation**
- **Metrics**: Accuracy, Precision, Recall, F1-Score (macro & weighted)
- **Confusion Matrices**: Heatmaps for each model
- **Classification Reports**: Per-class performance breakdown
- **Model Comparison**: Side-by-side visual comparisons

### 4. **K-Fold Cross-Validation**
- Stratified 5-fold cross-validation
- Mean and standard deviation for all metrics
- Prevents overfitting and provides robust performance estimates

### 5. **MLflow Integration**
- ✅ Automatic experiment tracking
- ✅ Parameter and metric logging
- ✅ Model versioning and registry
- ✅ Artifact storage (plots, reports, models)
- ✅ Run comparison and best model identification
- ✅ Local tracking server with web UI

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

```bash
# 1. Clone the repository (if not already cloned)
cd c:/Users/ACER/Desktop/UsMiniProject

# 2. Navigate to the ML pipeline directory
cd ml_pipeline

# 3. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download required NLTK data (automatic on first run)
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt')"

# 6. Download spaCy model
python -m spacy download en_core_web_sm
```

---

## 📊 Dataset Preparation

### Expected CSV Format

Your dataset CSV file should have the following structure:

```csv
resume_text,label
"Experienced software engineer with 5 years of Python...",Authentic
"PhD in Machine Learning from MIT, 20 years experience...",Exaggerated
"Founder of Google, invented the internet...",Fake
```

### Required Columns:
- `resume_text` (string): Full text content of the resume
- `label` (string): One of `Authentic`, `Exaggerated`, or `Fake`

### Generate Sample Dataset

If you don't have a dataset, generate a sample one:

```bash
python generate_sample_dataset.py
```

This creates `data/resume_dataset.csv` with 1000 synthetic resume samples.

---

## 🎮 Usage

### Quick Start (Full Pipeline)

```bash
# Run the complete pipeline with default settings
python main.py --dataset ./data/resume_dataset.csv
```

### Advanced Usage

```bash
# Custom configuration
python main.py \
    --dataset ./data/resume_dataset.csv \
    --experiment-name My_Resume_Experiment \
    --test-size 0.25 \
    --max-features 3000 \
    --cv-folds 10 \
    --random-state 42
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--dataset` | Path to dataset CSV | `./data/resume_dataset.csv` |
| `--experiment-name` | MLflow experiment name | `Resume_Authenticity_Experiment` |
| `--test-size` | Test set proportion | `0.2` |
| `--max-features` | Max TF-IDF features | `5000` |
| `--cv-folds` | Cross-validation folds | `5` |
| `--random-state` | Random seed | `42` |
| `--no-save-models` | Skip saving models | `False` |
| `--no-export-results` | Skip exporting results | `False` |

---

## 📈 Output & Results

### Generated Files

After running the pipeline, you'll find:

```
ml_pipeline/
├── models/                          # Trained models (.joblib)
│   ├── Logistic_Regression_20260228_143022.joblib
│   ├── Random_Forest_20260228_143045.joblib
│   ├── XGBoost_20260228_143110.joblib
│   └── Neural_Network_20260228_143135.joblib
│
├── artifacts/                       # Visualizations
│   ├── confusion_matrix_Logistic_Regression_20260228_143022.png
│   ├── confusion_matrix_Random_Forest_20260228_143045.png
│   ├── confusion_matrix_XGBoost_20260228_143110.png
│   ├── confusion_matrix_Neural_Network_20260228_143135.png
│   └── model_comparison_20260228_143200.png
│
├── results/                         # Evaluation reports
│   ├── model_comparison_20260228_143200.csv
│   ├── report_Logistic_Regression_20260228_143200.txt
│   ├── report_Random_Forest_20260228_143200.txt
│   ├── report_XGBoost_20260228_143200.txt
│   └── report_Neural_Network_20260228_143200.txt
│
├── mlruns/                          # MLflow tracking data
└── pipeline_run_20260228_143000.log # Execution log
```

### MLflow UI

View experiment results in the MLflow web interface:

```bash
# Start MLflow UI
mlflow ui

# Open in browser
http://localhost:5000
```

**Features in MLflow UI:**
- Compare all model runs side-by-side
- Interactive metric charts
- Download trained models
- View confusion matrices
- Inspect hyperparameters

---

## 🔬 Pipeline Components

### 1. Preprocessing (`src/preprocess.py`)

```python
from src.preprocess import preprocess_pipeline

data = preprocess_pipeline(
    file_path='data/resume_dataset.csv',
    test_size=0.2,
    max_features=5000
)
```

**Returns:**
- `X_train`: Training features (TF-IDF vectors)
- `X_test`: Testing features
- `y_train`: Training labels
- `y_test`: Testing labels
- `preprocessor`: Fitted preprocessor instance
- `label_names`: List of class names

### 2. Training (`src/train.py`)

```python
from src.train import ModelTrainer

trainer = ModelTrainer(random_state=42)
trained_models = trainer.train_all_models(X_train, y_train)

# Cross-validation
cv_results = trainer.cross_validate_all_models(X_full, y_full, cv_folds=5)
```

### 3. Evaluation (`src/evaluate.py`)

```python
from src.evaluate import ModelEvaluator

evaluator = ModelEvaluator(label_names=['Authentic', 'Exaggerated', 'Fake'])
results = evaluator.evaluate_all_models(trained_models, X_test, y_test)

# Generate visualizations
evaluator.plot_all_confusion_matrices('./artifacts')
evaluator.plot_model_comparison('./artifacts/comparison.png')

# Get best model
best_model_name, best_metrics = evaluator.get_best_model()
```

### 4. MLflow Tracking (`src/mlflow_logger.py`)

```python
from src.mlflow_logger import MLflowLogger

ml_logger = MLflowLogger('Resume_Authenticity_Experiment')
ml_logger.start_run('model_run')

# Log parameters and metrics
ml_logger.log_parameters(params)
ml_logger.log_metrics(metrics)

# Log model
ml_logger.log_model(model, 'XGBoost')

# Log confusion matrix
ml_logger.log_confusion_matrix(cm, 'XGBoost', label_names)

ml_logger.end_run()
```

---

## 📊 Sample Output

```
================================================================================
RESUME AUTHENTICITY DETECTION - ML PIPELINE
================================================================================
Dataset: ./data/resume_dataset.csv
Experiment: Resume_Authenticity_Experiment
Random State: 42
Timestamp: 2026-02-28 14:30:00
================================================================================

================================================================================
STEP 1: DATA PREPROCESSING
================================================================================
Loading dataset from: ./data/resume_dataset.csv
Dataset loaded successfully. Shape: (1000, 2)
...
Training samples: 800
Testing samples: 200
✓ Preprocessing completed successfully

================================================================================
STEP 2: MODEL TRAINING
================================================================================
Training Logistic_Regression...
  Training completed in 2.34 seconds
Training Random_Forest...
  Training completed in 8.91 seconds
Training XGBoost...
  Training completed in 5.67 seconds
Training Neural_Network...
  Training completed in 12.45 seconds
✓ Model training completed successfully

================================================================================
STEP 3: MODEL EVALUATION
================================================================================
Results for XGBoost
============================================================
Accuracy:           0.9450
Precision (macro):  0.9433
Recall (macro):     0.9417
F1-Score (macro):   0.9425
============================================================

================================================================================
MODEL COMPARISON TABLE
================================================================================
              Model  Accuracy  Precision (Macro)  Recall (Macro)  F1-Score (Macro)
           XGBoost    0.9450             0.9433          0.9417            0.9425
     Random_Forest    0.9300             0.9288          0.9267            0.9277
Logistic_Regression    0.8850             0.8833          0.8817            0.8825
   Neural_Network     0.9100             0.9088          0.9067            0.9077
================================================================================

✓ Model evaluation completed successfully

================================================================================
BEST MODEL IDENTIFICATION
================================================================================
Best Model: XGBoost
F1-Score (Macro): 0.9425
================================================================================

================================================================================
PIPELINE EXECUTION COMPLETED SUCCESSFULLY
================================================================================
Total Duration: 156.78 seconds (2.61 minutes)
Models Trained: 4
Best Model: XGBoost
Results saved in: ./results, ./models, ./artifacts
MLflow UI: Run 'mlflow ui' and open http://localhost:5000
================================================================================
```

---

## 🧪 Testing

Run unit tests (if implemented):

```bash
pytest tests/ -v --cov=src
```

---

## 🔧 Customization

### Add Custom Models

Edit `src/train.py` and add your model to the `_initialize_models` method:

```python
'Your_Model_Name': YourModelClass(
    param1=value1,
    param2=value2,
    random_state=self.random_state
)
```

### Modify Preprocessing

Edit `src/preprocess.py` to customize:
- Text cleaning rules
- Feature extraction methods
- Train-test split ratios

### Custom Metrics

Add new metrics in `src/evaluate.py`:

```python
from sklearn.metrics import your_custom_metric

metrics['custom_metric'] = your_custom_metric(y_test, y_pred)
```

---

## 📚 Dependencies

**Core Libraries:**
- scikit-learn 1.3.0 (ML algorithms)
- xgboost 2.0.0 (Gradient boosting)
- nltk 3.8.1 (NLP preprocessing)
- pandas 2.0.3 (Data manipulation)
- numpy 1.24.3 (Numerical computing)

**Experiment Tracking:**
- mlflow 2.7.1 (Experiment tracking & model registry)

**Visualization:**
- matplotlib 3.7.2 (Plotting)
- seaborn 0.12.2 (Statistical visualization)

See `requirements.txt` for complete list.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **University Feedback**: This implementation incorporates best practices and feedback from academic review
- **MLflow Community**: For excellent experiment tracking tools
- **scikit-learn Team**: For comprehensive ML library
- **XGBoost Developers**: For high-performance gradient boosting

---

## 📞 Support

For issues, questions, or contributions:

- 📧 Email: [your-email@university.edu]
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Documentation: This README

---

## 🎓 Academic Citation

If you use this work in academic research, please cite:

```bibtex
@software{resume_authenticity_detection,
  author = {Your Name},
  title = {Resume Authenticity Detection: Production ML Pipeline},
  year = {2026},
  url = {https://github.com/your-repo}
}
```

---

## 🗓️ Version History

- **v1.0.0** (2026-02-28): Initial production-ready release
  - Complete ML pipeline with 4 models
  - MLflow integration
  - Comprehensive evaluation framework
  - Enterprise-grade code structure

---

## 🎯 Future Enhancements

- [ ] Deep learning models (BERT, GPT-based)
- [ ] Real-time inference API
- [ ] Web-based dashboard
- [ ] Blockchain verification integration
- [ ] Multi-language support
- [ ] Automated hyperparameter tuning (Optuna/Ray Tune)
- [ ] Model explainability (SHAP, LIME)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment guide

---

**Built with ❤️ for Enterprise ML**
