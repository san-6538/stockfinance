import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnalyticsPoint } from "../types";

export function ReturnsChart({ data }: { data: AnalyticsPoint[] }) {
  const rows = data.map((d) => ({ ...d, pct: d.returns === null ? null : d.returns * 100 }));
  return (
    <div className="chart">
      <h3>Daily Returns (%)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={rows} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#22304a" strokeDasharray="3 3" />
          <XAxis dataKey="date" stroke="#7c8aa5" tick={{ fontSize: 11 }} minTickGap={40} />
          <YAxis stroke="#7c8aa5" tick={{ fontSize: 11 }} width={56} />
          <Tooltip
            contentStyle={{ background: "#0e1726", border: "1px solid #22304a" }}
            labelStyle={{ color: "#cbd5e1" }}
            formatter={(v: number) => `${v.toFixed(2)}%`}
          />
          <Bar dataKey="pct" name="Return">
            {rows.map((r, i) => (
              <Cell key={i} fill={(r.pct ?? 0) >= 0 ? "#34d399" : "#f87171"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
