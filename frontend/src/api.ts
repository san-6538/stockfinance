import type {
  AnalyticsPoint,
  PipelineRunResult,
  Range,
  SearchResult,
  StockInfo,
  StockSummary,
} from "./types";

// Empty base => relative URLs (dev proxy / nginx in prod). Override with
// VITE_API_URL to point at a backend on a different origin. Accepts a bare
// hostname (e.g. Render's fromService `host`) and adds https:// if missing.
const RAW = (import.meta.env.VITE_API_URL ?? "").trim().replace(/\/$/, "");
const BASE = RAW && !/^https?:\/\//.test(RAW) ? `https://${RAW}` : RAW;

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listStocks: () => get<StockInfo[]>("/api/stocks"),

  search: (q: string) =>
    get<SearchResult[]>(`/api/search?q=${encodeURIComponent(q)}`),

  analytics: (ticker: string, range: Range) =>
    get<AnalyticsPoint[]>(
      `/api/stocks/${encodeURIComponent(ticker)}/analytics?range=${range}`
    ),

  summary: (ticker: string) =>
    get<StockSummary>(`/api/stocks/${encodeURIComponent(ticker)}/summary`),

  exportUrl: (ticker: string) =>
    `${BASE}/api/stocks/${encodeURIComponent(ticker)}/export.csv`,

  async runPipeline(tickers?: string[]): Promise<PipelineRunResult> {
    const res = await fetch(`${BASE}/api/pipeline/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tickers: tickers ?? null }),
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText);
      throw new Error(`${res.status}: ${detail}`);
    }
    return res.json();
  },
};
