import pandas as pd
import json
import os

# Load the dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, "cars24.parquet")
CSV_PATH = os.path.join(script_dir, "cars24.csv")

# Try to load from Parquet first
if os.path.exists(DATA_PATH):
    print(f"Loading from Parquet: {DATA_PATH}")
    df = pd.read_parquet(DATA_PATH, engine="pyarrow")
elif os.path.exists(CSV_PATH):
    print(f"Loading from CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, engine="python", on_bad_lines="skip", encoding="utf-8")
else:
    print("No dataset found!")
    exit(1)

print(f"Dataset loaded with {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Check if company and model columns exist
if 'company' in df.columns and 'model' in df.columns:
    # Dataset already has company and model columns
    companies = df['company'].unique().tolist()
    companies = [c for c in companies if c != 'unknown' and c != '' and pd.notna(c)]
    companies = sorted([str(c).lower().strip() for c in companies])
    
    # Build models dictionary
    models_dict = {}
    for company in companies:
        company_models = df[df['company'].str.lower() == company]['model'].unique().tolist()
        company_models = [m for m in company_models if m != 'unknown' and m != '' and pd.notna(m)]
        models_dict[company] = sorted([str(m).lower().strip() for m in company_models])
    
elif 'Car Name' in df.columns:
    # Need to extract company and model from Car Name
    df['company'] = df['Car Name'].apply(lambda x: str(x).split()[0].lower().strip() if isinstance(x, str) and len(x.split()) > 0 else "unknown")
    df['model'] = df['Car Name'].apply(lambda x: ' '.join(str(x).split()[1:]).lower().strip() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
    
    companies = df['company'].unique().tolist()
    companies = [c for c in companies if c != 'unknown' and c != '' and pd.notna(c)]
    companies = sorted(companies)
    
    # Build models dictionary
    models_dict = {}
    for company in companies:
        company_models = df[df['company'] == company]['model'].unique().tolist()
        company_models = [m for m in company_models if m != 'unknown' and m != '' and pd.notna(m)]
        models_dict[company] = sorted(company_models)
else:
    print("No company/model columns found!")
    exit(1)

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
