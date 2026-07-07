import json
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching of preprocessed data for faster loading"""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        
        self.cache_dir = cache_dir
        self.companies_cache_file = os.path.join(cache_dir, "companies.json")
        self.models_cache_file = os.path.join(cache_dir, "models.json")
        self.metadata_cache_file = os.path.join(cache_dir, "metadata.json")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def save_companies(self, companies: List[str]) -> None:
        """Save companies list to cache"""
        try:
            with open(self.companies_cache_file, 'w') as f:
                json.dump({"companies": sorted(companies)}, f, indent=2)
            logger.info(f"✅ Cached {len(companies)} companies")
        except Exception as e:
            logger.error(f"Failed to cache companies: {e}")
    
    def load_companies(self) -> List[str] | None:
        """Load companies list from cache"""
        try:
            if os.path.exists(self.companies_cache_file):
                with open(self.companies_cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"✅ Loaded {len(data['companies'])} companies from cache")
                    return data['companies']
        except Exception as e:
            logger.error(f"Failed to load companies from cache: {e}")
        return None
    
    def save_models(self, models_dict: Dict[str, List[str]]) -> None:
        """Save models dictionary to cache"""
        try:
            with open(self.models_cache_file, 'w') as f:
                json.dump(models_dict, f, indent=2)
            logger.info(f"✅ Cached models for {len(models_dict)} companies")
        except Exception as e:
            logger.error(f"Failed to cache models: {e}")
    
    def load_models(self) -> Dict[str, List[str]] | None:
        """Load models dictionary from cache"""
        try:
            if os.path.exists(self.models_cache_file):
                with open(self.models_cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"✅ Loaded models for {len(data)} companies from cache")
                    return data
        except Exception as e:
            logger.error(f"Failed to load models from cache: {e}")
        return None
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save dataset metadata to cache"""
        try:
            with open(self.metadata_cache_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"✅ Cached dataset metadata")
        except Exception as e:
            logger.error(f"Failed to cache metadata: {e}")
    
    def load_metadata(self) -> Dict[str, Any] | None:
        """Load dataset metadata from cache"""
        try:
            if os.path.exists(self.metadata_cache_file):
                with open(self.metadata_cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"✅ Loaded dataset metadata from cache")
                    return data
        except Exception as e:
            logger.error(f"Failed to load metadata from cache: {e}")
        return None
    
    def clear_cache(self) -> None:
        """Clear all cache files"""
        try:
            for file in [self.companies_cache_file, self.models_cache_file, self.metadata_cache_file]:
                if os.path.exists(file):
                    os.remove(file)
            logger.info("✅ Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def cache_exists(self) -> bool:
        """Check if cache files exist"""
        return all(os.path.exists(f) for f in [
            self.companies_cache_file, 
            self.models_cache_file, 
            self.metadata_cache_file
        ])
