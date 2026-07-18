import pandas as pd
import json
import os

# Load the combined dataset from training script
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "neww data")

# Load all three datasets and combine them
print("Loading combined datasets...")

# Load realistic_car_data.csv
df1 = pd.read_csv(os.path.join(data_dir, "realistic_car_data.csv"))
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

# Load Cars24.csv
df2 = pd.read_csv(os.path.join(data_dir, "Cars24.csv"))
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
df2['company'] = df2['car_model'].apply(lambda x: str(x).split()[0].lower().strip() if isinstance(x, str) and len(x.split()) > 0 else "unknown")
df2['car_model'] = df2['car_model'].apply(lambda x: ' '.join(str(x).split()[1:]).lower().strip() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
df2['color'] = 'unknown'
df2['service_history'] = False
df2['previous_accidents'] = False
df2['engine_capacity'] = 0
df2['car_type'] = 'unknown'
df2['insurance'] = 'unknown'

# Load car_details.csv
df3 = pd.read_csv(os.path.join(data_dir, "car_details.csv"))
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
df3['company'] = df3['car_name'].apply(lambda x: str(x).split()[0].lower().strip() if isinstance(x, str) and len(x.split()) > 0 else "unknown")
df3['car_model'] = df3['car_name'].apply(lambda x: ' '.join(str(x).split()[1:]).lower().strip() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
df3['color'] = 'unknown'
df3['service_history'] = False
df3['previous_accidents'] = False
df3['car_type'] = 'unknown'

# Select common columns
common_columns = ['company', 'car_model']
df1_selected = df1[common_columns].copy()
df2_selected = df2[common_columns].copy()
df3_selected = df3[common_columns].copy()

# Combine datasets
combined_df = pd.concat([df1_selected, df2_selected, df3_selected], ignore_index=True)
print(f"Combined dataset: {len(combined_df)} rows")

# Normalize string columns
for col in ['company', 'car_model']:
    combined_df[col] = combined_df[col].astype(str).str.lower().str.strip()

# Normalize company names (merge similar names)
def normalize_company_name(company):
    company = str(company).lower().strip()
    # Merge maruti suzuki into maruti
    if company == 'maruti suzuki':
        return 'maruti'
    # Add other normalizations if needed
    return company

combined_df['company'] = combined_df['company'].apply(normalize_company_name)

# Extract unique companies
companies = combined_df['company'].unique().tolist()
# Filter out invalid entries: unknown, empty, nan, and years (numeric values)
companies = [c for c in companies if c != 'unknown' and c != '' and c != 'nan' and not c.replace('.', '').isdigit()]
companies = sorted(companies)

# Build models dictionary
models_dict = {}
for company in companies:
    company_models = combined_df[combined_df['company'] == company]['car_model'].unique().tolist()
    company_models = [m for m in company_models if m != 'unknown' and m != '' and m != 'nan']
    models_dict[company] = sorted(company_models)

# Save to JSON files
companies_json_path = os.path.join(script_dir, "companies.json")
models_json_path = os.path.join(script_dir, "company_models.json")

with open(companies_json_path, 'w') as f:
    json.dump(companies, f, indent=2)

with open(models_json_path, 'w') as f:
    json.dump(models_dict, f, indent=2)

print(f"✅ Saved {len(companies)} companies to {companies_json_path}")
print(f"✅ Saved models for {len(models_dict)} companies to {models_json_path}")
print(f"Total models: {sum(len(v) for v in models_dict.values())}")
