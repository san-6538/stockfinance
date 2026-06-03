export interface StockInfo {
  ticker: string;
  name: string;
  has_data: boolean;
}

export interface AnalyticsPoint {
  date: string;
  close: number | null;
  returns: number | null;
  ma_20: number | null;
  ma_50: number | null;
  volatility: number | null;
}

export interface StockSummary {
  ticker: string;
  name: string;
  points: number;
  as_of: string | null;
  latest_close: number | null;
  prev_close: number | null;
  change: number | null;
  change_pct: number | null;
  volatility: number | null;
}

export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}

export interface PipelineRunResult {
  status: string;
  files_processed: number;
  rows_written: number;
  tickers: string[];
}

export const RANGES = ["1M", "3M", "6M", "1Y", "3Y", "5Y", "MAX"] as const;
export type Range = (typeof RANGES)[number];
