import pandas as pd
import yfinance as yf
import logging
import os

logger = logging.getLogger(__name__)

def download_price_data(ticker: str, start_date: str, end_date: str, save_path: str = None) -> pd.DataFrame:
    """
    Download historical price data from YFinance.
    """
    logger.info(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            logger.warning(f"No data found for {ticker}")
            return pd.DataFrame()

        # Reset index to make Date a column
        df = df.reset_index()

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            df.to_csv(save_path, index=False)
            logger.info(f"Saved price data to {save_path}")

        return df
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {e}")
        return pd.DataFrame()

def load_price_data(path: str, date_col: str = "Date") -> pd.DataFrame:

    df = pd.read_csv(path)
    # Standardize column names (common variants)
    df.columns = [c.strip() for c in df.columns]
    if date_col not in df.columns:
        raise ValueError(f"Date column '{date_col}' not found in price data")


    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")


    df = df.sort_values(date_col).reset_index(drop=True)
    return df