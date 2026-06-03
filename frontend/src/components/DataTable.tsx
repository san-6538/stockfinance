import type { AnalyticsPoint } from "../types";
import { fmtNum } from "../format";

export function DataTable({ data }: { data: AnalyticsPoint[] }) {
  // Most recent first, capped for the DOM (full data is in the CSV export).
  const rows = [...data].reverse().slice(0, 60);
  return (
    <div className="table-wrap">
      <h3>Recent Data</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Close</th>
            <th>Return</th>
            <th>MA 20</th>
            <th>MA 50</th>
            <th>Volatility</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.date}>
              <td>{r.date}</td>
              <td>{fmtNum(r.close)}</td>
              <td className={(r.returns ?? 0) >= 0 ? "pos" : "neg"}>
                {r.returns === null ? "—" : `${(r.returns * 100).toFixed(2)}%`}
              </td>
              <td>{fmtNum(r.ma_20)}</td>
              <td>{fmtNum(r.ma_50)}</td>
              <td>{r.volatility === null ? "—" : fmtNum(r.volatility, 4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
