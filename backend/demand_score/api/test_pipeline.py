import json
import os
import shutil
from datetime import datetime

def test_pipeline_with_existing_data():
    """Test the pipeline using existing Cars24 data"""
    print("=" * 60)
    print("TESTING DEMAND SCORE PIPELINE WITH EXISTING DATA")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Copy existing data to raw directory
    source_file = "cars24_page2.json"
    target_dir = "demand_score/data/raw"
    target_file = os.path.join(target_dir, f"test_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    print(f"\n[Step 1] Copying existing data to raw directory...")
    if os.path.exists(source_file):
        shutil.copy(source_file, target_file)
        print(f"Copied {source_file} to {target_file}")
    else:
        print(f"Error: {source_file} not found")
        return False
    
    # Test data processor
    print(f"\n[Step 2] Testing data processor...")
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from training.data_processor import DataProcessor
        
        processor = DataProcessor()
        master_dataset = processor.process_pipeline()
        
        print(f"✅ Data processing successful")
        print(f"   Total listings: {master_dataset['metadata']['total_listings']}")
        print(f"   Cities: {master_dataset['metadata']['cities']}")
        print(f"   Makes: {len(master_dataset['metadata']['makes'])}")
        
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        return False
    
    # Test demand calculator
    print(f"\n[Step 3] Testing demand calculator...")
    try:
        from training.demand_calculator import DemandScoreCalculator
        
        calculator = DemandScoreCalculator()
        demand_score_data = calculator.generate_demand_score_data()
        
        print(f"✅ Demand score generation successful")
        print(f"   Total scores: {demand_score_data['metadata']['total_scores']}")
        
        # Show sample score
        if demand_score_data['metadata']['total_scores'] > 0:
            sample_key = list(demand_score_data['scores'].keys())[0]
            sample_score = demand_score_data['scores'][sample_key]
            print(f"\n   Sample score:")
            print(f"   Car: {sample_score['make']} {sample_score['model']} ({sample_score['city']})")
            print(f"   Score: {sample_score['score']}")
            print(f"   Level: {sample_score['level']}")
        
    except Exception as e:
        print(f"❌ Demand score calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n[Step 4] Testing API endpoint...")
    print("   API endpoint will be tested after backend restart")
    
    print("\n" + "=" * 60)
    print("PIPELINE TEST COMPLETED SUCCESSFULLY")
    print(f"Completed at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    import sys
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    success = test_pipeline_with_existing_data()
    sys.exit(0 if success else 1)
