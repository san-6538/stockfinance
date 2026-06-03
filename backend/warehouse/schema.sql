CREATE TABLE IF NOT EXISTS stock_analytics (
    date DATE,
    ticker TEXT,
    close DOUBLE,
    returns DOUBLE,
    ma_20 DOUBLE,
    ma_50 DOUBLE,
    volatility DOUBLE,
    PRIMARY KEY (date, ticker)
);
