# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import pandas as pd
# import pickle
# import os
# from fastapi.middleware.cors import CORSMiddleware

# # Create the FastAPI app instance
# app = FastAPI(title="Car Price Dashboard API")

# # Fix CORS - only define once and include more permissive origins
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
# try:
#     with open("CarPriceModel.pkl", "rb") as f:
#         model = pickle.load(f)
#     print("Model loaded successfully")
# except FileNotFoundError:
#     print("Warning: CarPriceModel.pkl not found")
#     model = None

# try:
#     df = pd.read_excel("cars24.csv")
#     print(f"Dataset loaded successfully with {len(df)} rows")
# except FileNotFoundError:
#     print("Warning: cars24.csv not found")
#     df = pd.DataFrame()

# # =========================
# # SAFE EXTRACTION OF COMPANY AND MODEL
# # =========================
# if not df.empty:
#     # Drop rows with missing Car Name
#     df = df.dropna(subset=['Car Name'])
#     # Convert Car Name to string
#     df['Car Name'] = df['Car Name'].astype(str)

#     # Extract company and model safely
#     df['company'] = df['Car Name'].apply(lambda x: x.split()[0].lower() if isinstance(x, str) else "unknown")
#     df['model'] = df['Car Name'].apply(lambda x: ' '.join(x.split()[1:]).lower() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
    
#     print(f"Companies found: {df['company'].nunique()}")
#     print(f"Models found: {df['model'].nunique()}")

# # =========================
# # PREDICTION ENDPOINT
# # =========================
# class CarRequest(BaseModel):
#     company: str
#     car_model: str
#     year: int
#     kms_driven: float
#     fuel_type: str
#     transmission: str
#     owners: int

# @app.post("/predict")
# def predict_price(car: CarRequest):
#     if model is None:
#         raise HTTPException(status_code=500, detail="Model not loaded")
    
#     # Map request data to match training columns
#     input_data = {
#         "company": car.company.lower(),
#         "model": car.car_model.lower(),
#         "year": car.year,
#         "kms_driven": car.kms_driven,
#         "fuel_type": car.fuel_type.lower(),
#         "transmission": car.transmission.lower(),
#         "owners": car.owners
#     }

#     input_df = pd.DataFrame([input_data])
    
#     # One-hot encode categorical features
#     X = pd.get_dummies(input_df)
    
#     # Make sure all features expected by model are present
#     X = X.reindex(columns=model.feature_names_in_, fill_value=0)
    
#     predicted_price = model.predict(X)[0]
    
#     return {"prediction": round(predicted_price, 2)}

# # =========================
# # DEMAND INDEX ENDPOINTS
# # =========================
# @app.get("/companies")
# def get_companies():
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     companies = df['company'].unique().tolist()
#     # Remove 'unknown' if present
#     companies = [c for c in companies if c != 'unknown']
#     return {"companies": companies}

# @app.get("/models/{company}")
# def get_models(company: str):
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     company = company.strip().lower()
#     models = df[df['company'] == company]['model'].unique().tolist()
#     # Remove 'unknown' if present
#     models = [m for m in models if m != 'unknown']
#     return {"company": company, "models": models}

# @app.get("/demand-index/{company}/{model}")
# def demand_index(company: str, model: str):
#     if df.empty:
#         raise HTTPException(status_code=500, detail="Dataset not loaded")
    
#     company = company.strip().lower()
#     model = model.strip().lower()
    
#     print(f"Searching for company: '{company}', model: '{model}'")

#     # Find exact matches for this car model
#     exact_matches = df[(df['company'] == company) & (df['model'] == model)]
    
#     if exact_matches.empty:
#         # Let's also check what companies and models we actually have
#         available_companies = df['company'].unique()[:10]  # First 10 for debugging
#         print(f"Available companies (first 10): {available_companies}")
        
#         company_subset = df[df['company'] == company]
#         if company_subset.empty:
#             raise HTTPException(status_code=404, detail=f"Company '{company}' not found")
#         else:
#             available_models = company_subset['model'].unique()[:10]
#             print(f"Available models for {company} (first 10): {available_models}")
#             raise HTTPException(status_code=404, detail=f"Model '{model}' not found for company '{company}'")

