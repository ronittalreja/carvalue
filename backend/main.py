# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import pandas as pd
# import pickle
# import os
# from fastapi.middleware.cors import CORSMiddleware
# import requests
# import logging
# from rapidfuzz import process
# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Model download configuration
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "CarPriceModel.pkl")
# MODEL_URL = "https://drive.google.com/uc?export=download&id=1pq-8U_1sEb1yX5lnnep7xjAwcLunaUzA"

# # Download model if not exists
# if not os.path.exists(MODEL_PATH):
#     logger.info("Downloading model from Google Drive...")
#     try:
#         r = requests.get(MODEL_URL, stream=True)
#         r.raise_for_status()
#         with open(MODEL_PATH, "wb") as f:
#             for chunk in r.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         logger.info("Model downloaded successfully.")
#     except Exception as e:
#         logger.error(f"Failed to download model: {e}")

# # Create the FastAPI app instance
# app = FastAPI(title="Car Price Dashboard API")

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:8080"],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "OPTIONS"],
#     allow_headers=["*"],
# )

# # =========================
# # LOAD MODEL + DATA
# # =========================
# model = None
# df = pd.DataFrame()

# # Load model
# try:
#     with open(MODEL_PATH, "rb") as f:
#         model = pickle.load(f)
#     logger.info("Model loaded successfully")
# except FileNotFoundError:
#     logger.warning("Warning: CarPriceModel.pkl not found")
# except Exception as e:
#     logger.error(f"Error loading model: {e}")

# # =========================
# # DATA PREPROCESSING
# # =========================
# def preprocess_data():
#     """Preprocess the loaded dataset"""
#     global df
    
#     if df.empty:
#         return
    
#     logger.info(f"Original dataset shape: {df.shape}")
#     logger.info(f"Columns: {df.columns.tolist()}")
    
#     # Rename columns to standard format (case-insensitive)
#     column_mapping = {}
#     for col in df.columns:
#         col_lower = col.lower().strip()
#         if 'year' in col_lower:
#             column_mapping[col] = 'year'
#         elif 'fuel' in col_lower:
#             column_mapping[col] = 'fuel_type'
#         elif 'owner' in col_lower:
#             column_mapping[col] = 'owners'
#         elif any(word in col_lower for word in ['drive', 'transmission', 'gear']):
#             column_mapping[col] = 'transmission'
#         elif 'price' in col_lower:
#             column_mapping[col] = 'price'
#         elif any(word in col_lower for word in ['km', 'driven', 'mileage']):
#             column_mapping[col] = 'kms_driven'
#         elif any(word in col_lower for word in ['car', 'name', 'model']):
#             column_mapping[col] = 'Car Name'
    
#     df.rename(columns=column_mapping, inplace=True)
#     logger.info(f"Renamed columns: {column_mapping}")
    
#     # Ensure Car Name column exists
#     if 'Car Name' not in df.columns:
#         # Try to find the most likely car name column
#         for col in df.columns:
#             if df[col].dtype == 'object' and df[col].str.contains(' ').any():
#                 df['Car Name'] = df[col]
#                 break
    
#     if 'Car Name' in df.columns:
#         # Drop rows with missing Car Name
#         df = df.dropna(subset=['Car Name'])
#         # Convert Car Name to string
#         df['Car Name'] = df['Car Name'].astype(str)
        
#         # Extract company and model safely
#         df['company'] = df['Car Name'].apply(
#             lambda x: x.split()[0].lower() if isinstance(x, str) and len(x.split()) > 0 else "unknown"
#         )
#         df['model'] = df['Car Name'].apply(
#             lambda x: ' '.join(x.split()[1:]).lower() if isinstance(x, str) and len(x.split()) > 1 else "unknown"
#         )
        
#         logger.info(f"Companies found: {df['company'].nunique()}")
#         logger.info(f"Models found: {df['model'].nunique()}")
    
#     # Clean numeric columns
#     numeric_columns = ['year', 'kms_driven', 'owners', 'price']
#     for col in numeric_columns:
#         if col in df.columns:
#             # Convert to numeric, coerce errors to NaN
#             df[col] = pd.to_numeric(df[col], errors='coerce')
    
