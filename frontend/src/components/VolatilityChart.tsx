import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnalyticsPoint } from "../types";

export function VolatilityChart({ data }: { data: AnalyticsPoint[] }) {
  return (
    <div className="chart">
      <h3>Volatility (20-day rolling)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="vol" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.6} />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#22304a" strokeDasharray="3 3" />
          <XAxis dataKey="date" stroke="#7c8aa5" tick={{ fontSize: 11 }} minTickGap={40} />
          <YAxis stroke="#7c8aa5" tick={{ fontSize: 11 }} width={56} />
          <Tooltip
            contentStyle={{ background: "#0e1726", border: "1px solid #22304a" }}
            labelStyle={{ color: "#cbd5e1" }}
          />
          <Area type="monotone" dataKey="volatility" name="Volatility" stroke="#a78bfa" fill="url(#vol)" strokeWidth={1.5} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
