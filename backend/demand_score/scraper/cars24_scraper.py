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
        """Scrape all listings for a specific city using searchAfter pagination"""
        if city_name not in self.cities:
            raise ValueError(f"City {city_name} not supported. Available: {list(self.cities.keys())}")
        
        city_id = self.cities[city_name]
        url = f"{self.base_url}-{city_name}"
        
        all_responses = []
        search_after = None
        request_count = 0
        max_requests = 100  # Safety limit
        
        print(f"Starting scrape for {city_name}...")
        
        while request_count < max_requests:
            payload = {
                "searchFilter": [],
                "cityId": city_id,
                "sort": "bestmatch",
                "size": 100,  # Increased size to get more cars per request
                "filterVersion": 4
            }
            
            if search_after:
                payload["searchAfter"] = search_after
            
            # Debug: print payload before request
            print(f"Request {request_count + 1}:")
            print(json.dumps(payload, indent=2))
            
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                # Debug: print response status
                print(f"Status: {response.status_code}")
                print(f"Response (first 1000 chars): {response.text[:1000]}")
                
                if response.status_code != 200:
                    print(f"Error response: {response.text[:500]}")
                    break
                    
                data = response.json()
                
                # Save the complete API response
                all_responses.append(data)
                print(f"Retrieved API response")
                
                # Extract searchAfter for next page from the Cars24 response structure
                try:
                    # New API structure: data is directly in "content" array at root level
                    if "content" in data:
                        content = data["content"]
                        # Count cars in this response
                        car_count = len(content)
                        print(f"Found {car_count} car listings in this response")
                        
                        if car_count == 0:
                            print(f"No more listings found for {city_name}")
                            break
                    else:
                        # Try old structure for backward compatibility
                        content = data["cmsData"]["data"]["data"][0]["data"]["content"]
                        car_count = sum(1 for item in content if item.get("type") == "SINGLE_CAR_CARD")
                        print(f"Found {car_count} car listings in this response (old structure)")
                        
                        if car_count == 0:
                            print(f"No more listings found for {city_name}")
                            break
                    
                    # Get searchAfter from the response (cursor-based pagination)
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
                    else:
                        print(f"Got searchAfter token: {search_after[:50]}...")
                        
                except (KeyError, IndexError) as e:
                    print(f"Error parsing response structure: {e}")
                    break
                
                request_count += 1
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error scraping {city_name}: {e}")
                break
        
        print(f"Completed scrape for {city_name}: {len(all_responses)} responses retrieved")
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
    
    # Scrape all available cities to gather more data
    print("Scraping all available cities...")
    results = scraper.scrape_all_cities()
    
    print("\nScraping Summary:")
    for city, data in results.items():
        if "error" in data:
            print(f"{city}: FAILED - {data['error']}")
        else:
            print(f"{city}: SUCCESS - {data['pages']} responses, saved to {data['filepath']}")