#     # Get all models from the same company for comparison
#     company_cars = df[df['company'] == company]
    
#     # Calculate multiple demand metrics
#     exact_count = len(exact_matches)
#     company_count = len(company_cars)
#     total_count = len(df)
    
#     # Method 1: Percentage within company (more meaningful)
#     company_percentage = (exact_count / company_count) * 100
    
#     # Method 2: Market share percentage  
#     market_share = (exact_count / total_count) * 100
    
#     # Method 3: Relative popularity score (normalized to 0-100)
#     # Find the most popular model in this company
#     model_counts = company_cars['model'].value_counts()
#     max_count_in_company = model_counts.iloc[0] if not model_counts.empty else 1
#     relative_popularity = (exact_count / max_count_in_company) * 100
    
#     # Method 4: Weighted demand index combining multiple factors
#     # Base score from company percentage (30%)
#     # Market position within company (40%)  
#     # Overall market presence (30%)
    
#     # Rank within company (1 = most popular in company)
#     company_rank = (model_counts.index.tolist().index(model) + 1) if model in model_counts.index else len(model_counts)
#     total_models_in_company = len(model_counts)
    
#     # Convert rank to score (higher rank = lower score)
#     rank_score = max(0, 100 - ((company_rank - 1) / max(1, total_models_in_company - 1)) * 60)
    
#     # Combine metrics for final weighted score
#     weighted_score = (
#         company_percentage * 0.3 +  # 30% from company share
#         rank_score * 0.4 +          # 40% from rank within company  
#         min(market_share * 10, 30) * 0.3  # 30% from market presence (capped)
#     )
    
#     # Ensure score is between 0-100
#     final_score = max(1, min(100, round(weighted_score, 1)))
    
#     print(f"Demand metrics calculated:")
#     print(f"  Exact matches: {exact_count}")
#     print(f"  Company percentage: {company_percentage:.1f}%")
#     print(f"  Market share: {market_share:.1f}%") 
#     print(f"  Relative popularity: {relative_popularity:.1f}%")
#     print(f"  Company rank: {company_rank}/{total_models_in_company}")
#     print(f"  Final weighted score: {final_score}")

#     return {
#         "company": company,
#         "model": model, 
#         "demand_index": final_score,
#         "metrics": {
#             "exact_listings": exact_count,
#             "company_share_percent": round(company_percentage, 1),
#             "market_share_percent": round(market_share, 2),
#             "company_rank": company_rank,
#             "total_company_models": total_models_in_company
#         }
#     }

# # =========================
# # HEALTH CHECK ENDPOINT
# # =========================
# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "model_loaded": model is not None,
#         "dataset_loaded": not df.empty,
#         "dataset_rows": len(df) if not df.empty else 0
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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import pickle
import os
from fastapi.middleware.cors import CORSMiddleware

# Create the FastAPI app instance
app = FastAPI(title="Car Price Dashboard API")

# Fix CORS - only define once and include more permissive origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# =========================
# LOAD MODEL + DATA
# =========================
try:
    with open("CarPriceModel.pkl", "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully")
except FileNotFoundError:
    print("Warning: CarPriceModel.pkl not found")
    model = None

print(type(model))
try:
    df = pd.read_excel("cars24.csv")
    print(f"Dataset loaded successfully with {len(df)} rows")
except FileNotFoundError:
    print("Warning: cars24.csv not found")
    df = pd.DataFrame()

# =========================
# SAFE EXTRACTION OF COMPANY AND MODEL
# =========================
if not df.empty:
    # Drop rows with missing Car Name
    df = df.dropna(subset=['Car Name'])
    # Convert Car Name to string
    df['Car Name'] = df['Car Name'].astype(str)

    # Extract company and model safely
    df['company'] = df['Car Name'].apply(lambda x: x.split()[0].lower() if isinstance(x, str) else "unknown")
    df['model'] = df['Car Name'].apply(lambda x: ' '.join(x.split()[1:]).lower() if isinstance(x, str) and len(x.split()) > 1 else "unknown")
    
    print(f"Companies found: {df['company'].nunique()}")
    print(f"Models found: {df['model'].nunique()}")

