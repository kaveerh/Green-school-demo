#!/usr/bin/env python3
"""
Test Large Dataset Generation

Generate a large dataset and test Create/Delete for all features.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import load_config
from src.cache import EntityCache
from src.client import SchoolAPIClient
from src.generator import DataGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Generate large dataset"""
    try:
        # Load config
        config_path = "config/large.yaml"
        logger.info(f"Loading config from {config_path}")
        config = load_config(config_path)
        
        # Initialize
        client = SchoolAPIClient(config["api"]["base_url"], config["api"]["timeout"])
        cache = EntityCache()
        generator = DataGenerator(config, client, cache)
        
        # Generate all data
        logger.info("Starting data generation...")
        generator.generate_all()
        
        logger.info("✓ Data generation complete!")
        logger.info(f"Generated:")
        logger.info(f"  - Schools: {len(cache.schools)}")
        logger.info(f"  - Users: {len(cache.users)}")
        logger.info(f"  - Teachers: {len(cache.teachers)}")
        logger.info(f"  - Students: {len(cache.students)}")
        logger.info(f"  - Parents: {len(cache.parents)}")
        logger.info(f"  - Subjects: {len(cache.subjects)}")
        logger.info(f"  - Rooms: {len(cache.rooms)}")
        logger.info(f"  - Classes: {len(cache.classes)}")
        
        # Save cache
        cache_file = "generated_data_cache_large.json"
        cache.save(cache_file)
        logger.info(f"✓ Cache saved to {cache_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
