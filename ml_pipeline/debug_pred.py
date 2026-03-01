import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Load XGBoost model
model = joblib.load('./models/xgboost_model.pkl')

# Load vectorizer
vectorizer = joblib.load('./models/tfidf_vectorizer.pkl')

# Test text
test_text = "software engineer with experience in python"
features = vectorizer.transform([test_text])

print(f"Features type: {type(features)}")
print(f"Features shape: {features.shape}")

# Try prediction
try:
    pred = model.predict(features)
    print(f"Prediction: {pred}")
    print(f"Prediction type: {type(pred)}")
    print(f"First element: {pred[0]}, type: {type(pred[0])}")
    
    #Try inverse transform
    le = LabelEncoder()
    le.classes_ = np.array(['Authentic', 'Exaggerated', 'Fake'])
    decoded = le.inverse_transform([int(pred[0])])
    print(f"Decoded: {decoded[0]}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
