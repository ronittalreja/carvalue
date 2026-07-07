import pandas as pd
import os

def convert_csv_to_parquet():
    """Convert CSV to Parquet format for faster loading"""
    csv_path = os.path.join(os.path.dirname(__file__), "cars24.csv")
    parquet_path = os.path.join(os.path.dirname(__file__), "cars24.parquet")
    
    print(f"Reading CSV from {csv_path}...")
    df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip", encoding="utf-8")
    
    # Fix duplicate column names
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]
        print("Duplicate columns removed")
    
    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Converting to Parquet...")
    
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    
    print(f"✅ Successfully converted to Parquet: {parquet_path}")
    print(f"Original CSV size: {os.path.getsize(csv_path) / 1024 / 1024:.2f} MB")
    print(f"Parquet file size: {os.path.getsize(parquet_path) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    convert_csv_to_parquet()
