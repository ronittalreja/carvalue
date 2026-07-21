import json
import os
import statistics
from datetime import datetime
from collections import defaultdict, Counter

class DemandScoreEngine:
    def __init__(self):
        self.processed_data_dir = os.path.join(os.path.dirname(__file__), "../data/processed")
        self.generated_data_dir = os.path.join(os.path.dirname(__file__), "../data/generated")
        
    def load_master_dataset(self):
        """Load the master dataset"""
        filepath = os.path.join(self.processed_data_dir, "master_dataset.json")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return data
    
    # =========================
    # PART 1: FEATURE EXTRACTION
    # =========================
    def extract_features(self, listings):
        """Extract features for each make+model combination"""
        # Group by make+model
        make_model_groups = defaultdict(list)
        
        for car in listings:
            make = car.get("make", "").strip()
            model = car.get("model", "").strip()
            if make and model:
                key = f"{make}_{model}"
                make_model_groups[key].append(car)
        
        # Extract features for each group
        features = {}
        
        for key, cars in make_model_groups.items():
            make, model = key.split("_", 1)
            
            # Basic counts
            listings_count = len(cars)
            
            # Price statistics
            prices = [car.get("price", 0) for car in cars if car.get("price")]
            average_price = statistics.mean(prices) if prices else 0
            median_price = statistics.median(prices) if prices else 0
            
            # Age statistics
            current_year = datetime.now().year
            ages = [current_year - car.get("year", current_year) for car in cars if car.get("year")]
            average_age = statistics.mean(ages) if ages else 0
            
            # KM statistics
            kms = [car.get("odometer", 0) for car in cars if car.get("odometer")]
            average_km = statistics.mean(kms) if kms else 0
            
            # Geographic presence
            cities = set(car.get("cityId") for car in cars if car.get("cityId"))
            cities_available = len(cities)
            
            # Transmission distribution
            transmissions = [car.get("transmission", "").lower() for car in cars if car.get("transmission")]
            transmission_counts = Counter(transmissions)
            manual_count = transmission_counts.get("manual", 0)
            automatic_count = transmission_counts.get("automatic", 0)
            
            # Fuel distribution
            fuels = [car.get("fuelType", "").lower() for car in cars if car.get("fuelType")]
            fuel_counts = Counter(fuels)
            petrol_count = fuel_counts.get("petrol", 0)
            diesel_count = fuel_counts.get("diesel", 0)
            electric_count = fuel_counts.get("electric", 0)
            cng_count = fuel_counts.get("cng", 0)
            
            # Ownership distribution
            ownerships = []
            for car in cars:
                ownership = car.get("ownership")
                if ownership:
                    # Handle both string and integer ownership values
                    if isinstance(ownership, int):
                        ownerships.append(str(ownership))
                    else:
                        ownerships.append(ownership.lower())
            
            ownership_counts = Counter(ownerships)
            first_owner_count = ownership_counts.get("1", 0) + ownership_counts.get("1st owner", 0) + ownership_counts.get("first owner", 0)
            second_owner_count = ownership_counts.get("2", 0) + ownership_counts.get("2nd owner", 0) + ownership_counts.get("second owner", 0)
            
            # Variant count
            variants = set(car.get("variant", "").strip() for car in cars if car.get("variant"))
            variant_count = len(variants)
            
            features[key] = {
                "make": make,
                "model": model,
                "listings": listings_count,
                "averagePrice": round(average_price),
                "medianPrice": round(median_price),
                "averageAge": round(average_age, 1),
                "averageKm": round(average_km),
                "citiesAvailable": cities_available,
                "manual": manual_count,
                "automatic": automatic_count,
                "petrol": petrol_count,
                "diesel": diesel_count,
                "electric": electric_count,
                "cng": cng_count,
                "firstOwner": first_owner_count,
                "secondOwner": second_owner_count,
                "variantCount": variant_count
            }
        
        return features
    
    # =========================
    # PART 2: MARKET ANALYTICS
    # =========================
    def calculate_market_analytics(self, features, total_listings):
        """Calculate demand-indicating statistics for each model"""
        analytics = {}
        
        # Calculate brand shares
        brand_totals = defaultdict(int)
        for key, feature in features.items():
            brand_totals[feature["make"]] += feature["listings"]
        
        total_brand_listings = sum(brand_totals.values())
        
        for key, feature in features.items():
            # Market share
            market_share = (feature["listings"] / total_listings * 100) if total_listings > 0 else 0
            
            # Brand share
            brand_share = (feature["listings"] / brand_totals[feature["make"]] * 100) if brand_totals[feature["make"]] > 0 else 0
            
            # Price statistics
            prices = [feature["averagePrice"]]  # Using average as proxy for now
            price_std_dev = 0  # Would need individual car prices for accurate std dev
            
            # Ownership quality (higher first owner % = better quality)
            ownership_quality = (feature["firstOwner"] / feature["listings"] * 100) if feature["listings"] > 0 else 0
            
            analytics[key] = {
                "listingCount": feature["listings"],
                "marketShare": round(market_share, 2),
                "averagePrice": feature["averagePrice"],
                "medianPrice": feature["medianPrice"],
                "priceStdDev": price_std_dev,
                "averageAge": feature["averageAge"],
                "averageKm": feature["averageKm"],
                "ownershipDistribution": {
                    "firstOwner": feature["firstOwner"],
                    "secondOwner": feature["secondOwner"],
                    "ownershipQuality": round(ownership_quality, 1)
                },
                "fuelMix": {
                    "petrol": feature["petrol"],
                    "diesel": feature["diesel"],
                    "electric": feature["electric"],
                    "cng": feature["cng"]
                },
                "transmissionMix": {
                    "manual": feature["manual"],
                    "automatic": feature["automatic"]
                },
                "citiesAvailable": feature["citiesAvailable"],
                "brandShare": round(brand_share, 2),
                "variantCount": feature["variantCount"]
            }
        
        return analytics
    
    # =========================
    # PART 3: DEMAND SCORE ALGORITHM
    # =========================
    def calculate_demand_score(self, analytics, features):
        """Calculate demand score using weighted formula"""
        demand_scores = {}
        
        # Find max values for normalization
        max_listings = max(analytics[key]["listingCount"] for key in analytics)
        max_cities = max(analytics[key]["citiesAvailable"] for key in analytics)
        max_variants = max(analytics[key]["variantCount"] for key in analytics)
        
        for key in analytics:
            feature = features[key]
            analytic = analytics[key]
            
            # 1. Listing Popularity (25%)
            # Normalize: 0-100 based on max listings
            listing_score = (analytic["listingCount"] / max_listings * 100) if max_listings > 0 else 0
            
            # 2. Brand Popularity (20%)
            # Use brand share as proxy for brand popularity
            brand_score = analytic["brandShare"]
            
            # 3. Variant Availability (15%)
            # More variants = better availability
            variant_score = (analytic["variantCount"] / max_variants * 100) if max_variants > 0 else 0
            
            # 4. Geographic Presence (15%)
            # More cities = better geographic presence
            geo_score = (analytic["citiesAvailable"] / max_cities * 100) if max_cities > 0 else 0
            
            # 5. Price Stability (10%)
            # Lower std dev relative to price = more stable
            # For now, use inverse of average price as proxy (lower price = more stable demand)
            price_stability_score = max(0, 100 - (analytic["averagePrice"] / 100000))  # Simple proxy
            
            # 6. Average Age (10%)
            # Younger cars = higher demand (inverse relationship)
            age_score = max(0, 100 - (analytic["averageAge"] * 10))  # Each year reduces score by 10
            
            # 7. Ownership Quality (5%)
            # Higher first owner % = better quality
            ownership_score = analytic["ownershipDistribution"]["ownershipQuality"]
            
            # Calculate weighted score
            weighted_score = (
                (listing_score * 0.25) +
                (brand_score * 0.20) +
                (variant_score * 0.15) +
                (geo_score * 0.15) +
                (price_stability_score * 0.10) +
                (age_score * 0.10) +
                (ownership_score * 0.05)
            )
            
            # Normalize to 0-100
            final_score = max(0, min(100, round(weighted_score)))
            
            demand_scores[key] = {
                "score": final_score,
                "components": {
                    "listingPopularity": round(listing_score, 1),
                    "brandPopularity": round(brand_score, 1),
                    "variantAvailability": round(variant_score, 1),
                    "geographicPresence": round(geo_score, 1),
                    "priceStability": round(price_stability_score, 1),
                    "averageAge": round(age_score, 1),
                    "ownershipQuality": round(ownership_score, 1)
                }
            }
        
        return demand_scores
    
    def get_demand_level(self, score):
        """Get demand level description"""
        if score >= 81:
            return "Very High"
        elif score >= 61:
            return "High"
        elif score >= 41:
            return "Moderate"
        elif score >= 21:
            return "Low"
        else:
            return "Very Low"
    
    def get_recommendation(self, score, analytics):
        """Get recommendation based on score and analytics"""
        if score >= 81:
            return "Strong demand with excellent resale prospects."
        elif score >= 61:
            return "Good demand. Should sell relatively quickly."
        elif score >= 41:
            return "Moderate demand. Pricing will be important."
        elif score >= 21:
            return "Lower demand. May take longer to sell."
        else:
            return "Very low demand. Consider competitive pricing."
    
    # =========================
    # PART 4: OUTPUT GENERATION
    # =========================
    def generate_demand_score_output(self, features, analytics, demand_scores):
        """Generate final demand_score.json output"""
        output = {}
        
        for key in features:
            feature = features[key]
            analytic = analytics[key]
            score_data = demand_scores[key]
            
            car_name = f"{feature['make']} {feature['model']}"
            
            output[car_name] = {
                "score": score_data["score"],
                "level": self.get_demand_level(score_data["score"]),
                "listingCount": analytic["listingCount"],
                "averagePrice": analytic["averagePrice"],
                "marketShare": analytic["marketShare"],
                "recommendation": self.get_recommendation(score_data["score"], analytic),
                "components": score_data["components"],
                "analytics": {
                    "medianPrice": analytic["medianPrice"],
                    "averageAge": analytic["averageAge"],
                    "averageKm": analytic["averageKm"],
                    "citiesAvailable": analytic["citiesAvailable"],
                    "variantCount": analytic["variantCount"],
                    "ownershipQuality": analytic["ownershipDistribution"]["ownershipQuality"]
                }
            }
        
        return output
    
    def run_demand_score_engine(self):
        """Run the complete demand score engine pipeline"""
        print("=" * 60)
        print("DEMAND SCORE ENGINE")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Load master dataset
        print("\n[Step 1/5] Loading master dataset...")
        master_data = self.load_master_dataset()
        listings = master_data.get("listings", [])
        total_listings = len(listings)
        print(f"Loaded {total_listings} listings")
        
        # Part 1: Feature Extraction
        print("\n[Step 2/5] Feature Extraction...")
        features = self.extract_features(listings)
        print(f"Extracted features for {len(features)} make+model combinations")
        
        # Part 2: Market Analytics
        print("\n[Step 3/5] Market Analytics...")
        analytics = self.calculate_market_analytics(features, total_listings)
        print(f"Calculated analytics for {len(analytics)} models")
        
        # Part 3: Demand Score Algorithm
        print("\n[Step 4/5] Demand Score Calculation...")
        demand_scores = self.calculate_demand_score(analytics, features)
        print(f"Calculated demand scores for {len(demand_scores)} models")
        
        # Part 4: Output Generation
        print("\n[Step 5/5] Generating demand_score.json...")
        output = self.generate_demand_score_output(features, analytics, demand_scores)
        
        # Save output
        os.makedirs(self.generated_data_dir, exist_ok=True)
        filepath = os.path.join(self.generated_data_dir, "demand_score.json")
        
        final_output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_models": len(output),
                "data_source": "Cars24 API",
                "algorithm_version": "1.0",
                "total_listings_analyzed": total_listings
            },
            "scores": output
        }
        
        with open(filepath, 'w') as f:
            json.dump(final_output, f, indent=2)
        
        print(f"Saved demand_score.json to {filepath}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("DEMAND SCORE ENGINE COMPLETED")
        print(f"Total models scored: {len(output)}")
        print(f"Average score: {round(sum(s['score'] for s in output.values()) / len(output), 1)}")
        print(f"Highest score: {max(output.values(), key=lambda x: x['score'])['score']}")
        print(f"Lowest score: {min(output.values(), key=lambda x: x['score'])['score']}")
        print("=" * 60)
        
        return final_output

if __name__ == "__main__":
    engine = DemandScoreEngine()
    engine.run_demand_score_engine()
