import pandas as pd
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv('./data/resume_dataset.csv')
print('Unique labels:', sorted(df['label'].unique()))

le = LabelEncoder()
encoded = le.fit_transform(df['label'])
print('\nLabel mapping:')
for i, label in enumerate(le.classes_):
    print(f'  {i} -> {label}')

# Test: What is label 0 and 2?
print(f'\nLabel 0 maps to: {le.inverse_transform([0])[0]}')
print(f'Label 2 maps to: {le.inverse_transform([2])[0]}')
