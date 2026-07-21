import json
import os
from datetime import datetime
from collections import defaultdict
import statistics

class DemandScoreCalculator:
    def __init__(self):
        self.processed_data_dir = os.path.join(os.path.dirname(__file__), "../data/processed")
        self.generated_data_dir = os.path.join(os.path.dirname(__file__), "../data/generated")
        self.snapshots_dir = os.path.join(os.path.dirname(__file__), "../data/snapshots")
        
    def load_master_dataset(self):
        """Load the master dataset"""
        filepath = os.path.join(self.processed_data_dir, "master_dataset.json")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return data
    
    def load_historical_data(self, months_back=3):
        """Load historical monthly snapshots for trend analysis"""
        historical_data = []
        current_date = datetime.now()
        
        for i in range(1, months_back + 1):
            month_date = current_date.replace(month=current_date.month - i)
            month_str = month_date.strftime("%Y-%m")
            month_dir = os.path.join(self.snapshots_dir, month_str)
            
            if os.path.exists(month_dir):
                snapshot_files = glob.glob(os.path.join(month_dir, "*.json"))
                if snapshot_files:
                    latest_snapshot = max(snapshot_files, key=os.path.getctime)
                    with open(latest_snapshot, 'r') as f:
                        historical_data.append(json.load(f))
        
        return historical_data
    
    def calculate_brand_popularity(self, listings):
        """Calculate brand popularity score"""
        brand_counts = defaultdict(int)
        for car in listings:
            if car.get("make"):
                brand_counts[car["make"].lower()] += 1
        
        total = sum(brand_counts.values())
        brand_popularity = {brand: count/total for brand, count in brand_counts.items()}
        
        return brand_popularity
    
    def calculate_model_popularity(self, listings):
        """Calculate model popularity score"""
        model_counts = defaultdict(int)
        for car in listings:
            if car.get("make") and car.get("model"):
                key = f"{car['make'].lower()}_{car['model'].lower()}"
                model_counts[key] += 1
        
        total = sum(model_counts.values())
        model_popularity = {model: count/total for model, count in model_counts.items()}
        
        return model_popularity
    
    def calculate_city_popularity(self, listings):
        """Calculate city popularity score"""
        city_counts = defaultdict(int)
        for car in listings:
            if car.get("city"):
                city_counts[car["city"].lower()] += 1
        
        total = sum(city_counts.values())
        city_popularity = {city: count/total for city, count in city_counts.items()}
        
        return city_popularity
    
    def calculate_price_volatility(self, listings):
        """Calculate price volatility for each make/model"""
        price_data = defaultdict(list)
        
        for car in listings:
            if car.get("make") and car.get("model") and car.get("price"):
                key = f"{car['make'].lower()}_{car['model'].lower()}"
                price_data[key].append(car["price"])
        
        volatility = {}
        for key, prices in price_data.items():
            if len(prices) > 1:
                mean_price = statistics.mean(prices)
                std_dev = statistics.stdev(prices)
                volatility[key] = (std_dev / mean_price) * 100 if mean_price > 0 else 0
            else:
                volatility[key] = 0
        
        return volatility
    
    def calculate_listing_growth(self, current_listings, historical_listings):
        """Calculate monthly listing growth rate"""
        current_count = len(current_listings)
        historical_count = sum(len(data.get("listings", [])) for data in historical_listings)
        
        if historical_count > 0:
            growth_rate = ((current_count - historical_count) / historical_count) * 100
        else:
            growth_rate = 0
        
        return growth_rate
    
    def calculate_price_trend(self, current_listings, historical_listings):
        """Calculate price trend percentage"""
        current_prices = [car.get("price", 0) for car in current_listings if car.get("price")]
        historical_prices = []
        
        for data in historical_listings:
            historical_prices.extend([car.get("price", 0) for car in data.get("listings", []) if car.get("price")])
        
        if current_prices and historical_prices:
            current_avg = statistics.mean(current_prices)
            historical_avg = statistics.mean(historical_prices)
            
            if historical_avg > 0:
                price_trend = ((current_avg - historical_avg) / historical_avg) * 100
            else:
                price_trend = 0
        else:
            price_trend = 0
        
        return price_trend
    
    def calculate_average_age(self, listings):
        """Calculate average vehicle age"""
        current_year = datetime.now().year
        ages = []
        
        for car in listings:
            if car.get("year"):
                age = current_year - car["year"]
                if age >= 0:
                    ages.append(age)
        
        return statistics.mean(ages) if ages else 0
    
    def calculate_average_kms(self, listings):
        """Calculate average kilometres driven"""
        kms = [car.get("kms", 0) for car in listings if car.get("kms")]
        return statistics.mean(kms) if kms else 0
    
    def calculate_demand_signals(self, make, model, city, listings, historical_data):
        """Calculate all demand signals for a specific car"""
        # Filter listings for the specific car
        filtered_listings = []
        for car in listings:
            if (car.get("make", "").lower() == make.lower() and 
                car.get("model", "").lower() == model.lower()):
                if city:
                    if car.get("city", "").lower() == city.lower():
                        filtered_listings.append(car)
                else:
                    filtered_listings.append(car)
        
        if not filtered_listings:
            return None
        
        # Calculate signals
        listing_count = len(filtered_listings)
        prices = [car.get("price", 0) for car in filtered_listings if car.get("price")]
        average_price = statistics.mean(prices) if prices else 0
        
        # Get popularity scores
        brand_popularity = self.calculate_brand_popularity(listings)
        model_popularity = self.calculate_model_popularity(listings)
        city_popularity = self.calculate_city_popularity(listings)
        
        brand_score = brand_popularity.get(make.lower(), 0)
        model_key = f"{make.lower()}_{model.lower()}"
        model_score = model_popularity.get(model_key, 0)
        city_score = city_popularity.get(city.lower(), 0) if city else 0
        
        # Calculate trends
        listing_growth = self.calculate_listing_growth(filtered_listings, historical_data)
        price_trend = self.calculate_price_trend(filtered_listings, historical_data)
        
        # Calculate averages
        avg_age = self.calculate_average_age(filtered_listings)
        avg_kms = self.calculate_average_kms(filtered_listings)
        
        return {
            "listing_count": listing_count,
            "average_price": average_price,
            "brand_popularity": brand_score,
            "model_popularity": model_score,
            "city_popularity": city_score,
            "listing_growth": listing_growth,
            "price_trend": price_trend,
            "average_age": avg_age,
            "average_kms": avg_kms
        }
    
    def calculate_demand_score(self, signals):
        """Calculate final demand score from signals"""
        if not signals:
            return 0
        
        # Weight different signals
        weights = {
            "listing_count": 0.25,      # More listings = higher demand
            "brand_popularity": 0.15,   # Popular brand = higher demand
            "model_popularity": 0.20,   # Popular model = higher demand
            "city_popularity": 0.10,     # Popular in city = higher demand
            "listing_growth": 0.15,     # Growing demand = higher score
            "price_trend": 0.10,        # Price trends affect demand
            "average_age": 0.05,        # Younger cars = higher demand
        }
        
        # Normalize signals to 0-100 range
        normalized_signals = {}
        
        # Listing count (logarithmic scaling)
        normalized_signals["listing_count"] = min(100, 20 * (signals["listing_count"] ** 0.5))
        
        # Popularity scores (already 0-1, scale to 0-100)
        normalized_signals["brand_popularity"] = signals["brand_popularity"] * 100
        normalized_signals["model_popularity"] = signals["model_popularity"] * 100
        normalized_signals["city_popularity"] = signals["city_popularity"] * 100
        
        # Growth rate (scale -100 to +100 to 0-100)
        normalized_signals["listing_growth"] = max(0, min(100, 50 + signals["listing_growth"]))
        
        # Price trend (scale -100 to +100 to 0-100)
        normalized_signals["price_trend"] = max(0, min(100, 50 + signals["price_trend"]))
        
        # Average age (inverse - younger is better)
        normalized_signals["average_age"] = max(0, 100 - (signals["average_age"] * 5))
        
        # Calculate weighted score
        weighted_score = sum(
            weights[key] * normalized_signals[key] 
            for key in weights.keys()
        )
        
        return round(weighted_score, 1)
    
    def get_demand_level(self, score):
        """Get demand level description"""
        if score >= 81:
            return "Very High Demand"
        elif score >= 61:
            return "High Demand"
        elif score >= 41:
            return "Moderate Demand"
        elif score >= 21:
            return "Low Demand"
        else:
            return "Very Low Demand"
    
    def get_recommendation(self, score, signals):
        """Get recommendation based on score and signals"""
        if score >= 81:
            return "Excellent resale demand with strong buyer interest."
        elif score >= 61:
            return "Good demand. Should sell relatively quickly."
        elif score >= 41:
            return "Moderate demand. Pricing will be important."
        elif score >= 21:
            return "Lower demand. May take longer to sell."
        else:
            return "Very low demand. Consider competitive pricing."
    
    def generate_demand_score_data(self):
        """Generate demand score data for all cars"""
        print("Loading master dataset...")
        master_data = self.load_master_dataset()
        listings = master_data.get("listings", [])
        
        print("Loading historical data...")
        historical_data = self.load_historical_data()
        
        print("Calculating demand scores...")
        demand_scores = {}
        
        # Group by make, model, city
        car_combinations = defaultdict(list)
        for car in listings:
            key = f"{car.get('make', '').lower()}_{car.get('model', '').lower()}_{car.get('city', '').lower()}"
            car_combinations[key].append(car)
        
        for key, car_list in car_combinations.items():
            make, model, city = key.split("_")
            signals = self.calculate_demand_signals(make, model, city, listings, historical_data)
            
            if signals:
                score = self.calculate_demand_score(signals)
                level = self.get_demand_level(score)
                recommendation = self.get_recommendation(score, signals)
                
                demand_scores[key] = {
                    "make": make,
                    "model": model,
                    "city": city,
                    "score": score,
                    "level": level,
                    "recommendation": recommendation,
                    "signals": signals,
                    "updated_at": datetime.now().isoformat()
                }
        
        # Save demand score data
        demand_score_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_scores": len(demand_scores),
                "data_source": "Cars24 API"
            },
            "scores": demand_scores
        }
        
        filepath = os.path.join(self.generated_data_dir, "demand_score.json")
        with open(filepath, 'w') as f:
            json.dump(demand_score_data, f, indent=2)
        
        print(f"Generated {len(demand_scores)} demand scores. Saved to {filepath}")
        return demand_score_data

if __name__ == "__main__":
    import glob
    calculator = DemandScoreCalculator()
    calculator.generate_demand_score_data()
