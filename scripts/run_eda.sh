#!/bin/bash
# Scripts to run data preparation and EDA
set -e

# Activate virtual environment if needed (optional)
# source venv/bin/activate

# Run data preparation
python src/main.py --task prep --config config/config.yaml

echo "Data preparation complete. Output saved to data/processed/"
