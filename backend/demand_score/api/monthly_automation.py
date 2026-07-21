import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.cars24_scraper import Cars24Scraper
from training.data_processor import DataProcessor
from training.demand_calculator import DemandScoreCalculator

class MonthlyAutomation:
    def __init__(self):
        self.scraper = Cars24Scraper()
        self.processor = DataProcessor()
        self.calculator = DemandScoreCalculator()
        
    def run_monthly_update(self):
        """Run the complete monthly automation pipeline"""
        print("=" * 60)
        print("MONTHLY DEMAND SCORE AUTOMATION")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # Step 1: Scrape Cars24 data
            print("\n[Step 1/4] Scraping Cars24 data...")
            cities_to_scrape = ["mumbai", "delhi", "bangalore", "pune"]  # Start with major cities
            scrape_results = self.scraper.scrape_all_cities(cities_to_scrape)
            
            successful_cities = [city for city, result in scrape_results.items() if "error" not in result]
            failed_cities = [city for city, result in scrape_results.items() if "error" in result]
            
            print(f"Successfully scraped: {len(successful_cities)} cities")
            print(f"Failed to scrape: {len(failed_cities)} cities")
            
            if not successful_cities:
                raise Exception("No cities were successfully scraped")
            
            # Step 2: Process raw data
            print("\n[Step 2/4] Processing raw data...")
            master_dataset = self.processor.process_pipeline()
            
            if not master_dataset or master_dataset["metadata"]["total_listings"] == 0:
                raise Exception("No listings found in processed data")
            
            print(f"Processed {master_dataset['metadata']['total_listings']} listings")
            
            # Step 3: Generate demand scores
            print("\n[Step 3/4] Generating demand scores...")
            demand_score_data = self.calculator.generate_demand_score_data()
            
            if not demand_score_data or demand_score_data["metadata"]["total_scores"] == 0:
                raise Exception("No demand scores were generated")
            
            print(f"Generated {demand_score_data['metadata']['total_scores']} demand scores")
            
            # Step 4: Summary
            print("\n[Step 4/4] Automation Summary")
            print("=" * 60)
            print(f"Total cities scraped: {len(successful_cities)}")
            print(f"Total listings processed: {master_dataset['metadata']['total_listings']}")
            print(f"Total demand scores generated: {demand_score_data['metadata']['total_scores']}")
            print(f"Data freshness: {demand_score_data['metadata']['created_at']}")
            print(f"Completed at: {datetime.now().isoformat()}")
            print("=" * 60)
            
            return {
                "success": True,
                "cities_scraped": successful_cities,
                "listings_processed": master_dataset["metadata"]["total_listings"],
                "scores_generated": demand_score_data["metadata"]["total_scores"],
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"\n❌ Automation failed: {str(e)}")
            print(f"Failed at: {datetime.now().isoformat()}")
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

if __name__ == "__main__":
    automation = MonthlyAutomation()
    result = automation.run_monthly_update()
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)
