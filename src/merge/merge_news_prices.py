import pandas as pd

def aggregate_daily_sentiment(news_df: pd.DataFrame, score_col: str = 'compound') -> pd.DataFrame:
    """
    Aggregate news sentiment per (stock, market_date).
    Expected columns in news_df: ['stock', 'market_date', score_col]
    Returns DataFrame with: stock, market_date, mean_sentiment, median_sentiment, num_articles
    """
    df = news_df.copy()


    # Ensure market_date is normalized date (no tz)
    if not pd.api.types.is_datetime64_any_dtype(df['market_date']):
        df['market_date'] = pd.to_datetime(df['market_date'])
    df['market_date'] = df['market_date'].dt.normalize()


    grouped = df.groupby(['stock', 'market_date']).agg(
    mean_sentiment=(score_col, 'mean'),
    median_sentiment=(score_col, 'median'),
    num_articles=(score_col, 'count')
    ).reset_index()


    return grouped




def merge_sentiment_prices(sent_df: pd.DataFrame, price_df: pd.DataFrame, price_date_col: str = 'Date', ticker_col: str = 'Stock') -> pd.DataFrame:
    """
    Merge aggregated sentiment DataFrame (sent_df) with price_df.


    The function assumes price_df has a column representing the ticker (ticker_col) and a date column (price_date_col).
    Returns merged DataFrame where sentiment columns align to the row of price Date.
    """
    # normalize price date
    price = price_df.copy()
    price[price_date_col] = pd.to_datetime(price[price_date_col])
    price['merge_date'] = price[price_date_col].dt.normalize()


    sent = sent_df.copy()
    sent['market_date'] = pd.to_datetime(sent['market_date']).dt.normalize()


    merged = pd.merge(
    price,
    sent,
    left_on=['merge_date', ticker_col],
    right_on=['market_date', 'stock'],
    how='left'
    )


    return merged