# =========================
# PREDICTION ENDPOINT
# =========================
class CarRequest(BaseModel):
    company: str
    car_model: str
    year: int
    kms_driven: float
    fuel_type: str
    transmission: str
    owners: int

@app.post("/predict")
def predict_price(car: CarRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Map request data to match training columns
    input_data = {
        "company": car.company.lower(),
        "model": car.car_model.lower(),
        "year": car.year,
        "kms_driven": car.kms_driven,
        "fuel_type": car.fuel_type.lower(),
        "transmission": car.transmission.lower(),
        "owners": car.owners
    }

    input_df = pd.DataFrame([input_data])
    
    # One-hot encode categorical features
    X = pd.get_dummies(input_df)
    
    # Make sure all features expected by model are present
    X = X.reindex(columns=model.feature_names_in_, fill_value=0)
    
    predicted_price = model.predict(X)[0]
    
    return {"prediction": round(predicted_price, 2)}

# =========================
# DEMAND INDEX ENDPOINTS
# =========================
@app.get("/companies")
def get_companies():
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    companies = df['company'].unique().tolist()
    # Remove 'unknown' if present
    companies = [c for c in companies if c != 'unknown']
    return {"companies": companies}

@app.get("/models/{company}")
def get_models(company: str):
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    company = company.strip().lower()
    models = df[df['company'] == company]['model'].unique().tolist()
    # Remove 'unknown' if present
    models = [m for m in models if m != 'unknown']
    return {"company": company, "models": models}

# Mapping dictionaries for transmission and ownership (adjust as per your dataset)
transmission_map = {
    "manual": "manual",
    "automatic": "automatic",
    "amt": "amt",
    "cvt": "cvt",
    "dct": "dct"
}

ownership_map = {
    "first": 1,
    "second": 2,
    "third+": 3,
    "4th+": 4
}

@app.get("/demand-index/{company}/{model}")
def demand_index(
    company: str,
    model: str,
    transmission: str = None,  # optional
    ownership: str = None      # optional
):
    company = company.lower().strip()
    model = model.lower().strip()
    transmission_val = transmission_map.get(transmission.lower(), None) if transmission else None
    ownership_val = ownership_map.get(ownership.lower(), None) if ownership else None

    # Filter dataset
    matches = df[
        (df['company'].str.lower() == company) &
        (df['model'].str.lower() == model)
    ]
    if transmission_val:
        matches = matches[matches['transmission'].str.lower() == transmission_val]
    if ownership_val:
        matches = matches[matches['owners'] == ownership_val]

    if matches.empty:
        raise HTTPException(status_code=404, detail="Car not found in dataset.")

    # Get all models from the same company for normalization
    company_cars = df[df['company'].str.lower() == company]
    model_counts = company_cars['model'].value_counts()
    max_count_in_company = model_counts.iloc[0] if not model_counts.empty else 1

    # Relative popularity score (0-100)
    relative_popularity = (len(matches) / max_count_in_company) * 100
    relative_popularity = max(1, min(100, round(relative_popularity, 1)))  # clamp to 1-100

    return {
    "company": company,
    "model": model,
    "transmission": transmission_val,
    "ownership": ownership_val,
    "demand_index": float(relative_popularity),  # convert to Python float
    "metrics": {
        "matches_count": int(len(matches)),  # convert to int
        # include other metrics if needed, make sure to cast numpy types
    }
}


# =========================
# HEALTH CHECK ENDPOINT
# =========================
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "dataset_loaded": not df.empty,
        "dataset_rows": len(df) if not df.empty else 0
    }

# =========================
# HOME ENDPOINT
# =========================
@app.get("/")
def home():
    return {"message": "Welcome to Car Price Dashboard API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

