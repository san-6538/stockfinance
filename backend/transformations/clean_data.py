import pandas as pd
from utils.validators import validate_dataframe
from utils.logger import logger

def clean(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data")

    df = df.dropna()
    df = df.sort_values("Date")

    validate_dataframe(df)

    return df
