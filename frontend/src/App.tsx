import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { RANGES, type AnalyticsPoint, type Range, type StockInfo, type StockSummary } from "./types";
import { SearchBox } from "./components/SearchBox";
import { SummaryCards } from "./components/SummaryCards";
import { PriceChart } from "./components/PriceChart";
import { VolatilityChart } from "./components/VolatilityChart";
import { ReturnsChart } from "./components/ReturnsChart";
import { DataTable } from "./components/DataTable";

export default function App() {
  const [stocks, setStocks] = useState<StockInfo[]>([]);
  const [ticker, setTicker] = useState<string>("");
  const [range, setRange] = useState<Range>("1Y");
  const [data, setData] = useState<AnalyticsPoint[]>([]);
  const [summary, setSummary] = useState<StockSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadStocks = useCallback(async (select?: string) => {
    const list = await api.listStocks();
    setStocks(list);
    const withData = list.filter((s) => s.has_data);
    const next = select || ticker || (withData[0] ?? list[0])?.ticker || "";
    if (next) setTicker(next);
  }, [ticker]);

  useEffect(() => {
    loadStocks().catch((e) => setError(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadData = useCallback(async () => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    try {
      const [pts, sum] = await Promise.all([
        api.analytics(ticker, range),
        api.summary(ticker),
      ]);
      setData(pts);
      setSummary(sum);
    } catch (e) {
      setError(String(e));
      setData([]);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, [ticker, range]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function refresh(target: string) {
    setBusy(`Fetching latest data for ${target}…`);
    setError(null);
    try {
      await api.runPipeline([target]);
      await loadStocks(target);
      await loadData();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  async function analyze(symbol: string) {
    const t = symbol.trim().toUpperCase();
    if (!t) return;
    setBusy(`Analyzing ${t}… (downloading from Yahoo Finance)`);
    setError(null);
    try {
      const res = await api.runPipeline([t]);
      if (res.rows_written === 0) {
        setError(`No data found for "${t}". Try searching by company name instead.`);
      } else {
        setTicker(t);
        await loadStocks(t);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>📈 Financial Data Platform</h1>
          <p className="subtitle">
            Ingest · transform · analyze stock time-series — powered by Yahoo Finance &amp; DuckDB
          </p>
        </div>
      </header>

      <section className="controls">
        <div className="control">
          <label>Ticker</label>
          <select value={ticker} onChange={(e) => setTicker(e.target.value)}>
            {stocks.map((s) => (
              <option key={s.ticker} value={s.ticker}>
                {s.ticker} — {s.name}
                {s.has_data ? "" : " (no data)"}
              </option>
            ))}
          </select>
        </div>

        <div className="control">
          <label>Range</label>
          <div className="ranges">
            {RANGES.map((r) => (
              <button
                key={r}
                className={r === range ? "range active" : "range"}
                onClick={() => setRange(r)}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className="control grow">
          <label>Search &amp; analyze any stock</label>
          <SearchBox onPick={analyze} disabled={!!busy} />
        </div>

        <div className="control">
          <label>&nbsp;</label>
          <div className="addrow">
            <button onClick={() => ticker && refresh(ticker)} disabled={!!busy || !ticker}>
              ⟳ Refresh
            </button>
            {ticker && (
              <a className="btn-link" href={api.exportUrl(ticker)}>
                ⤓ CSV
              </a>
            )}
          </div>
        </div>
      </section>

      {busy && <div className="banner busy">{busy}</div>}
      {error && <div className="banner error">{error}</div>}

      {summary && summary.points === 0 && !loading && (
        <div className="banner">
          No data for {ticker} yet. Click <b>Refresh</b> to fetch it.
        </div>
      )}

      <SummaryCards s={summary} />

      {loading ? (
        <div className="banner">Loading…</div>
      ) : data.length > 0 ? (
        <>
          <PriceChart data={data} />
          <div className="grid2">
            <VolatilityChart data={data} />
            <ReturnsChart data={data} />
          </div>
          <DataTable data={data} />
        </>
      ) : null}

      <footer>
        <span>
          API: <a href="/docs">/docs</a> · Same image runs anywhere via Docker.
        </span>
      </footer>
    </div>
  );
}
