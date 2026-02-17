import argparse
import logging
import yaml
import os
import sys

from src.utils.logger import setup_logger
from src.data_prep import load_data, clean_data, feature_engineering, save_data

def load_config(config_path: str) -> dict:
    """
    Loads configuration from a YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def main():
    parser = argparse.ArgumentParser(description="Sentiment Analysis Pipeline")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config file")
    parser.add_argument("--task", type=str, required=True, choices=["prep", "analyze", "full"], help="Task to perform")

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Failed to load config: {e}")
        sys.exit(1)

    # Setup logger
    log_file = config.get("logging", {}).get("file", "logs/app.log")
    log_level = config.get("logging", {}).get("level", "INFO")
    logger = setup_logger(name="main", log_file=log_file, level=getattr(logging, log_level.upper(), logging.INFO))

    logger.info("Starting pipeline...")

    if args.task in ["prep", "full"]:
        logger.info("Running data preparation...")
        raw_path = config["data"]["raw_path"]
        processed_path = config["data"]["processed_path"]

        try:
            df = load_data(raw_path)
            df = clean_data(df)
            df = feature_engineering(df)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            save_data(df, processed_path)

        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            sys.exit(1)

    if args.task in ["analyze", "full"]:
        logger.info("Running analysis... (Not fully implemented)")
        # analytical functions would be called here
        pass

    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
