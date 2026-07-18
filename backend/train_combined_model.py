import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Load the cleaned dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
cleaned_data_path = os.path.join(script_dir, "cleaned_training_data.csv")

print("Loading cleaned training data...")

# Load cleaned dataset
combined_df = pd.read_csv(cleaned_data_path)
print(f"Loaded cleaned training data: {len(combined_df)} rows")
print(f"Columns: {combined_df.columns.tolist()}")

# Convert boolean columns
for col in ['service_history', 'previous_accidents']:
    if col in combined_df.columns:
        combined_df[col] = combined_df[col].astype(bool)

print(f"Cleaned dataset: {len(combined_df)} rows")
print(f"Columns: {combined_df.columns.tolist()}")

# Prepare features for training - only 10 fields
feature_columns = ['company', 'car_model', 'year', 'kms_driven', 'fuel_type', 'transmission', 'owners']
if 'service_history' in combined_df.columns:
    feature_columns.append('service_history')
if 'previous_accidents' in combined_df.columns:
    feature_columns.append('previous_accidents')
if 'insurance' in combined_df.columns:
    feature_columns.append('insurance')

print(f"Feature columns: {feature_columns}")

# Prepare X and y
X = combined_df[feature_columns].copy()
y = combined_df['price']

# One-hot encode categorical features
categorical_cols = ['company', 'car_model', 'fuel_type', 'transmission']
if 'insurance' in X.columns:
    categorical_cols.append('insurance')

X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

print(f"Features after encoding: {X.shape[1]}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
print("Training model...")
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluate
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Train R²: {train_score:.4f}")
print(f"Test R²: {test_score:.4f}")

# Save model
model_path = os.path.join(script_dir, "CarPriceModel.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"Model saved to {model_path}")

# Save feature names
feature_names_path = os.path.join(script_dir, "feature_names.pkl")
with open(feature_names_path, 'wb') as f:
    pickle.dump(X.columns.tolist(), f)
print(f"Feature names saved to {feature_names_path}")

print("Training complete!")
