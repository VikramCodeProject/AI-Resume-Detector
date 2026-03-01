import joblib
import re
import string

# Load models
vectorizer = joblib.load('./models/tfidf_vectorizer.pkl')
xgb_model = joblib.load('./models/xgboost_model.pkl')
mlp_model = joblib.load('./models/neural_network_mlp_model.pkl')

# Clean text function
def clean_text(text):
    text = text.lower()
    text = re.sub(f'[{string.punctuation}]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Test resume
resume = "John Smith - Software Engineer at Google"
cleaned = clean_text(resume)
features = vectorizer.transform([cleaned])

print(f"Feature type: {type(features)}")
print(f"Feature shape: {features.shape}")

# Test each model
print("\nTesting XGBoost:")
try:
    pred = xgb_model.predict(features)
    print(f"  Success: {pred}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting MLP:")
try:
    pred = mlp_model.predict(features)
    print(f"  Success: {pred}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()
