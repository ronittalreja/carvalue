import json
import os
from datetime import datetime
from collections import defaultdict
import glob

class DataProcessor:
    def __init__(self):
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), "../data/raw")
        self.processed_data_dir = os.path.join(os.path.dirname(__file__), "../data/processed")
        self.snapshots_dir = os.path.join(os.path.dirname(__file__), "../data/snapshots")
        
    def load_raw_files(self):
        """Load all raw JSON files from the raw directory"""
        raw_files = glob.glob(os.path.join(self.raw_data_dir, "*.json"))
        all_listings = []
        
        for filepath in raw_files:
            print(f"Loading {filepath}...")
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_listings.extend(data)
                    else:
                        print(f"Warning: {filepath} does not contain a list")
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        
        print(f"Loaded {len(all_listings)} total listings from {len(raw_files)} files")
        return all_listings
    
    def extract_car_data(self, raw_listing):
        """Extract relevant fields from raw Cars24 listing"""
        try:
            # Extract fields based on Cars24 API response structure
            car_data = {
                "appointmentId": raw_listing.get("appointmentId"),
                "make": raw_listing.get("make"),
                "model": raw_listing.get("model"),
                "variant": raw_listing.get("variant"),
                "year": raw_listing.get("year"),
                "price": raw_listing.get("price"),
                "fuel": raw_listing.get("fuel"),
                "transmission": raw_listing.get("transmission"),
                "ownership": raw_listing.get("ownership"),
                "kms": raw_listing.get("kms"),
                "city": raw_listing.get("city"),
                "status": raw_listing.get("status"),
                "sellerType": raw_listing.get("sellerType"),
                "image": raw_listing.get("image"),
                "url": raw_listing.get("url")
            }
            
            # Only include if essential fields are present
            if car_data["make"] and car_data["model"]:
                return car_data
            return None
            
        except Exception as e:
            print(f"Error extracting car data: {e}")
            return None
    
    def clean_listings(self, raw_listings):
        """Clean and normalize listings"""
        cleaned_listings = []
        
        for listing in raw_listings:
            car_data = self.extract_car_data(listing)
            if car_data:
                cleaned_listings.append(car_data)
        
        print(f"Cleaned {len(cleaned_listings)} listings from {len(raw_listings)} raw listings")
        return cleaned_listings
    
    def create_master_dataset(self, cleaned_listings):
        """Create master dataset with all cleaned listings"""
        master_dataset = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_listings": len(cleaned_listings),
                "cities": list(set(car.get("city") for car in cleaned_listings if car.get("city"))),
                "makes": list(set(car.get("make") for car in cleaned_listings if car.get("make")))
            },
            "listings": cleaned_listings
        }
        
        return master_dataset
    
    def save_master_dataset(self, master_dataset):
        """Save master dataset to processed directory"""
        filepath = os.path.join(self.processed_data_dir, "master_dataset.json")
        
        with open(filepath, 'w') as f:
            json.dump(master_dataset, f, indent=2)
        
        print(f"Saved master dataset to {filepath}")
        return filepath
    
    def create_monthly_snapshot(self, master_dataset):
        """Create monthly snapshot"""
        current_month = datetime.now().strftime("%Y-%m")
        month_dir = os.path.join(self.snapshots_dir, current_month)
        os.makedirs(month_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(month_dir, f"snapshot_{timestamp}.json")
        
        with open(filepath, 'w') as f:
            json.dump(master_dataset, f, indent=2)
        
        print(f"Created monthly snapshot at {filepath}")
        return filepath
    
    def process_pipeline(self):
        """Run the complete data processing pipeline"""
        print("Starting data processing pipeline...")
        
        # Load raw data
        raw_listings = self.load_raw_files()
        
        # Clean listings
        cleaned_listings = self.clean_listings(raw_listings)
        
        # Create master dataset
        master_dataset = self.create_master_dataset(cleaned_listings)
        
        # Save master dataset
        self.save_master_dataset(master_dataset)
        
        # Create monthly snapshot
        self.create_monthly_snapshot(master_dataset)
        
        print("Data processing pipeline completed!")
        return master_dataset

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_pipeline()
