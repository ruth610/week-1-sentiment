import pandas as pd
import logging
from typing import Tuple
from src.utils.date_utils import ensure_datetime_utc

logger = logging.getLogger(__name__)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads raw data from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} rows.")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs data cleaning and preprocessing.

    Args:
        df (pd.DataFrame): Raw DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    logger.info(" detailed: Cleaning data...")
    df = df.copy()

    # Drop unnamed columns if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Standardize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Convert date to datetime
    if "date" in df.columns:
        logger.info("Converting 'date' column to datetime...")
        df["date"] = ensure_datetime_utc(df["date"])
    else:
        logger.warning("'date' column not found.")

    # Drop duplicates
    initial_len = len(df)
    df = df.drop_duplicates()
    logger.info(f"Dropped {initial_len - len(df)} duplicate rows.")

    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds engineered features like headline length and domain extraction.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with new features.
    """
    logger.info("Performing feature engineering...")
    df = df.copy()

    # Headline length
    if "headline" in df.columns:
        df["headline_length"] = df["headline"].astype(str).apply(len)
        logger.info("Added 'headline_length' column.")

    # Extract publisher domain (if publisher is email-like)
    if "publisher" in df.columns:
        # Simple extraction might need refinement based on actual data
        df["publisher_domain"] = df["publisher"].str.extract(r'@(.+)$')
        # Fill NaN if not email format
        df["publisher_domain"] = df["publisher_domain"].fillna(df["publisher"])
        logger.info("Added 'publisher_domain' column.")

    return df

def save_data(df: pd.DataFrame, file_path: str):
    """
    Saves the processed DataFrame to a CSV file.
    """
    try:
        logger.info(f"Saving processed data to {file_path}")
        df.to_csv(file_path, index=False)
        logger.info("Data saved successfully.")
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise
