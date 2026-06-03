import pandas as pd
from utils.logger import logger

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Generating features")

    df["returns"] = df["Close"].pct_change()
    df["ma_20"] = df["Close"].rolling(20).mean()
    df["ma_50"] = df["Close"].rolling(50).mean()
    df["volatility"] = df["returns"].rolling(20).std()

    return df.dropna()