#     # Clean categorical columns
#     categorical_columns = ['fuel_type', 'transmission']
#     for col in categorical_columns:
#         if col in df.columns:
#             # Convert to lowercase and strip whitespace
#             df[col] = df[col].astype(str).str.lower().str.strip()
    
#     logger.info(f"Preprocessed dataset shape: {df.shape}")


# # =========================
# # LOAD DATASET (SIMPLE)
# # =========================
# def load_dataset():
#     global df
#     try:
#         df = pd.read_csv("cars24.csv", engine="python", on_bad_lines="skip", encoding="utf-8")

#         # 🔹 Fix duplicate column names
#         if df.columns.duplicated().any():
#             df = df.loc[:, ~df.columns.duplicated()]
#             logger.warning("Duplicate columns found and removed")

#         # 🔹 Optional: rename 'Unnamed: 0' to 'index' if present
#         if "Unnamed: 0" in df.columns:
#             df.rename(columns={"Unnamed: 0": "index"}, inplace=True)

#         logger.info(f"✅ Dataset loaded successfully with {len(df)} rows and {len(df.columns)} columns")
#         logger.info(f"Columns after cleaning: {df.columns.tolist()}")

#         return True
#     except Exception as e:
#         logger.error(f"❌ Failed to load dataset: {e}")
#         df = pd.DataFrame()  # ensure df is always a DataFrame
#         return False

# # Load dataset when server starts
# if load_dataset():
#     preprocess_data()
# else:
#     logger.warning("Dataset not loaded at startup. Endpoints will return errors until fixed.")

# # Preprocess the data

# # =========================
# # PYDANTIC MODELS
# # =========================
# class CarRequest(BaseModel):
#     company: str
#     car_model: str
#     year: int
#     kms_driven: float
#     fuel_type: str
#     transmission: str
#     owners: int

# # =========================
# # PREDICTION ENDPOINT
# # =========================
# @app.post("/predict")
# def predict_price(car: CarRequest):
#     if model is None:
#         raise HTTPException(status_code=500, detail="Model not loaded")
    
#     try:
#         # Map request data to match training columns
#         input_data = {
#             "company": car.company.lower(),
#             "model": car.car_model.lower(),
#             "year": car.year,
#             "kms_driven": car.kms_driven,
#             "fuel_type": car.fuel_type.lower(),
#             "transmission": car.transmission.lower(),
#             "owners": car.owners
#         }

#         input_df = pd.DataFrame([input_data])
        
#         # One-hot encode categorical features
#         X = pd.get_dummies(input_df)
        
#         # Make sure all features expected by model are present
#         X = X.reindex(columns=model.feature_names_in_, fill_value=0)
        
#         predicted_price = model.predict(X)[0]
        
#         return {"prediction": round(predicted_price, 2)}
    
#     except Exception as e:
#         logger.error(f"Prediction error: {e}")
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# # =========================
# # DATA ENDPOINTS
# # =========================
# @app.get("/companies")
# def get_companies():
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     if 'company' not in df.columns:
#         raise HTTPException(status_code=500, detail="Company data not available")
    
#     companies = df['company'].unique().tolist()
#     companies = [c for c in companies if c != 'unknown' and pd.notna(c)]
#     return {"companies": sorted(companies)}

# @app.get("/models/{company}")
# def get_models(company: str):
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     if 'company' not in df.columns or 'model' not in df.columns:
#         raise HTTPException(status_code=500, detail="Company/model data not available")
    
#     company = company.strip().lower()
#     models = df[df['company'] == company]['model'].unique().tolist()
#     models = [m for m in models if m != 'unknown' and pd.notna(m)]
#     return {"company": company, "models": sorted(models)}

# @app.get("/transmissions")
# def get_transmissions():
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     if 'transmission' not in df.columns:
#         return {"transmissions": ["manual", "automatic"]}  # Default fallback
    
#     transmissions = df['transmission'].dropna().unique().tolist()
#     return {"transmissions": sorted([t.lower() for t in transmissions if pd.notna(t)])}

