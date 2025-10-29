#!/usr/bin/env python3
"""Test single feature generation"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import load_config
from src.cache import EntityCache
from src.client import SchoolAPIClient
from src.generators.teacher import TeacherGenerator
from src.generators.user import UserGenerator
from faker import Faker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    config = load_config("config/large.yaml")
    client = SchoolAPIClient(config["api"]["base_url"])
    cache = EntityCache()
    faker = Faker()
    
    # Get existing school
    schools = client.get("/api/v1/schools")["data"]
    school = schools[0]
    cache.add_entity("school", school["id"], school)
    logger.info(f"Using school: {school['id']}")
    
    # Create one teacher user
    user_gen = UserGenerator(client, cache, faker, config)
    users = user_gen.generate(count=1, persona="teacher")
    logger.info(f"Created teacher user: {users[0]['id']}")
    
    # Create teacher profile
    teacher_gen = TeacherGenerator(client, cache, faker, config)
    try:
        teachers = teacher_gen.generate(count=1)
        logger.info(f"✓ Created teacher: {teachers[0]['id']}")
    except Exception as e:
        logger.error(f"✗ Failed to create teacher: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
