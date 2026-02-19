import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging

logger = logging.getLogger(__name__)

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')


class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using VADER.
        Returns compound score (-1 to 1).
        """
        if not isinstance(text, str):
            return 0.0
        scores = self.sia.polarity_scores(text)
        return scores['compound']

    def process_dataframe(self, df: pd.DataFrame, text_col: str = 'headline') -> pd.DataFrame:
        """
        Apply sentiment analysis to a dataframe column.
        Adds 'compound' sentiment score column.
        """
        logger.info(f"Calculating sentiment for {len(df)} rows...")
        if text_col not in df.columns:
            raise ValueError(f"Column '{text_col}' not found in dataframe.")

        df = df.copy()
        # Ensure text is string
        df[text_col] = df[text_col].astype(str)

        # Apply sentiment
        tqdm_available = False
        try:
            from tqdm import tqdm
            tqdm.pandas()
            tqdm_available = True
        except ImportError:
            pass

        if tqdm_available:
             df['compound'] = df[text_col].progress_apply(self.analyze_sentiment)
        else:
             df['compound'] = df[text_col].apply(self.analyze_sentiment)

        # Convert sentiment to categorical (optional, for analysis)
        # df['sentiment_category'] = df['compound'].apply(lambda x: 'positive' if x > 0.05 else ('negative' if x < -0.05 else 'neutral'))

        return df