# @app.get("/owners")
# def get_owners():
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     if 'owners' not in df.columns:
#         return {"owners": ["1", "2", "3", "4+"]}  # Default fallback
    
#     owners = df['owners'].dropna().unique().tolist()
#     return {"owners": sorted([str(int(o)) for o in owners if pd.notna(o)])}


# @app.get("/demand-index/{company}/{model}")
# def demand_index(company: str, model: str, transmission: str = None, ownership: str = None):
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")

#     if 'company' not in df.columns or 'model' not in df.columns:
#         raise HTTPException(status_code=500, detail="Company/model data not available")

#     company = company.lower().strip()
#     model = model.lower().strip()

#     try:
#         matches = df[
#             (df['company'].str.lower() == company) &
#             (df['model'].str.lower() == model)
#         ]

#         if transmission and 'transmission' in df.columns:
#             matches = matches[matches['transmission'].str.lower() == transmission.lower()]

#         if ownership and 'owners' in df.columns:
#             matches = matches[matches['owners'].astype(str).str.lower() == ownership.lower()]

#         if matches.empty:
#             raise HTTPException(status_code=404, detail="Car not found in dataset.")

#         # rest of your demand-index logic...
#         company_cars = df[df['company'].str.lower() == company]
#         model_counts = company_cars['model'].value_counts()
#         max_count_in_company = model_counts.iloc[0] if not model_counts.empty else 1

#         relative_popularity = (len(matches) / max_count_in_company) * 100
#         relative_popularity = max(1, min(100, round(relative_popularity, 1)))

#         return {
#             "company": company,
#             "model": model,
#             "transmission": transmission if transmission else "any",
#             "ownership": ownership if ownership else "any",
#             "demand_index": float(relative_popularity),
#             "metrics": {
#                 "matches_count": int(len(matches)),
#                 "company_total": int(len(company_cars))
#             }
#         }

#     except HTTPException:  # re-raise cleanly
#         raise
#     except Exception as e:
#         logger.error(f"Demand index calculation error: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to calculate demand index: {str(e)}")
# # =========================
# # HEALTH CHECK ENDPOINT
# # =========================
# @app.get("/health")
# def health_check():
#     if df is None or not isinstance(df, pd.DataFrame):
#         return {
#             "status": "unhealthy",
#             "model_loaded": model is not None,
#             "dataset_loaded": False,
#             "dataset_rows": 0,
#             "dataset_columns": []
#         }
    
#     return {
#         "status": "healthy",
#         "model_loaded": model is not None,
#         "dataset_loaded": not df.empty,
#         "dataset_rows": len(df) if not df.empty else 0,
#         "dataset_columns": list(df.columns) if not df.empty else []
#     }

# # =========================
# # DEBUG ENDPOINT
# # =========================
# @app.get("/debug")
# def debug_info():
#     """Debug endpoint to check data structure"""
#     if df.empty:
#         return {"error": "Dataset not loaded"}
    
#     return {
#         "shape": df.shape,
#         "columns": df.columns.tolist(),
#         "dtypes": df.dtypes.to_dict(),
#         "sample_data": df.head().to_dict(),
#         "companies_sample": df.get('company', pd.Series()).value_counts().head().to_dict() if 'company' in df.columns else {},
#         "null_counts": df.isnull().sum().to_dict()
#     }

# # =========================
# # HOME ENDPOINT
# # =========================
# @app.get("/")
# def home():
#     return {"message": "Welcome to Car Price Dashboard API"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd
import pickle
import os
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
from typing import Optional
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model download configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), "CarPriceModel.pkl")
MODEL_URL = "https://drive.google.com/uc?export=download&id=1pq-8U_1sEb1yX5lnnep7xjAwcLunaUzA"

# Download model if not exists
if not os.path.exists(MODEL_PATH):
    logger.info("Downloading model from Google Drive...")
    try:
        r = requests.get(MODEL_URL, stream=True)
        r.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Model downloaded successfully.")
    except Exception as e:
        logger.error(f"Failed to download model: {e}")

