import requests
import json
import os
from datetime import datetime
import time

class Cars24Scraper:
    def __init__(self):
        self.base_url = "https://car-catalog-gateway-in.c24.tech/listing/v2/buy-used-cars"
        self.headers = {
            "Content-Type": "application/json",
            "x_tenant_id": "c24",
            "x_user_city_id": "1",
            "clientid": "c24-web",
            "source": "web",
            "x_experiment_id": "default"
        }
        self.cities = {
            "mumbai": "1",
            "delhi": "2", 
            "bangalore": "3",
            "pune": "4",
            "hyderabad": "5",
            "chennai": "6",
            "kolkata": "7",
            "ahmedabad": "8"
        }
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), "../data/raw")
        
    def scrape_city(self, city_name):
        """Scrape all listings for a specific city using searchAfter pagination"""
        if city_name not in self.cities:
            raise ValueError(f"City {city_name} not supported. Available: {list(self.cities.keys())}")
        
        city_id = self.cities[city_name]
        url = f"{self.base_url}-{city_name}"
        
        all_responses = []
        search_after = None
        page = 0
        max_pages = 100  # Safety limit
        
        print(f"Starting scrape for {city_name}...")
        
        while page < max_pages:
            payload = {
                "cityId": int(city_id),
                "filterVersion": "v2",
                "page": page,
                "searchFilter": {},
                "userAction": "search"
            }
            
            if search_after:
                payload["searchAfter"] = search_after
            
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                # Debug: print response status and first part of response
                print(f"Page {page}: Status {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Error response: {response.text[:500]}")
                    break
                    
                data = response.json()
                
                # Save the complete API response
                all_responses.append(data)
                print(f"Page {page}: Retrieved API response")
                
                # Extract searchAfter for next page from the Cars24 response structure
                try:
                    # Navigate to the content array to find car listings
                    content = data["cmsData"]["data"]["data"][0]["data"]["content"]
                    
                    # Count cars in this response
                    car_count = sum(1 for item in content if item.get("type") == "SINGLE_CAR_CARD")
                    print(f"  Found {car_count} car listings on this page")
                    
                    if car_count == 0:
                        print(f"No more listings found for {city_name} at page {page}")
                        break
                    
                    # Get searchAfter from the response (Cars24 specific location)
                    # This might be in different locations depending on API version
                    search_after = data.get("searchAfter")
                    if not search_after:
                        # Try alternative locations for searchAfter
                        try:
                            search_after = data.get("cmsData", {}).get("data", {}).get("searchAfter")
                        except:
                            pass
                    
                    if not search_after:
                        print(f"No searchAfter token found, ending pagination for {city_name}")
                        break
                        
                except (KeyError, IndexError) as e:
                    print(f"Error parsing response structure: {e}")
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error scraping {city_name} page {page}: {e}")
                break
        
        print(f"Completed scrape for {city_name}: {len(all_responses)} pages retrieved")
        return all_responses
    
    def save_raw_data(self, city_name, responses):
        """Save raw JSON API responses to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city_name}_{timestamp}.json"
        filepath = os.path.join(self.raw_data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(responses, f, indent=2)
        
        print(f"Saved raw data to {filepath}")
        return filepath
    
    def scrape_all_cities(self, cities=None):
        """Scrape all specified cities"""
        if cities is None:
            cities = list(self.cities.keys())
        
        all_data = {}
        
        for city in cities:
            try:
                responses = self.scrape_city(city)
                if responses:
                    filepath = self.save_raw_data(city, responses)
                    all_data[city] = {
                        "pages": len(responses),
                        "filepath": filepath,
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"Failed to scrape {city}: {e}")
                all_data[city] = {"error": str(e)}
        
        return all_data

if __name__ == "__main__":
    scraper = Cars24Scraper()
    
    # For now, use existing data instead of live API scraping
    # The live API seems to require additional authentication or different payload structure
    print("Using existing cars24_page2.json for testing...")
    
    # Copy existing data to raw directory
    import shutil
    source_file = "cars24_page2.json"
    target_dir = scraper.raw_data_dir
    
    if os.path.exists(source_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = os.path.join(target_dir, f"existing_data_{timestamp}.json")
        shutil.copy(source_file, target_file)
        print(f"Copied existing data to {target_file}")
    else:
        print(f"Error: {source_file} not found")
        print("Attempting live API scrape...")
        
        # Test with one city first
        results = scraper.scrape_city("mumbai")
        print(f"Total pages scraped: {len(results)}")
        
        # Save the data
        scraper.save_raw_data("mumbai", results)
