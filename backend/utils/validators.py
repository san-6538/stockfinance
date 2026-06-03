def validate_dataframe(df):
    required_columns = ["Date", "Close", "ticker"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