# Create the FastAPI app instance
app = FastAPI(title="Car Price Dashboard API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# =========================
# GLOBAL VARIABLES
# =========================
model = None
df = pd.DataFrame()

# =========================
# UTILITY FUNCTIONS
# =========================
def normalize_string(s):
    """Normalize string for comparison"""
    if pd.isna(s) or s is None:
        return ""
    return str(s).lower().strip()

def extract_numeric_owner(owner_str):
    """Extract numeric value from owner string"""
    if pd.isna(owner_str):
        return None
    
    owner_str = str(owner_str).lower()
    
    # Extract numbers from string
    numbers = re.findall(r'\d+', owner_str)
    if numbers:
        return int(numbers[0])
    
    # Handle special cases
    if 'first' in owner_str or '1st' in owner_str:
        return 1
    elif 'second' in owner_str or '2nd' in owner_str:
        return 2
    elif 'third' in owner_str or '3rd' in owner_str:
        return 3
    elif 'fourth' in owner_str or '4th' in owner_str or '4+' in owner_str:
        return 4
    
    return None

# =========================
# LOAD MODEL
# =========================
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except FileNotFoundError:
    logger.warning("Warning: CarPriceModel.pkl not found")
except Exception as e:
    logger.error(f"Error loading model: {e}")

# =========================
# DATA PREPROCESSING
# =========================
def preprocess_data():
    """Preprocess the loaded dataset"""
    global df
    
    if df.empty:
        return
    
    logger.info(f"Original dataset shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Rename columns to standard format (case-insensitive)
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'year' in col_lower:
            column_mapping[col] = 'year'
        elif 'fuel' in col_lower:
            column_mapping[col] = 'fuel_type'
        elif 'owner' in col_lower:
            column_mapping[col] = 'owners'
        elif any(word in col_lower for word in ['drive', 'transmission', 'gear']):
            column_mapping[col] = 'transmission'
        elif 'price' in col_lower:
            column_mapping[col] = 'price'
        elif any(word in col_lower for word in ['km', 'driven', 'mileage', 'distance']):
            column_mapping[col] = 'kms_driven'
        elif any(word in col_lower for word in ['car', 'name', 'model']):
            column_mapping[col] = 'Car Name'
    
    df.rename(columns=column_mapping, inplace=True)
    logger.info(f"Renamed columns: {column_mapping}")
    
    # Ensure Car Name column exists
    if 'Car Name' not in df.columns:
        # Try to find the most likely car name column
        for col in df.columns:
            if df[col].dtype == 'object' and df[col].str.contains(' ', na=False).any():
                df['Car Name'] = df[col]
                break
    
    if 'Car Name' in df.columns:
        # Drop rows with missing Car Name
        df = df.dropna(subset=['Car Name'])
        # Convert Car Name to string
        df['Car Name'] = df['Car Name'].astype(str)
        
        # Extract company and model safely with better normalization
        df['company'] = df['Car Name'].apply(
            lambda x: normalize_string(x.split()[0]) if isinstance(x, str) and len(x.split()) > 0 else "unknown"
        )
        df['model'] = df['Car Name'].apply(
            lambda x: normalize_string(' '.join(x.split()[1:])) if isinstance(x, str) and len(x.split()) > 1 else "unknown"
        )
        
        logger.info(f"Companies found: {df['company'].nunique()}")
        logger.info(f"Models found: {df['model'].nunique()}")
    
    # Clean numeric columns
    numeric_columns = ['year', 'kms_driven', 'price']
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, coerce errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Special handling for owners column
    if 'owners' in df.columns:
        df['owners_numeric'] = df['owners'].apply(extract_numeric_owner)
        df['owners_str'] = df['owners'].apply(normalize_string)
    
    # Clean categorical columns
    categorical_columns = ['fuel_type', 'transmission']
    for col in categorical_columns:
        if col in df.columns:
            # Convert to lowercase and strip whitespace
            df[col] = df[col].astype(str).str.lower().str.strip()
    
    logger.info(f"Preprocessed dataset shape: {df.shape}")
    
    # Debug: Show sample data
    if 'company' in df.columns and 'model' in df.columns:
        logger.info(f"Sample companies: {df['company'].value_counts().head().to_dict()}")
        logger.info(f"Sample models for first company: {df[df['company'] == df['company'].iloc[0]]['model'].value_counts().head().to_dict()}")

# =========================
# LOAD DATASET
# =========================
def load_dataset():
    global df
    try:
        df = pd.read_csv("cars24.csv", engine="python", on_bad_lines="skip", encoding="utf-8")

        # Fix duplicate column names
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()]
            logger.warning("Duplicate columns found and removed")

        # Optional: rename 'Unnamed: 0' to 'index' if present
        if "Unnamed: 0" in df.columns:
            df.rename(columns={"Unnamed: 0": "index"}, inplace=True)

        logger.info(f"✅ Dataset loaded successfully with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns after cleaning: {df.columns.tolist()}")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to load dataset: {e}")
        df = pd.DataFrame()
        return False

# Load dataset when server starts
if load_dataset():
    preprocess_data()
else:
    logger.warning("Dataset not loaded at startup. Endpoints will return errors until fixed.")

# =========================
# PYDANTIC MODELS
# =========================
class CarRequest(BaseModel):
    company: str = Field(..., min_length=1)
    car_model: str = Field(..., min_length=1)
    year: int = Field(..., ge=1900, le=2030)
    kms_driven: float = Field(..., ge=0)
    fuel_type: str
    transmission: str
    owners: int = Field(..., ge=1, le=10)

# =========================
# PREDICTION ENDPOINT
# =========================
@app.post("/predict")
def predict_price(car: CarRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Map request data to match training columns
        input_data = {
            "company": normalize_string(car.company),
            "model": normalize_string(car.car_model),
            "year": car.year,
            "kms_driven": car.kms_driven,
            "fuel_type": normalize_string(car.fuel_type),
            "transmission": normalize_string(car.transmission),
            "owners": car.owners
        }

        input_df = pd.DataFrame([input_data])
        
        # One-hot encode categorical features
        X = pd.get_dummies(input_df)
        
        # Make sure all features expected by model are present
        X = X.reindex(columns=model.feature_names_in_, fill_value=0)
        
        predicted_price = model.predict(X)[0]
        
        return {"prediction": round(predicted_price, 2)}
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail="Please check your input values and try again")

# =========================
# DATA ENDPOINTS
# =========================
@app.get("/companies")
def get_companies():
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    if 'company' not in df.columns:
        raise HTTPException(status_code=500, detail="Company data not available")
    
    companies = df['company'].unique().tolist()
    companies = [c for c in companies if c != 'unknown' and c != '' and pd.notna(c)]
    return {"companies": sorted(companies)}

@app.get("/models/{company}")
def get_models(company: str):
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    if 'company' not in df.columns or 'model' not in df.columns:
        raise HTTPException(status_code=500, detail="Company/model data not available")
    
    company = normalize_string(company)
    models = df[df['company'] == company]['model'].unique().tolist()
    models = [m for m in models if m != 'unknown' and m != '' and pd.notna(m)]
    return {"company": company, "models": sorted(models)}

@app.get("/transmissions")
def get_transmissions():
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    if 'transmission' not in df.columns:
        return {"transmissions": ["manual", "automatic"]}
    
    transmissions = df['transmission'].dropna().unique().tolist()
    transmissions = [normalize_string(t) for t in transmissions if pd.notna(t) and t != '']
    return {"transmissions": sorted(set(transmissions))}

@app.get("/owners")
def get_owners():
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    if 'owners_numeric' not in df.columns:
        return {"owners": [1, 2, 3, 4]}
    
    owners = df['owners_numeric'].dropna().unique().tolist()
    owners = [int(o) for o in owners if pd.notna(o)]
    return {"owners": sorted(owners)}

@app.get("/demand-index/{company}/{model}")
def demand_index(
    company: str, 
    model: str, 
    transmission: Optional[str] = Query(None),
    ownership: Optional[str] = Query(None)
):
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")

    if 'company' not in df.columns or 'model' not in df.columns:
        raise HTTPException(status_code=500, detail="Company/model data not available")

    company_norm = normalize_string(company)
    model_norm = normalize_string(model)

    try:
        # Start with company and model filter
        matches = df[
            (df['company'] == company_norm) &
            (df['model'] == model_norm)
        ]

        # Apply transmission filter if provided
        if transmission and 'transmission' in df.columns:
            transmission_norm = normalize_string(transmission)
            matches = matches[matches['transmission'] == transmission_norm]

        # Apply ownership filter if provided  
        if ownership and 'owners_numeric' in df.columns:
            try:
                ownership_num = int(ownership)
                matches = matches[matches['owners_numeric'] == ownership_num]
            except (ValueError, TypeError):
                # If can't convert to int, try string matching
                ownership_norm = normalize_string(ownership)
                matches = matches[matches['owners_str'] == ownership_norm]

        if matches.empty:
            # Return a user-friendly response instead of error
            return {
                "company": company,
                "model": model,
                "transmission": transmission if transmission else "any",
                "ownership": ownership if ownership else "any",
                "demand_index": 0.0,
                "message": "No data found for this combination. Please try different filters.",
                "metrics": {
                    "matches_count": 0,
                    "company_total": 0
                }
            }

        # Calculate demand index
        company_cars = df[df['company'] == company_norm]
        if company_cars.empty:
            relative_popularity = 0.0
        else:
            model_counts = company_cars['model'].value_counts()
            max_count_in_company = model_counts.iloc[0] if not model_counts.empty else 1
            relative_popularity = (len(matches) / max_count_in_company) * 100
            relative_popularity = max(1, min(100, round(relative_popularity, 1)))

        return {
            "company": company,
            "model": model,
            "transmission": transmission if transmission else "any",
            "ownership": ownership if ownership else "any",
            "demand_index": float(relative_popularity),
            "message": "Demand index calculated successfully",
            "metrics": {
                "matches_count": int(len(matches)),
                "company_total": int(len(company_cars))
            }
        }

    except Exception as e:
        logger.error(f"Demand index calculation error: {e}")
        # Return user-friendly error instead of 500
        return {
            "company": company,
            "model": model,
            "transmission": transmission if transmission else "any",
            "ownership": ownership if ownership else "any",
            "demand_index": 0.0,
            "message": "Unable to calculate demand index. Please try again.",
            "metrics": {
                "matches_count": 0,
                "company_total": 0
            }
        }

# =========================
# HEALTH CHECK ENDPOINT
# =========================
@app.get("/health")
def health_check():
    if df is None or not isinstance(df, pd.DataFrame):
        return {
            "status": "unhealthy",
            "model_loaded": model is not None,
            "dataset_loaded": False,
            "dataset_rows": 0,
            "dataset_columns": []
        }
    
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "dataset_loaded": not df.empty,
        "dataset_rows": len(df) if not df.empty else 0,
        "dataset_columns": list(df.columns) if not df.empty else []
    }

# =========================
# DEBUG ENDPOINT
# =========================
@app.get("/debug")
def debug_info():
    """Debug endpoint to check data structure"""
    if df.empty:
        return {"error": "Dataset not loaded"}
    
    debug_data = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample_data": df.head(3).to_dict(),
        "null_counts": df.isnull().sum().to_dict()
    }
    
    # Add specific car data samples
    if 'company' in df.columns:
        debug_data["companies_sample"] = df['company'].value_counts().head().to_dict()
    
    if 'model' in df.columns and 'company' in df.columns:
        # Show models for BMW as example
        bmw_models = df[df['company'] == 'bmw']['model'].value_counts().head()
        debug_data["bmw_models_sample"] = bmw_models.to_dict()
    
    if 'owners_numeric' in df.columns:
        debug_data["owners_distribution"] = df['owners_numeric'].value_counts().sort_index().to_dict()
    
    if 'transmission' in df.columns:
        debug_data["transmission_types"] = df['transmission'].value_counts().to_dict()
    
    return debug_data

# =========================
# HOME ENDPOINT  
# =========================
@app.get("/")
def home():
    return {"message": "Welcome to Car Price Dashboard API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)