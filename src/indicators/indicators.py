import pandas as pd


try:
    import pandas_ta as ta
except Exception:
    ta = None




def add_indicators(df: pd.DataFrame, close_col: str = 'Close') -> pd.DataFrame:
    """
    Add SMA_20, RSI_14, MACD and MACD_signal to the price DataFrame.
    This function operates on a DataFrame for a single ticker or on a multi-ticker DataFrame
    if grouped beforehand. It returns a new DataFrame with indicator columns.
    If pandas_ta is not installed, the function will raise an informative error.
    """
    if ta is None:
        raise ImportError('pandas_ta not available. Install with `pip install pandas_ta`')


    df = df.copy()


    # Simple Moving Average
    df['SMA_20'] = ta.sma(df[close_col], length=20)


    # RSI
    df['RSI_14'] = ta.rsi(df[close_col], length=14)


    # MACD
    macd_df = ta.macd(df[close_col])
    # pandas_ta returns columns with keys like 'MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9'
    if 'MACD_12_26_9' in macd_df.columns:
        df['MACD'] = macd_df['MACD_12_26_9']
    if 'MACDs_12_26_9' in macd_df.columns:
        df['MACD_signal'] = macd_df['MACDs_12_26_9']


    return df

