import pandas as pd

def load_price_data(path: str, date_col: str = "Date") -> pd.DataFrame:

    df = pd.read_csv(path)
    # Standardize column names (common variants)
    df.columns = [c.strip() for c in df.columns]
    if date_col not in df.columns:
        raise ValueError(f"Date column '{date_col}' not found in price data")


    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")


    df = df.sort_values(date_col).reset_index(drop=True)
    return df