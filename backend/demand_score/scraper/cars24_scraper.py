import requests
import json
import os
from datetime import datetime
import time

class Cars24Scraper:
    def __init__(self):
        self.base_url = "https://car-catalog-gateway-in.c24.tech/listing/v1/buy-used-cars"
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://www.cars24.com",
            "referer": "https://www.cars24.com/",
            "user-agent": "Mozilla/5.0",
            "clientid": "389321643.1765379264",
            "source": "WebApp",
            "x_experiment_id": "18637211-c578-44cd-895b-f8774eaa1dcf",
            "x_tenant_id": "INDIA_CAR_LISTING",
            "x_user_city_id": "2378"
        }
        self.cities = {
            "mumbai": "2378",
            "bangalore": "4709",
            "pune": "2423"
        }
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), "../data/raw")
        
    def scrape_city(self, city_name):
        """Scrape all listings for a specific city using v1 API with multiple requests"""
        if city_name not in self.cities:
            raise ValueError(f"City {city_name} not supported. Available: {list(self.cities.keys())}")
        
        city_id = self.cities[city_name]
        url = f"{self.base_url}-{city_name}"
        
        all_responses = []
        total_cars_extracted = 0
        
        # Since v1 API seems limited to 30 cars per request without proper pagination,
        # we'll make multiple requests with slight variations to gather more data
        max_requests = 70  # To get ~2000 cars (30 * 70 = 2100)
        
        print(f"Starting scrape for {city_name}...")
        
        for request_num in range(max_requests):
            # Build payload for v1 API
            payload = {
                "searchFilter": [],
                "cityId": city_id,
                "sort": "bestmatch",
                "size": 30,  # Max seems to be 30
                "filterVersion": 4
            }
            
            # Vary the sort parameter to get different results
            sort_options = ["bestmatch", "price_asc", "price_desc", "newest_first", "kilometers_asc"]
            payload["sort"] = sort_options[request_num % len(sort_options)]
            
            # Log request details
            print(f"\n=== Request {request_num + 1} ===")
            print(f"Sort: {payload['sort']}")
            print(f"Size: {payload['size']}")
            
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code != 200:
                    print(f"Error: Status {response.status_code}")
                    print(f"Response: {response.text[:500]}")
                    break
                
                data = response.json()
                
                # Save the complete API response
                all_responses.append(data)
                
                # Extract car data from v1 API response
                try:
                    if "content" in data:
                        content = data["content"]
                        car_count = len(content)
                        total_cars_extracted += car_count
                        
                        print(f"Cars Extracted: {car_count} (Total: {total_cars_extracted})")
                        
                        if car_count == 0:
                            print(f"No more listings found")
                            break
                        
                        # Rate limiting
                        time.sleep(0.5)
                    else:
                        print(f"No content found in response")
                        break
                        
                except (KeyError, IndexError) as e:
                    print(f"Error parsing response: {e}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Error scraping {city_name}: {e}")
                break
        
        print(f"\n=== Scrape Complete ===")
        print(f"Total requests: {len(all_responses)}")
        print(f"Total cars extracted: {total_cars_extracted}")
        
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
    
    # Retry Bangalore to get remaining cars (got 930, need 1170 more)
    print("Retrying Bangalore to get remaining cars...")
    results = scraper.scrape_city("bangalore")
    
    if results:
        scraper.save_raw_data("bangalore", results)
        print(f"\nBangalore data saved successfully")
