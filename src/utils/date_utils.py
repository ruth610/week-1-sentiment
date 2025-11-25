import pandas as pd
from typing import Optional


def ensure_datetime_utc(series: pd.Series) -> pd.Series:
    """
    Safely convert a Series of datelike objects (possibly mixed tz-aware and naive strings)
    into timezone-aware UTC datetimes.


    Returns a series with dtype datetime64[ns, UTC]. Invalid parses -> NaT.
    """
    # Force string then parse with utc=True to handle mixed tz
    return pd.to_datetime(series.astype(str), errors="coerce", utc=True)




def align_to_market_date(news_df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Given a news DataFrame with a datetime-like `date_col` (ideally tz-aware UTC),
    produce a `market_date` column representing the trading date the news should affect.


    Rules used:
    - Convert timestamps to America/New_York (ET) to reason about market open/close
    - If publish_time > 16:00 ET -> assign next trading day
    - Else -> same day


    Returns a copy of the DataFrame with additional columns: date_utc, date_et, market_date
    """
    df = news_df.copy()


    # Create tz-aware UTC date
    df['date_utc'] = ensure_datetime_utc(df[date_col])


    # If conversion failed for some rows, they will be NaT
    # Convert to ET (America/New_York) to determine market open/close
    df['date_et'] = df['date_utc'].dt.tz_convert('America/New_York')


    # Market date baseline is the calendar date in ET
    df['market_date'] = df['date_et'].dt.date


    # Identify times after market close (16:00 ET) -> assign next day
    after_close_mask = df['date_et'].dt.time > pd.to_datetime('16:00').time()
    df.loc[after_close_mask, 'market_date'] = df.loc[after_close_mask, 'market_date'].apply(lambda d: d + pd.Timedelta(days=1))


    # Normalize market_date to pandas Timestamp (no timezone)
    df['market_date'] = pd.to_datetime(df['market_date']).dt.normalize()


    return df