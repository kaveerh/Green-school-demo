"""
Configuration Loader

Load and validate YAML configuration files.
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    logger.info(f"Loading configuration from: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Load environment variables
    load_dotenv()

    # Override config with environment variables if present
    if os.getenv("API_BASE_URL"):
        config["api"]["base_url"] = os.getenv("API_BASE_URL")

    if os.getenv("API_TIMEOUT"):
        config["api"]["timeout"] = int(os.getenv("API_TIMEOUT"))

    if os.getenv("LOG_LEVEL"):
        config["output"]["log_level"] = os.getenv("LOG_LEVEL")

    # Validate configuration
    validate_config(config)

    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration structure

    Args:
        config: Configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = ["api", "school", "data_volumes", "generation_rules", "output"]

    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")

    # Validate API config
    if "base_url" not in config["api"]:
        raise ValueError("Missing api.base_url in configuration")

    # Validate data volumes
    volumes = config["data_volumes"]
    required_volumes = [
        "administrators",
        "teachers",
        "students",
        "parents",
        "subjects",
        "rooms",
        "classes",
    ]

    for volume in required_volumes:
        if volume not in volumes:
            raise ValueError(f"Missing data_volumes.{volume} in configuration")

    # Validate grade distribution sums to student count
    grade_dist = config["generation_rules"].get("grade_distribution", {})
    total_students_in_dist = sum(grade_dist.values())
    configured_students = volumes["students"]

    if total_students_in_dist != configured_students:
        raise ValueError(
            f"Grade distribution total ({total_students_in_dist}) "
            f"does not match configured students ({configured_students})"
        )

    logger.info("Configuration validated successfully")


def get_default_config_path() -> str:
    """Get path to default configuration file"""
    # Try environment variable first
    env_config = os.getenv("DEFAULT_CONFIG")
    if env_config:
        return env_config

    # Default to config/default.yaml
    current_dir = Path(__file__).parent.parent
    default_config = current_dir / "config" / "default.yaml"

    return str(default_config)
