import pandas as pd
import logging

logger = logging.getLogger(__name__)

try:
    import pandas_ta as ta
except ImportError:
    logger.warning("pandas_ta not found. Technical indicators cannot be computed.")
    ta = None


def add_indicators(df: pd.DataFrame, close_col: str = 'Close') -> pd.DataFrame:
    """
    Add technical indicators (SMA, RSI, MACD) to the price DataFrame.

    This function operates on a DataFrame for a single ticker or on a multi-ticker DataFrame
    if grouped beforehand. It returns a new DataFrame with indicator columns appended.

    Args:
        df (pd.DataFrame): Input DataFrame containing price data.
        close_col (str): The name of the column containing closing prices. Default is 'Close'.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with added columns:
                      - 'SMA_20': Simple Moving Average (20 periods)
                      - 'RSI_14': Relative Strength Index (14 periods)
                      - 'MACD': MACD line
                      - 'MACD_signal': MACD signal line

    Raises:
        ImportError: If pandas_ta is not installed.
    """
    if ta is None:
        raise ImportError('pandas_ta not available. Install with `pip install pandas_ta`')

    # Ensure the close column exists
    if close_col not in df.columns:
        raise ValueError(f"Column '{close_col}' not found in DataFrame.")

    df = df.copy()

    try:
        # Simple Moving Average
        df['SMA_20'] = ta.sma(df[close_col], length=20)

        # RSI
        df['RSI_14'] = ta.rsi(df[close_col], length=14)

        # MACD
        macd_df = ta.macd(df[close_col])
        if macd_df is not None:
             # pandas_ta returns columns with specific suffixes
            if 'MACD_12_26_9' in macd_df.columns:
                df['MACD'] = macd_df['MACD_12_26_9']
            if 'MACDs_12_26_9' in macd_df.columns:
                df['MACD_signal'] = macd_df['MACDs_12_26_9']

        logger.info("Technical indicators added successfully.")

    except Exception as e:
        logger.error(f"Error computing indicators: {e}")
        raise

    return df

