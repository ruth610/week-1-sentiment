import pandas as pd
import numpy as np
import logging
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

from src.data_prep import load_data, clean_data, feature_engineering
from src.sentiment.analyzer import SentimentAnalyzer
from src.merge.merge_news_prices import aggregate_daily_sentiment, merge_sentiment_prices
from src.price.load_price_data import download_price_data, load_price_data
from src.indicators.indicators import add_indicators

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.model_path = config.get("model", {}).get("save_path", "models/sentiment_model.pkl")
        self.stocks = config.get("analysis", {}).get("stocks", ["AAPL", "MSFT", "GOOG"])


    def prepare_data(self):
        """
        Orchestrates the data preparation pipeline:
        1. Load & Clean Raw News
        2. Analyze Sentiment
        3. Load/Download Prices
        4. Calculate Indicators
        5. Merge Data
        6. Create Target
        """
        logger.info("Step 1: Loading & Cleaning News Data...")
        raw_path = self.config["data"]["raw_path"]
        try:
            df_news = load_data(raw_path)
            df_news = clean_data(df_news)
        except Exception as e:
            logger.error(f"Failed to load news data: {e}")
            return pd.DataFrame()

        logger.info("Step 2: Sentiment Analysis...")
        analyzer = SentimentAnalyzer()
        # Clean headline column for analysis
        if 'headline' in df_news.columns:
            df_news['headline'] = df_news['headline'].fillna('')
            df_news = analyzer.process_dataframe(df_news, text_col='headline')
        else:
            logger.error("Column 'headline' not found in news data.")
            return pd.DataFrame()

        # Rename 'date' to 'market_date' if present
        if 'date' in df_news.columns:
            df_news = df_news.rename(columns={'date': 'market_date'})

        # Ensure sentiment is aggregated
        daily_sentiment = aggregate_daily_sentiment(df_news, score_col='compound')

        final_df_list = []

        # Determine strict list of stocks to process
        # Use config if available, otherwise fallback to data
        target_stocks = self.config.get("analysis", {}).get("stocks", [])
        if not target_stocks:
             target_stocks = daily_sentiment['stock'].unique()

        # Limit to available stocks in data
        available_stocks = set(daily_sentiment['stock'].unique())
        stocks_to_process = [s for s in target_stocks if s in available_stocks]

        logger.info(f"Processing {len(stocks_to_process)} stocks: {stocks_to_process}")

        for stock in stocks_to_process:
            logger.info(f"Processing data for {stock}...")

            stock_sent = daily_sentiment[daily_sentiment['stock'] == stock].copy()
            if stock_sent.empty:
                continue

            # 3. Load/Download Prices
            # Determine date range
            min_date = stock_sent['market_date'].min()
            max_date = stock_sent['market_date'].max()

            start_str = (min_date - pd.Timedelta(days=30)).strftime('%Y-%m-%d') # Get some history for indicators
            end_str = (max_date + pd.Timedelta(days=5)).strftime('%Y-%m-%d')

            logger.info(f"Downloading price data for {stock} ({start_str} to {end_str})...")
            try:
                price_df = download_price_data(stock, start_date=start_str, end_date=end_str)
            except Exception as e:
                logger.error(f"Error downloading {stock}: {e}")
                continue

            if price_df.empty:
                logger.warning(f"No price data found for {stock}")
                continue

            # 4. Cleanup Price Data
            # Ensure Date column
            if isinstance(price_df.columns, pd.MultiIndex):
                original_cols = price_df.columns
                # Flatten multi-index columns if present (e.g., from yfinance)
                # Usually (Price, Ticker) -> just Price
                # But if we downloaded only 1 ticker, yfinance might not return MultiIndex?
                # Actually newer yfinance returns MultiIndex even for single ticker often.
                price_df.columns = price_df.columns.get_level_values(0)
                logger.debug(f"Flattened columns: {original_cols} -> {price_df.columns}")

            if 'Date' not in price_df.columns and not isinstance(price_df.index, pd.DatetimeIndex):
                 price_df = price_df.reset_index()

            # If date is in index, reset index to make it a column
            if isinstance(price_df.index, pd.DatetimeIndex):
                price_df = price_df.reset_index()

            # Rename 'Date' if needed (sometimes 'date' lowercase)
            price_df = price_df.rename(columns={'date': 'Date'})

            # Ensure price date is tz-naive to match sentiment (or both aware)
            # Simplest is to make both tz-naive (UTC normalized)
            if price_df['Date'].dt.tz is not None:
                price_df['Date'] = price_df['Date'].dt.tz_convert(None)

            # Also ensure sentiment date is naive in the merge function if needed,
            # but here we can't easily touch sentiment df inside the loop without affecting others?
            # Actually we copy stock_sent.
            if stock_sent['market_date'].dt.tz is not None:
                stock_sent['market_date'] = stock_sent['market_date'].dt.tz_convert(None)

            # Add Stock column for merging
            price_df['Stock'] = stock

            # normalize column names
            # standard yfinance returns capitalized 'Date', 'Open', 'Close' etc.

            # 5. Add Indicators
            try:
                # Expects 'Close' column
                price_df = add_indicators(price_df)
            except Exception as e:
                logger.warning(f"Indicator calculation failed for {stock}: {e}")
                # Continue without indicators if failed, or skip?
                # For now continue, maybe basic price features work

            # 6. Merge
            # The merge function expects 'Date' in price_df
            merged = merge_sentiment_prices(stock_sent, price_df, price_date_col='Date')

            if merged.empty:
                logger.warning(f"Merged dataframe empty for {stock}")
                continue

            # 7. Create Target
            # We want to predict if price goes UP next day
            # Calculate return
            merged['Close_Shift'] = merged['Close'].shift(-1)
            merged['Target'] = (merged['Close_Shift'] > merged['Close']).astype(int)

            # Drop NaN created by shift
            merged = merged.dropna(subset=['Close_Shift', 'Target'])

            final_df_list.append(merged)

        if not final_df_list:
             return pd.DataFrame()

        final_df = pd.concat(final_df_list, ignore_index=True)
        return final_df

    def train(self):
        logger.info("Starting training process...")
        df = self.prepare_data()

        if df.empty:
            logger.error("Training aborted: No data available.")
            return

        logger.info(f"Training on {len(df)} samples...")

        # Features & Target
        # Select numeric columns only
        features = ['mean_sentiment', 'SMA_20', 'RSI_14', 'MACD', 'MACD_signal']
        # Check if they exist
        features = [f for f in features if f in df.columns]

        X = df[features]
        y = df['Target']

        # Split (TimeSeriesSplit is better but using random for simplicity/demo)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # Model
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        # Evaluate
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        logger.info(f"Model Accuracy: {acc:.4f}")
        logger.info("\n" + classification_report(y_test, preds))

        # Save
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(clf, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
