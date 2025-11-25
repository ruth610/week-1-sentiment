# 📈 Predicting Stock Price Movements Using News Sentiment  
**Nova Financial Solutions**  

This project explores how **financial news headlines influence stock market movements** using a combined workflow of **data engineering, sentiment analysis, and quantitative finance techniques**.  

The goal is to build a **reproducible data pipeline** that:  
1. Extracts patterns from news headlines  
2. Computes sentiment scores  
3. Aligns news events with stock price movements  
4. Computes technical indicators  
5. Analyzes correlations and predictive relationships  

---

## 🚀 Challenge Overview  
Financial markets move rapidly in response to information. Understanding **how news sentiment affects short-term stock returns** is a core capability of quantitative trading firms.  

This project simulates a real-world workflow used by analysts at **Nova Financial Solutions**, combining:  
- Data Engineering (DE)  
- Financial Analytics (FA)  
- Machine Learning Engineering (MLE)  
- Reproducible software practices (Git, CI/CD, notebooks, Python modules)  

The workload is intentionally intense — mirroring fast-paced financial analytics environments.

---

## 🎯 Business Objective  
As a Data Analyst at Nova Financial Solutions, my mission is to determine:

### **1. Sentiment → Price Movement Link**  
Perform sentiment analysis on each headline and quantify the tone (positive/neutral/negative).  
Understand if certain sentiments reliably predict price moves.

### **2. Correlation Between News & Returns**  
Determine whether news sentiment has impact on:  
- same-day returns  
- next-day returns  
- multi-day returns  
- volatility  
- volume changes

### **3. Investment Strategy Insights**  
Use results to propose **data-backed trading insights**, such as:  
- “Highly negative headlines predict higher short-term volatility”  
- “Positive sentiment correlates with next-day gains for tech stocks"  

---

## 📚 Dataset Overview  

### **Financial News + Price Integration Dataset (FNSPID)**  
The dataset contains:  

| Column      | Description |
|-------------|-------------|
| **headline** | Short news headline summarizing financial event |
| **url** | Link to full article |
| **publisher** | Source or author |
| **date** | UTC-4 timestamp of article publication |
| **stock** | Stock ticker symbol (AAPL, TSLA, AMZN, etc.) |

This dataset is enriched with **price data** containing:  
- Open  
- High  
- Low  
- Close  
- Volume  

---

## 🗂 Folder Structure  

```bash
├── .github/workflows/unittests.yml # CI: Run tests
├── .vscode/settings.json
├── data/
│ ├── raw/ # raw_analyst_ratings.csv
│ └── processed/ # cleaned and merged datasets
├── notebooks/
│ ├── 01_EDA.ipynb
│ ├── 02_text_analysis.ipynb
│ └── 03_time_series_indicators.ipynb
├── src/
│ ├── data_prep.py # load/clean/preprocess datasets
│ ├── sentiment.py # headline sentiment functions
│ ├── indicators.py # RSI, MACD, SMA etc.
│ ├── analysis.py # correlations, regressions
│ └── utils.py
├── scripts/
│ ├── run_eda.sh
│ ├── compute_indicators.sh
│ └── export_summary.sh
├── tests/
│ ├── test_data_prep.py
│ └── test_indicators.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Environment Setup  

### **1. Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate    # Mac/Linux
.venv\Scripts\activate       # Windows
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Start Jupyter
```bash
jupyter lab
```

## 🔍 Task 1 — Exploratory Data Analysis (EDA)
1. Descriptive Statistics

  - Headline length distributions
  
  - Article counts per publisher
  
  - News volume over time
  
  - Publishing time-of-day patterns

2. Text Analysis

  - TF-IDF keyword extraction
  
  - Topic modeling (optional: LDA)
  
  - Frequent financial event patterns (e.g. “price target”, “downgrade”, “Earnings beat”)

3. Time Series News Trends

  - Publication spikes around earnings
  
  - Daily vs intraday publication rates
  
  - Publisher behavioural differences

Outputs stored in:

notebooks/01_EDA.ipynb
data/processed/cleaned_data.csv


## 🧠 Task 2 — Price Data & Technical Indicators
A. Align News With Market Dates

Rules:

  - If headline time < 09:30 → same trading day
  
  - If headline time > 16:00 → next trading day
  
  - If timezone unknown → use article date (daily frequency)

B. Compute Returns
```bash
df['daily_return'] = df['Close'].pct_change()
df['return_next_1d'] = df['Close'].pct_change().shift(-1)
df['return_next_3d'] = df['Close'].pct_change(periods=3).shift(-3)
```

C. Add Indicators

Defined in src/indicators.py:
```bash
import pandas_ta as ta

def add_indicators(df):
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    return df
```
D. Merge With Sentiment

For each (stock, date):

  1. Aggregate news sentiment (mean, median, count)
  
  2. Join with price data


## 📊 Task 3 — Correlation & Statistical Analysis

Functions in src/analysis.py include:

Correlations

  - sentiment vs daily return
  
  - sentiment vs next-day return
  
  - sentiment vs volatility (rolling std)

  - sentiment vs volume

Hypothesis tests

  - T-tests comparing returns after positive vs negative sentiment
  
  - Pearson / Spearman correlation

Regression models:
```bash
return_next_1d ~ sentiment + RSI + prev_return + volume_change
```
Visualizations

  - Scatterplots: sentiment vs next-day return
  
  - Boxplots: sentiment groups (negative/neutral/positive)
  
  - Price indicators vs sentiment patterns

## 📈 What This Project Produces

| Output                          | Location                                      |
|---------------------------------|-----------------------------------------------|
| Cleaned processed dataset       | data/processed/                               |
| Sentiment-scored dataset        | data/processed/sentiment.csv                  |
| EDA notebook                    | notebooks/01_EDA.ipynb                        |
| Technical indicators notebook   | notebooks/03_time_series_indicators.ipynb     |
| Analysis scripts                | src/analysis.py                               |
| Visual plots                   | notebooks/ or reports/                         |
| Interim PDF report              | docs/interim_report.pdf                       |


## 🧪 Testing & CI

Automated tests run using GitHub Actions:

  - Data cleaning tests
  
  - Indicator accuracy tests
  
  - Smoke tests for sentiment model

Run locally:
```bash
pytest -q
```

## 🛠 Tools & Technologies

Python (Pandas, NumPy, Matplotlib, Seaborn)

NLP: VADER, TextBlob, TF-IDF, optional transformers

Technical Analysis: pandas_ta, TA-Lib

Jupyter Notebooks

Git + GitHub + CI/CD

Regression & statistical tests

## ✔️ Author

Kalkidan Abreham
10 Academy – Week 1 Challenge
Nova Financial Solutions (Training Simulation)
