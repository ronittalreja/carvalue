import pandas as pd
import numpy as np
import json
import os

# Load the combined dataset from training script
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "neww data")

print("Loading combined datasets for cleaning...")

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
# Convert price from lakhs to INR
df2['price'] = df2['price_lakhs'] * 100000
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
# Clean price column - handle "Make Your Offer" and convert to INR
def clean_price(price_str):
    if pd.isna(price_str):
        return np.nan
    price_str = str(price_str).strip()
    if 'Make Your Offer' in price_str or 'make your offer' in price_str:
        return np.nan
    # Extract numeric value
    price_str = price_str.replace('₹', '').replace(',', '').replace('Lakh', '00000').replace('Crore', '0000000')
    try:
        return float(price_str)
    except:
        return np.nan

df3['price'] = df3['price'].apply(clean_price)
df3['color'] = 'unknown'
df3['service_history'] = False
df3['previous_accidents'] = False
df3['car_type'] = 'unknown'

# Select common columns for training
training_columns = ['company', 'car_model', 'year', 'kms_driven', 'fuel_type', 'transmission', 'owners', 'service_history', 'previous_accidents', 'insurance', 'price']

# Get available columns from each dataframe
df1_cols = [col for col in training_columns if col in df1.columns]
df2_cols = [col for col in training_columns if col in df2.columns]
df3_cols = [col for col in training_columns if col in df3.columns]

df1_selected = df1[df1_cols].copy()
df2_selected = df2[df2_cols].copy()
df3_selected = df3[df3_cols].copy()

# Combine datasets
combined_df = pd.concat([df1_selected, df2_selected, df3_selected], ignore_index=True)
print(f"Original combined dataset: {len(combined_df)} rows")

# Normalize string columns
for col in ['company', 'car_model', 'fuel_type', 'transmission', 'insurance']:
    if col in combined_df.columns:
        combined_df[col] = combined_df[col].astype(str).str.lower().str.strip()

# Normalize company names
def normalize_company_name(company):
    company = str(company).lower().strip()
    if company == 'maruti suzuki':
        return 'maruti'
    return company

combined_df['company'] = combined_df['company'].apply(normalize_company_name)

# Remove brands with insufficient data (causing prediction issues)
brands_to_remove = ['porsche', 'ssangyong', 'mitsubishi']
before_removal = len(combined_df)
combined_df = combined_df[~combined_df['company'].isin(brands_to_remove)]
print(f"Removed {before_removal - len(combined_df)} rows from brands with insufficient data: {brands_to_remove}")

# Clean numeric columns
combined_df['year'] = pd.to_numeric(combined_df['year'], errors='coerce')
combined_df['kms_driven'] = pd.to_numeric(combined_df['kms_driven'], errors='coerce')
combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce')
combined_df['owners'] = pd.to_numeric(combined_df['owners'], errors='coerce')

# Remove rows with missing critical values
combined_df = combined_df.dropna(subset=['company', 'car_model', 'year', 'kms_driven', 'price'])
print(f"After removing missing critical values: {len(combined_df)} rows")

# Basic sanity checks
print("\n=== BASIC DATA QUALITY CHECKS ===")
print(f"Price range: ₹{combined_df['price'].min():,.0f} to ₹{combined_df['price'].max():,.0f}")
print(f"Year range: {combined_df['year'].min()} to {combined_df['year'].max()}")
print(f"KM range: {combined_df['kms_driven'].min():,.0f} to {combined_df['kms_driven'].max():,.0f}")

# Remove obviously unrealistic entries
print("\n=== REMOVING OBVIOUSLY UNREALISTIC ENTRIES ===")
before_count = len(combined_df)

# Remove cars with impossible years (before 1990 or after 2025)
combined_df = combined_df[(combined_df['year'] >= 1990) & (combined_df['year'] <= 2025)]
print(f"After removing invalid years: {len(combined_df)} rows (removed {before_count - len(combined_df)})")
before_count = len(combined_df)

# Remove cars with impossible KM (negative or over 500,000 km)
combined_df = combined_df[(combined_df['kms_driven'] >= 0) & (combined_df['kms_driven'] <= 500000)]
print(f"After removing invalid KM: {len(combined_df)} rows (removed {before_count - len(combined_df)})")
before_count = len(combined_df)

