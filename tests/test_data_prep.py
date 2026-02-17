import pandas as pd
import pytest
from src.data_prep import clean_data, feature_engineering

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "headline": ["Stock hits new high", "Market crashes", "Company report"],
        "publisher": ["Benzinga", "CNBC", "investor@example.com"],
        "date": ["2020-01-01", "2020-01-02", "Invalid date"]
    })

def test_clean_data(sample_data):
    clean_df = clean_data(sample_data)

    # Check duplicate removal (none here, but logic exists)
    assert len(clean_df) == 3

    # Check date conversion
    assert pd.api.types.is_datetime64_ns_dtype(clean_df["date"])
    # Invalid date should be NaT
    assert pd.isna(clean_df.loc[2, "date"])

def test_feature_engineering(sample_data):
    fe_df = feature_engineering(sample_data)

    assert "headline_length" in fe_df.columns
    assert fe_df.loc[0, "headline_length"] == len("Stock hits new high")

    assert "publisher_domain" in fe_df.columns
    # Check domain extraction
    assert fe_df.loc[2, "publisher_domain"] == "example.com"
