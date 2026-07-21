import json
import os
import glob
from datetime import datetime

class DatasetBuilder:
    def __init__(self):
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), "../data/raw")
        self.processed_data_dir = os.path.join(os.path.dirname(__file__), "../data/processed")
        
    def load_raw_files(self):
        """Load all raw JSON files from the raw directory"""
        raw_files = glob.glob(os.path.join(self.raw_data_dir, "*.json"))
        print(f"Found {len(raw_files)} raw JSON files")
        return raw_files
    
    def extract_cars_from_response(self, api_response):
        """Extract car objects from a single Cars24 API response"""
        cars = []
        
        try:
            # Try new API structure first (content at root level)
            if "content" in api_response:
                content = api_response["content"]
                
                for car in content:
                    # New API structure has car data directly in content array
                    car_data = {
                        "appointmentId": car.get("appointmentId"),
                        "make": car.get("make"),
                        "model": car.get("model"),
                        "variant": car.get("variant"),
                        "year": car.get("year"),
                        "price": car.get("listingPrice"),
                        "fuelType": car.get("fuelType"),
                        "transmission": car.get("transmissionType", {}).get("value") if car.get("transmissionType") else None,
                        "ownership": car.get("ownership"),
                        "odometer": car.get("odometer", {}).get("value") if car.get("odometer") else None,
                        "cityId": car.get("cityId"),
                        "sellerType": car.get("sellerType"),
                        "status": car.get("status"),
                        "image": car.get("listingImage", {}).get("uri") if car.get("listingImage") else None,
                        "url": f"https://www.cars24.com/buy-used-car-{car.get('make', '').lower()}-{car.get('model', '').lower()}-{car.get('appointmentId', '')}"
                    }
                    
                    # Only include if essential fields are present
                    if car_data["appointmentId"] and car_data["make"] and car_data["model"]:
                        cars.append(car_data)
            else:
                # Try old API structure (backward compatibility)
                content = api_response["cmsData"]["data"]["data"][0]["data"]["content"]
                
                for item in content:
                    if item.get("type") == "SINGLE_CAR_CARD":
                        car_card = item["data"]["carCard"]
                        
                        # Extract car data using the exact field mapping from read_json.py
                        car_data = {
                            "appointmentId": car_card.get("appointmentId"),
                            "make": car_card.get("make"),
                            "model": car_card.get("model"),
                            "variant": car_card.get("variant"),
                            "year": car_card.get("year"),
                            "price": car_card.get("listingPrice"),
                            "fuelType": car_card.get("fuelType"),
                            "transmission": car_card.get("transmission"),
                            "ownership": car_card.get("ownership"),
                            "odometer": car_card.get("odometer", {}).get("value") if car_card.get("odometer") else None,
                            "cityId": car_card.get("cityId"),
                            "sellerType": car_card.get("sellerType"),
                            "status": car_card.get("status"),
                            "image": car_card.get("listingImage", {}).get("uri") if car_card.get("listingImage") else None,
                            "url": "https://www.cars24.com/" + car_card.get("cdpRelativeUrl", "") if car_card.get("cdpRelativeUrl") else None
                        }
                        
                        # Only include if essential fields are present
                        if car_data["appointmentId"] and car_data["make"] and car_data["model"]:
                            cars.append(car_data)
                        
        except (KeyError, IndexError) as e:
            print(f"Error extracting cars from response: {e}")
        
        return cars
    
    def process_raw_files(self):
        """Process all raw JSON files and extract car objects"""
        all_cars = []
        raw_files = self.load_raw_files()
        
        for filepath in raw_files:
            print(f"Processing {os.path.basename(filepath)}...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both single response and array of responses
                if isinstance(data, list):
                    responses = data
                else:
                    responses = [data]
                
                # Extract cars from each response
                for response in responses:
                    cars = self.extract_cars_from_response(response)
                    all_cars.extend(cars)
                    print(f"  Extracted {len(cars)} cars from this response")
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
        
        print(f"Total cars extracted: {len(all_cars)}")
        return all_cars
    
    def create_master_dataset(self, cars):
        """Create master dataset with metadata"""
        # Get unique values for metadata
        cities = set()
        makes = set()
        
        for car in cars:
            if car.get("cityId"):
                cities.add(car["cityId"])
            if car.get("make"):
                makes.add(car["make"])
        
        master_dataset = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_listings": len(cars),
                "cities": sorted(list(cities)),
                "makes": sorted(list(makes)),
                "data_source": "Cars24 API"
            },
            "listings": cars
        }
        
        return master_dataset
    
    def save_master_dataset(self, master_dataset):
        """Save master dataset to processed directory"""
        os.makedirs(self.processed_data_dir, exist_ok=True)
        filepath = os.path.join(self.processed_data_dir, "master_dataset.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(master_dataset, f, indent=2)
        
        print(f"Saved master dataset to {filepath}")
        return filepath
    
    def build_dataset(self):
        """Run the complete dataset building pipeline"""
        print("=" * 60)
        print("DATASET BUILDER PIPELINE")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Step 1: Process raw files
        print("\n[Step 1/2] Processing raw files...")
        cars = self.process_raw_files()
        
        if not cars:
            print("No cars extracted. Cannot create master dataset.")
            return None
        
        # Step 2: Create master dataset
        print("\n[Step 2/2] Creating master dataset...")
        master_dataset = self.create_master_dataset(cars)
        
        # Step 3: Save master dataset
        filepath = self.save_master_dataset(master_dataset)
        
        print("\n" + "=" * 60)
        print("DATASET BUILDING COMPLETED")
        print(f"Total listings: {master_dataset['metadata']['total_listings']}")
        print(f"Unique cities: {len(master_dataset['metadata']['cities'])}")
        print(f"Unique makes: {len(master_dataset['metadata']['makes'])}")
        print(f"Saved to: {filepath}")
        print("=" * 60)
        
        return master_dataset

if __name__ == "__main__":
    builder = DatasetBuilder()
    builder.build_dataset()