# Remove cars with impossible prices (under ₹50,000 or over ₹5 crore)
combined_df = combined_df[(combined_df['price'] >= 50000) & (combined_df['price'] <= 50000000)]
print(f"After removing invalid prices: {len(combined_df)} rows (removed {before_count - len(combined_df)})")
before_count = len(combined_df)

# Luxury brand handling
luxury_brands = ['porsche', 'mercedes', 'bmw', 'audi', 'jaguar', 'landrover', 'lexus', 'volvo']
print(f"\n=== LUXURY BRAND PRICE CLEANING ===")
for brand in luxury_brands:
    brand_data = combined_df[combined_df['company'] == brand]
    if len(brand_data) > 5:  # Only if we have enough data
        # Remove bottom 5% as they're likely underpriced
        min_reasonable = brand_data['price'].quantile(0.05)
        removed = len(combined_df[(combined_df['company'] == brand) & (combined_df['price'] < min_reasonable)])
        combined_df = combined_df[~((combined_df['company'] == brand) & (combined_df['price'] < min_reasonable))]
        print(f"{brand}: removed {removed} underpriced entries (min price: ₹{min_reasonable:,.0f})")

# IQR-based outlier removal by brand
print(f"\n=== IQR-BASED OUTLIER REMOVAL BY BRAND ===")
total_iqr_removed = 0
for brand in combined_df['company'].unique():
    brand_data = combined_df[combined_df['company'] == brand]
    if len(brand_data) > 10:  # Only if enough data
        Q1 = brand_data['price'].quantile(0.25)
        Q3 = brand_data['price'].quantile(0.75)
        IQR = Q3 - Q1
        # Use 2.5*IQR for more conservative removal
        lower_bound = Q1 - 2.5 * IQR
        upper_bound = Q3 + 2.5 * IQR
        
        brand_outliers = brand_data[(brand_data['price'] < lower_bound) | (brand_data['price'] > upper_bound)]
        if len(brand_outliers) > 0:
            combined_df = combined_df[~((combined_df['company'] == brand) & ((combined_df['price'] < lower_bound) | (combined_df['price'] > upper_bound)))]
            print(f"{brand}: removed {len(brand_outliers)} outliers (range: ₹{lower_bound:,.0f} - ₹{upper_bound:,.0f})")
            total_iqr_removed += len(brand_outliers)

print(f"\nTotal IQR outliers removed: {total_iqr_removed}")

# Final statistics
print(f"\n=== FINAL CLEANED DATASET STATISTICS ===")
print(f"Total rows: {len(combined_df)}")
print(f"Total companies: {combined_df['company'].nunique()}")
print(f"Price range: ₹{combined_df['price'].min():,.0f} to ₹{combined_df['price'].max():,.0f}")
print(f"Average price: ₹{combined_df['price'].mean():,.0f}")
print(f"Median price: ₹{combined_df['price'].median():,.0f}")

# Show price distribution by company
print(f"\n=== PRICE DISTRIBUTION BY TOP 10 COMPANIES ===")
top_companies = combined_df['company'].value_counts().head(10).index
for company in top_companies:
    company_data = combined_df[combined_df['company'] == company]
    print(f"{company}: {len(company_data)} cars, price range ₹{company_data['price'].min():,.0f} - ₹{company_data['price'].max():,.0f}, avg ₹{company_data['price'].mean():,.0f}")

# Save cleaned dataset
cleaned_path = os.path.join(script_dir, "cleaned_training_data.csv")
combined_df.to_csv(cleaned_path, index=False)
print(f"\n✅ Cleaned dataset saved to {cleaned_path}")

# Save summary statistics
summary = {
    'original_rows': len(pd.concat([df1_selected, df2_selected, df3_selected], ignore_index=True)),
    'cleaned_rows': len(combined_df),
    'removed_rows': len(pd.concat([df1_selected, df2_selected, df3_selected], ignore_index=True)) - len(combined_df),
    'companies': combined_df['company'].nunique(),
    'price_range': [float(combined_df['price'].min()), float(combined_df['price'].max())],
    'avg_price': float(combined_df['price'].mean()),
    'median_price': float(combined_df['price'].median())
}

summary_path = os.path.join(script_dir, "cleaning_summary.json")
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
print(f"✅ Cleaning summary saved to {summary_path}")
