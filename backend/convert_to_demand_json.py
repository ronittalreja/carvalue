import pandas as pd
import json
import os

# Load the cleaned dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
cleaned_data_path = os.path.join(script_dir, "cleaned_training_data.csv")

print("Loading cleaned training data...")
df = pd.read_csv(cleaned_data_path)
print(f"Loaded {len(df)} rows")

# Convert to JSON format optimized for demand index
# Keep only the columns needed for demand index calculations
demand_columns = ['company', 'car_model', 'year', 'kms_driven', 'fuel_type', 'transmission', 'owners', 'price']
demand_df = df[demand_columns].copy()

# Convert to list of dictionaries
demand_data = demand_df.to_dict(orient='records')

# Save to JSON
demand_json_path = os.path.join(script_dir, "demand_data.json")
with open(demand_json_path, 'w') as f:
    json.dump(demand_data, f, indent=2)

file_size_mb = os.path.getsize(demand_json_path) / (1024 * 1024)
print(f"✅ Demand data saved to {demand_json_path}")
print(f"File size: {file_size_mb:.2f} MB")
print(f"Total records: {len(demand_data)}")

# Print sample data
print(f"\nSample record:")
print(json.dumps(demand_data[0], indent=2))
