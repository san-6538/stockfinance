import type { StockSummary } from "../types";
import { fmtNum, fmtPct } from "../format";

export function SummaryCards({ s }: { s: StockSummary | null }) {
  if (!s || s.points === 0) return null;
  const up = (s.change ?? 0) >= 0;
  return (
    <div className="cards">
      <div className="card">
        <div className="card-label">Latest Close</div>
        <div className="card-value">{fmtNum(s.latest_close)}</div>
        <div className="card-sub">as of {s.as_of ?? "—"}</div>
      </div>
      <div className="card">
        <div className="card-label">Daily Change</div>
        <div className={`card-value ${up ? "pos" : "neg"}`}>
          {up ? "▲" : "▼"} {fmtNum(Math.abs(s.change ?? 0))}
        </div>
        <div className={`card-sub ${up ? "pos" : "neg"}`}>
          {fmtPct(s.change_pct)}
        </div>
      </div>
      <div className="card">
        <div className="card-label">Volatility (20d)</div>
        <div className="card-value">
          {s.volatility === null ? "—" : fmtPct(s.volatility * 100)}
        </div>
        <div className="card-sub">rolling std of returns</div>
      </div>
      <div className="card">
        <div className="card-label">Data Points</div>
        <div className="card-value">{s.points.toLocaleString()}</div>
        <div className="card-sub">trading days</div>
      </div>
    </div>
  );
}
