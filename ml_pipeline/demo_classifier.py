"""
Demo: Using Trained Models for Resume Classification
This script demonstrates how to use the trained models to classify new resumes
"""

import joblib
import re
import string
import sys

print("=" * 80)
print(" " * 20 + "RESUME CLASSIFIER - DEMO")
print("=" * 80)

# Load models
print("\n[1/3] Loading trained models...")
try:
    vectorizer = joblib.load('./models/tfidf_vectorizer.pkl')
    models = {
        'Logistic Regression': joblib.load('./models/logistic_regression_model.pkl'),
        'Random Forest': joblib.load('./models/random_forest_model.pkl'),
        'XGBoost': joblib.load('./models/xgboost_model.pkl'),
        'Neural Network': joblib.load('./models/neural_network_mlp_model.pkl')
    }
    print(f"[OK] Loaded {len(models)} models")
    
    # Load label encoder for XGBoost/MLP
    import numpy as np
    from sklearn.preprocessing import LabelEncoder
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(['Authentic', 'Exaggerated', 'Fake'])  # Match training order
    
except Exception as e:
    print(f"[ERROR] Error loading models: {e}")
    sys.exit(1)

# Define text cleaning function
def clean_text(text):
    """Basic text cleaning"""
    text = text.lower()
    text = re.sub(f'[{string.punctuation}]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Example resumes
test_resumes = {
    "Authentic Resume": """
John Smith - Software Engineer
EXPERIENCE:
- Software Developer at Google (2018-2020): Worked on cloud infrastructure
- Full Stack Engineer at Microsoft (2020-2023): Developed Azure services
EDUCATION:
- BS Computer Science, MIT (2014-2018)
SKILLS:
- Python, Java, JavaScript, AWS, Docker, Kubernetes
- Machine Learning, Data Structures, Algorithms
PROJECTS:
- Built a microservices architecture serving 1M+ users
- Contributed to open-source projects on GitHub
    """,
    
    "Exaggerated Resume": """
Emily Johnson - Lead AI Architect & Quantum Computing Expert
EXPERIENCE:
- Chief AI Officer at Fortune 10 company (2019-2023): Led team of 500 engineers
- Senior Machine Learning Scientist at NASA (2017-2019): Developed AGI system
EDUCATION:
- PhD in AI from Stanford (2013-2017) - Youngest graduate ever
SKILLS:
- Expert in ALL programming languages, ALL frameworks, ALL technologies
- Invented 15 new machine learning algorithms
- Published 200+ papers in top journals
ACHIEVEMENTS:
- Won Nobel Prize in Computer Science (declined)
- Created technology used by entire tech industry
- Revolutionized artificial intelligence singlehandedly
    """,
    
    "Fake Resume": """
Alex Chen - CEO & Founder
EXPERIENCE:
- CEO at Apple, Google, Microsoft, Amazon (simultaneously 2015-2023)
- President of 5 countries (2010-2015)
EDUCATION:
- 20 PhDs from Harvard, MIT, Stanford, Oxford (all completed in 1 year)
- Youngest person to graduate from university at age 5
SKILLS:
- Speak 150 languages fluently
- Can code in any language without learning it
- Invented the internet, smartphones, and AI
ACHIEVEMENTS:
- Net worth: $500 trillion dollars
- Won all Nobel Prizes in same year
- Discovered cure for all diseases
- Traveled to Mars 100 times
    """
}

# Process each resume
print("\n[2/3] Classifying test resumes...")
print("\n" + "=" * 80)

for resume_name, resume_text in test_resumes.items():
    print(f"\n{resume_name}:")
    print("-" * 80)
    print(f"Text Preview: {resume_text[:150]}...")
    print("-" * 80)
    
    # Clean and vectorize
    cleaned = clean_text(resume_text)
    features = vectorizer.transform([cleaned])
    
    # Get predictions from all models
    print("\nModel Predictions:")
    predictions = {}
    for model_name, model in models.items():
        try:
            pred = model.predict(features)[0]
            # XGBoost and Neural Network return encoded labels (0, 1, 2)
            if model_name in ['XGBoost', 'Neural Network']:
                if not isinstance(pred, str):  # If not already a string label
                    import numpy as np
                    pred = label_encoder.inverse_transform(np.array([pred]))[0]
            predictions[model_name] = pred
            print(f"  - {model_name:<25} -> {pred}")
        except Exception as e:
            import traceback
            print(f"  - {model_name:<25} -> Error: {e}")
            # traceback.print_exc()  # Uncomment for debugging
    
    # Consensus vote
    pred_values = list(predictions.values())
    consensus = max(set(pred_values), key=pred_values.count)
    agreement = pred_values.count(consensus) / len(pred_values) * 100
    
    print(f"\n  CONSENSUS: {consensus} ({agreement:.0f}% agreement)")
    print("=" * 80)

# Interactive Mode
print("\n[3/3] Interactive Mode")
print("-" * 80)
print("Try your own resume! (or type 'exit' to quit)")
print()

while True:
    user_input = input("Paste resume text (or 'exit'): ").strip()
    
    if user_input.lower() in ['exit', 'quit', 'q']:
        print("\nThank you for using Resume Classifier!")
        break
    
    if not user_input:
        print("Please enter some text.\n")
        continue
    
    # Classify
    try:
        cleaned = clean_text(user_input)
        features = vectorizer.transform([cleaned])
        
        print("\nPredictions:")
        for model_name, model in models.items():
            pred = model.predict(features)[0]
            if model_name in ['XGBoost', 'Neural Network']:
                if not isinstance(pred, str):
                    import numpy as np
                    pred = label_encoder.inverse_transform(np.array([int(pred)]))[0]
            print(f"  {model_name:<25} → {pred}")
        print()
        
    except Exception as e:
        print(f"Error during prediction: {e}\n")

print("\n" + "=" * 80)
print("[SUCCESS] Demo completed successfully!")
print("=" * 80)
