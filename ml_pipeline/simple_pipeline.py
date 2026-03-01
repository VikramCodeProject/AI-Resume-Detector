"""
Simplified Resume Authenticity Detection Pipeline
No external NLP dependencies - runs immediately after pip install
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import re
import string
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("RESUME AUTHENTICITY DETECTION - SIMPLE PIPELINE")
print("=" * 80)

# Step 1: Load Data
print("\n[1/6] Loading dataset...")
df = pd.read_csv('./data/resume_dataset.csv')
print(f"✓ Loaded {len(df)} resumes")
print(f"  - Authentic: {len(df[df['label']=='Authentic'])}")
print(f"  - Exaggerated: {len(df[df['label']=='Exaggerated'])}")
print(f"  - Fake: {len(df[df['label']=='Fake'])}")

# Step 2: Simple Text Cleaning
print("\n[2/6] Cleaning text (basic preprocessing)...")
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
print("\n[3/6] Extracting features (TF-IDF)...")
vectorizer = TfidfVectorizer(
    max_features=3000,
    min_df=2,
    max_df=0.9,
    ngram_range=(1, 2)
)
X = vectorizer.fit_transform(df['cleaned_text'])
y = df['label']
print(f"✓ Feature matrix: {X.shape}")

# Step 4: Train-Test Split
print("\n[4/6] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train: {X_train.shape[0]} samples")
print(f"✓ Test: {X_test.shape[0]} samples")

# Step 5: Train Models
print("\n[5/6] Training models...")
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
}

results = {}
for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    
    results[name] = {
        'accuracy': accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'predictions': y_pred
    }
    
    print(f"  ✓ Test Accuracy: {accuracy:.4f}")
    print(f"  ✓ CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Step 6: Evaluation
print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)

for name, result in results.items():
    print(f"\n{name}:")
    print(f"  Test Accuracy: {result['accuracy']:.4f}")
    print(f"  Cross-Validation: {result['cv_mean']:.4f} (+/- {result['cv_std']:.4f})")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, result['predictions'], zero_division=0))
    print(f"\n  Confusion Matrix:")
    cm = confusion_matrix(y_test, result['predictions'])
    print(cm)

# Save best model
best_model_name = max(results, key=lambda x: results[x]['accuracy'])
print(f"\n{'=' * 80}")
print(f"Best Model: {best_model_name}")
print(f"Accuracy: {results[best_model_name]['accuracy']:.4f}")
print(f"{'=' * 80}\n")

# Save model
import joblib
import os
os.makedirs('./models', exist_ok=True)
model_path = f'./models/{best_model_name.replace(" ", "_").lower()}_model.pkl'
joblib.dump(models[best_model_name], model_path)
joblib.dump(vectorizer, './models/tfidf_vectorizer.pkl')
print(f"✓ Model saved: {model_path}")
print(f"✓ Vectorizer saved: ./models/tfidf_vectorizer.pkl")

print("\n🎉 Pipeline completed successfully!")
