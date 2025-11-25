import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm




def compute_returns(df: pd.DataFrame, close_col: str = 'Close', group_col: str = 'Stock') -> pd.DataFrame:
    df = df.copy()
    df['daily_return'] = df.groupby(group_col)[close_col].pct_change()
    df['return_next_1d'] = df.groupby(group_col)['daily_return'].shift(-1)
    df['return_next_3d'] = (df.groupby(group_col)[close_col].shift(-3) - df[close_col]) / df[close_col]
    return df




def correlation_matrix(df: pd.DataFrame, cols: list = None, figsize=(10, 8)) -> pd.DataFrame:
    if cols is None:
        cols = ['mean_sentiment', 'daily_return', 'return_next_1d', 'RSI_14', 'SMA_20', 'MACD']


    corr = df[cols].corr()
    plt.figure(figsize=figsize)
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')
    plt.title('Correlation matrix')
    plt.tight_layout()
    plt.show()
    return corr




def regression_return_next_day(df: pd.DataFrame, features: list = None, target: str = 'return_next_1d'):
    """
    Simple OLS regression predicting next-day return.
    Returns statsmodels summary object.
    """
    df_clean = df.dropna(subset=[target] + (features or []))
    if features is None:
        features = ['mean_sentiment', 'daily_return', 'RSI_14']


    X = df_clean[features]
    X = sm.add_constant(X)
    y = df_clean[target]


    model = sm.OLS(y, X).fit()
    return model




def t_test_groups(df: pd.DataFrame, score_col: str = 'mean_sentiment', target: str = 'return_next_1d', threshold: float = 0.2):
    """
    Compare future returns for positive vs negative sentiment groups using t-test.
    Positive if score_col > threshold, Negative if score_col < -threshold.
    """
    from scipy import stats


    pos = df[df[score_col] > threshold][target].dropna()
    neg = df[df[score_col] < -threshold][target].dropna()


    tstat, pval = stats.ttest_ind(pos, neg, equal_var=False, nan_policy='omit')
    return {'tstat': tstat, 'pval': pval, 'n_pos': len(pos), 'n_neg': len(neg)}

