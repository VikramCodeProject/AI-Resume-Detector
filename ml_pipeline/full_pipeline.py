"""
Complete ML Pipeline with 4 Models & MLflow Tracking
Includes: Logistic Regression, Random Forest, XGBoost, Neural Network (MLP)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
import xgboost as xgb
import re
import string
import warnings
import os
import joblib
warnings.filterwarnings('ignore')

try:
    import mlflow
    import mlflow.sklearn
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("Resume_Authenticity_Detection")
    MLFLOW_AVAILABLE = True
except:
    MLFLOW_AVAILABLE = False
    print("MLflow not available - will skip experiment tracking")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOT_AVAILABLE = True
except:
    PLOT_AVAILABLE = False
    print("Matplotlib/Seaborn not available - will skip visualizations")

print("=" * 80)
print(" " * 15 + "RESUME AUTHENTICITY DETECTION")
print(" " * 10 + "Production ML Pipeline with 4 Models")
print("=" * 80)

# Step 1: Load Data
print("\n[1/7] Loading dataset...")
df = pd.read_csv('./data/resume_dataset.csv')
print(f"✓ Loaded {len(df)} resumes")
print(f"  Distribution:")
for label in df['label'].unique():
    count = len(df[df['label']==label])
    print(f"    - {label}: {count} ({count/len(df)*100:.1f}%)")

# Step 2: Simple Text Cleaning
print("\n[2/7] Preprocessing text...")
def clean_text(text):
    """Basic text cleaning without NLTK"""
    text = text.lower()
    text = re.sub(f'[{string.punctuation}]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df['cleaned_text'] = df['resume_text'].apply(clean_text)
print("✓ Text cleaned")

# Step 3: Feature Extraction
print("\n[3/7] Extracting features (TF-IDF)...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.9,
    ngram_range=(1, 2)
)
X = vectorizer.fit_transform(df['cleaned_text'])
y = df['label']

# Encode labels for XGBoost (needs 0,1,2 not strings)
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"✓ Feature matrix: {X.shape} (samples × features)")

# Step 4: Train-Test Split
print("\n[4/7] Splitting data (stratified)...")
X_train, X_test, y_train_enc, y_test_enc = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
# Keep string labels for non-XGBoost models
X_train_, X_test_, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train set: {X_train.shape[0]} samples ({X_train.shape[0]/len(df)*100:.0f}%)")
print(f"✓ Test set: {X_test.shape[0]} samples ({X_test.shape[0]/len(df)*100:.0f}%)")

# Step 5: Define Models
print("\n[5/7] Initializing 4 ML models...")
models = {
    'Logistic Regression': LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver='lbfgs'
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=20,
        min_samples_split=5
    ),
    'XGBoost': xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss'
    ),
    'Neural Network (MLP)': MLPClassifier(
        hidden_layer_sizes=(128, 64),
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )
}
print(f"✓ {len(models)} models initialized")

# Step 6: Train & Evaluate
print("\n[6/7] Training models with 5-fold cross-validation...")
results = {}
os.makedirs('./models', exist_ok=True)
os.makedirs('./artifacts', exist_ok=True)

for name, model in models.items():
    print(f"\n  {'=' * 70}")
    print(f"  Model: {name}")
    print(f"  {'=' * 70}")
    
    # MLflow run
    if MLFLOW_AVAILABLE:
        mlflow.start_run(run_name=name)
        mlflow.log_param("model_type", name)
        mlflow.log_param("train_size", X_train.shape[0])
        mlflow.log_param("test_size", X_test.shape[0])
        mlflow.log_param("n_features", X_train.shape[1])
    
    # Training
    print(f"  Training...")
    # XGBoost and MLP need encoded labels, others work with strings
    if name in ['XGBoost', 'Neural Network (MLP)']:
        model.fit(X_train, y_train_enc)
        y_pred_enc = model.predict(X_test)
        y_pred = label_encoder.inverse_transform(y_pred_enc)
        y_test_current = y_test
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_test_current = y_test
    print(f"  ✓ Training complete")
    print(f"  ✓ Training complete")
    
    # Metrics
    accuracy = accuracy_score(y_test_current, y_pred)
    precision = precision_score(y_test_current, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test_current, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test_current, y_pred, average='weighted', zero_division=0)
    
    print(f"  Test Accuracy:  {accuracy:.4f}")
    print(f"  Precision:      {precision:.4f}")
    print(f"  Recall:         {recall:.4f}")
    print(f"  F1-Score:       {f1:.4f}")
    
    # Cross-validation
    print(f"  Running 5-fold cross-validation...")
    if name in ['XGBoost', 'Neural Network (MLP)']:
        cv_scores = cross_val_score(model, X_train, y_train_enc, cv=5, scoring='accuracy')
    else:
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"  ✓ CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Log to MLflow
    if MLFLOW_AVAILABLE:
        mlflow.log_metric("test_accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("cv_mean", cv_scores.mean())
        mlflow.log_metric("cv_std", cv_scores.std())
        
        # Save model
        mlflow.sklearn.log_model(model, "model")
        mlflow.end_run()
    
    # Save locally
    model_filename = f"./models/{name.replace(' ', '_').replace('(', '').replace(')', '').lower()}_model.pkl"
    joblib.dump(model, model_filename)
    
    results[name] = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'predictions': y_pred,
        'confusion_matrix': confusion_matrix(y_test_current, y_pred)
    }

# Save vectorizer
joblib.dump(vectorizer, './models/tfidf_vectorizer.pkl')

# Step 7: Generate Report
print("\n" + "=" * 80)
print(" " * 25 + "FINAL RESULTS")
print("=" * 80)

# Summary table
print("\nModel Performance Summary:")
print("-" * 80)
print(f"{'Model':<25} {'Accuracy':>10} {'F1-Score':>10} {'CV Score':>15}")
print("-" * 80)
for name, result in results.items():
    print(f"{name:<25} {result['accuracy']:>10.4f} {result['f1_score']:>10.4f} "
          f"{result['cv_mean']:>10.4f} (+/- {result['cv_std']:.4f})")
print("-" * 80)

# Best model
best_model_name = max(results, key=lambda x: results[x]['accuracy'])
best_accuracy = results[best_model_name]['accuracy']
print(f"\n🏆 BEST MODEL: {best_model_name}")
print(f"   Accuracy: {best_accuracy:.4f}")
print(f"   F1-Score: {results[best_model_name]['f1_score']:.4f}")

# Detailed reports
print("\n" + "=" * 80)
print("DETAILED CLASSIFICATION REPORTS")
print("=" * 80)

for name, result in results.items():
    print(f"\n{name}:")
    print("-" * 70)
    print(classification_report(y_test, result['predictions'], zero_division=0))
    print("\nConfusion Matrix:")
    print(result['confusion_matrix'])
    print()

# Save confusion matrices as plots if matplotlib available
if PLOT_AVAILABLE:
    print("\n[7/7] Generating visualizations...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Confusion Matrices - Resume Authenticity Detection', fontsize=16, fontweight='bold')
    
    for idx, (name, result) in enumerate(results.items()):
        ax = axes[idx // 2, idx % 2]
        sns.heatmap(result['confusion_matrix'], annot=True, fmt='d', cmap='Blues', ax=ax,
                    xticklabels=['Authentic', 'Exaggerated', 'Fake'],
                    yticklabels=['Authentic', 'Exaggerated', 'Fake'])
        ax.set_title(f"{name}\nAccuracy: {result['accuracy']:.4f}", fontweight='bold')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
    
    plt.tight_layout()
    plt.savefig('./artifacts/confusion_matrices.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: ./artifacts/confusion_matrices.png")
    
    # Model comparison chart
    fig, ax = plt.subplots(figsize=(12, 6))
    model_names = list(results.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1_score']
    x = np.arange(len(model_names))
    width = 0.2
    
    for idx, metric in enumerate(metrics):
        values = [results[m][metric] for m in model_names]
        ax.bar(x + idx*width, values, width, label=metric.replace('_', ' ').title())
    
    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    plt.savefig('./artifacts/model_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: ./artifacts/model_comparison.png")

print("\n" + "=" * 80)
print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\nSaved Artifacts:")
print(f"  • Models: ./models/ ({len(models)} models + vectorizer)")
print(f"  • Visualizations: ./artifacts/ (confusion matrices + comparison)")
if MLFLOW_AVAILABLE:
    print(f"  • MLflow Tracking: ./mlruns/")
    print(f"\n💡 View results: mlflow ui (then open http://localhost:5000)")
print()
