import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Load the three datasets
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "neww data")

print("Loading datasets...")

# Load realistic_car_data.csv
df1 = pd.read_csv(os.path.join(data_dir, "realistic_car_data.csv"))
print(f"Loaded realistic_car_data.csv: {len(df1)} rows")
print(f"Columns: {df1.columns.tolist()}")

# Load Cars24.csv
df2 = pd.read_csv(os.path.join(data_dir, "Cars24.csv"))
print(f"Loaded Cars24.csv: {len(df2)} rows")
print(f"Columns: {df2.columns.tolist()}")

# Load car_details.csv
df3 = pd.read_csv(os.path.join(data_dir, "car_details.csv"))
print(f"Loaded car_details.csv: {len(df3)} rows")
print(f"Columns: {df3.columns.tolist()}")

# Standardize column names for df1 (realistic_car_data.csv)
df1 = df1.rename(columns={
    'Brand': 'company',
    'Model': 'car_model',
    'Year': 'year',
    'Odometer Reading (km)': 'kms_driven',
    'Fuel Type': 'fuel_type',
    'Transmission Type': 'transmission',
    'Color': 'color',
    'Number of Owners': 'owners',
    'Service History': 'service_history',
    'Location': 'location',
    'Previous Accidents': 'previous_accidents',
    'Engine Capacity (L)': 'engine_capacity',
    'Car Type': 'car_type',
    'Insurance Type': 'insurance',
    'Price (INR)': 'price'
})

# Standardize column names for df2 (Cars24.csv)
df2 = df2.rename(columns={
    'Year': 'year',
    'Car Model': 'car_model',
    'Car Variant': 'car_variant',
    'KM Driven': 'kms_driven',
    'Fuel Type': 'fuel_type',
    'Transmission Type': 'transmission',
    'Ownership': 'ownership',
    'Price(in Lakhs)': 'price_lakhs',
    'Location': 'location'
})

# Extract company from car_model for df2
df2['company'] = df2['car_model'].apply(lambda x: str(x).split()[0].lower().strip() if isinstance(x, str) and len(x.split()) > 0 else "unknown")
df2['car_model'] = df2['car_model'].apply(lambda x: ' '.join(str(x).split()[1:]).lower().strip() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
# Convert price from lakhs to actual price
df2['price'] = df2['price_lakhs'] * 100000
# Convert ownership to numeric
df2['owners'] = df2['ownership'].apply(lambda x: int(str(x).split()[0]) if isinstance(x, str) and str(x).split()[0].isdigit() else 1)
# Add missing columns with default values
df2['color'] = 'unknown'
df2['service_history'] = False
df2['previous_accidents'] = False
df2['engine_capacity'] = 0
df2['car_type'] = 'unknown'
df2['insurance'] = 'unknown'

# Standardize column names for df3 (car_details.csv)
df3 = df3.rename(columns={
    'vehical_name': 'car_name',
    'Registration Year ': 'year',
    'Insurance ': 'insurance',
    'Fuel Type ': 'fuel_type',
    'Seats ': 'seats',
    'Kms Driven ': 'kms_driven',
    'RTO': 'location',
    'Ownership ': 'ownership',
    'Engine Displacement ': 'engine_capacity',
    'Transmission ': 'transmission',
    'Year of Manufacture ': 'manufacture_year',
    'Engine ': 'engine',
    'Power ': 'power',
    'Drive Type ': 'drive_type',
    'Mileage ': 'mileage',
    'Fuel ': 'fuel',
    'new_vehical_price': 'new_price',
    'vehical_price': 'price',
    'other_features': 'other_features'
})

# Extract company and model from car_name for df3
df3['company'] = df3['car_name'].apply(lambda x: str(x).split()[0].lower().strip() if isinstance(x, str) and len(x.split()) > 0 else "unknown")
df3['car_model'] = df3['car_name'].apply(lambda x: ' '.join(str(x).split()[1:]).lower().strip() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
# Clean kms_driven (remove commas and "Kms")
df3['kms_driven'] = df3['kms_driven'].apply(lambda x: float(str(x).replace(',', '').replace('Kms', '').strip()) if isinstance(x, str) else 0)
# Convert ownership to numeric
df3['owners'] = df3['ownership'].apply(lambda x: 1 if 'first' in str(x).lower() else 2 if 'second' in str(x).lower() else 3 if 'third' in str(x).lower() else 4 if 'fourth' in str(x).lower() else 1)
# Clean price (remove currency symbols and text)
def clean_price(x):
    if isinstance(x, str):
        # Remove currency symbols and text
        cleaned = str(x).replace('₹', '').replace('Lakh', '').replace(',', '').replace('Make Your Offer', '').strip()
        try:
            return float(cleaned) * 100000
        except:
            return 0
    elif isinstance(x, (int, float)):
        return x * 100000 if x < 1000 else x  # If already in lakhs, convert
    else:
        return 0

df3['price'] = df3['price'].apply(clean_price)
# Add missing columns with default values
df3['color'] = 'unknown'
df3['service_history'] = False
df3['previous_accidents'] = False
df3['car_type'] = 'unknown'

# Select common columns for all datasets
common_columns = ['company', 'car_model', 'year', 'kms_driven', 'fuel_type', 'transmission', 'owners', 'price']

# Select additional columns where available
additional_columns = ['color', 'service_history', 'previous_accidents', 'engine_capacity', 'car_type', 'insurance', 'location']

# Prepare each dataset
df1_selected = df1[common_columns + [col for col in additional_columns if col in df1.columns]].copy()
df2_selected = df2[common_columns + [col for col in additional_columns if col in df2.columns]].copy()
df3_selected = df3[common_columns + [col for col in additional_columns if col in df3.columns]].copy()

print(f"df1_selected: {len(df1_selected)} rows")
print(f"df2_selected: {len(df2_selected)} rows")
print(f"df3_selected: {len(df3_selected)} rows")

# Combine datasets
combined_df = pd.concat([df1_selected, df2_selected, df3_selected], ignore_index=True)
print(f"Combined dataset: {len(combined_df)} rows")

# Clean data
combined_df = combined_df.dropna(subset=['price'])
combined_df = combined_df[combined_df['price'] > 0]
# Convert year to numeric
combined_df['year'] = pd.to_numeric(combined_df['year'], errors='coerce')
combined_df = combined_df[combined_df['year'] >= 2000]
# Clean engine_capacity (extract numeric value)
if 'engine_capacity' in combined_df.columns:
    combined_df['engine_capacity'] = combined_df['engine_capacity'].apply(lambda x: float(str(x).replace('cc', '').replace('L', '').strip()) if isinstance(x, str) else float(x) if pd.notna(x) else 0)
# Clean kms_driven
combined_df['kms_driven'] = pd.to_numeric(combined_df['kms_driven'], errors='coerce').fillna(0)

# Normalize string columns
for col in ['company', 'car_model', 'fuel_type', 'transmission', 'color', 'car_type', 'insurance', 'location']:
    if col in combined_df.columns:
        combined_df[col] = combined_df[col].astype(str).str.lower().str.strip()

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
