import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnalyticsPoint } from "../types";

export function PriceChart({ data }: { data: AnalyticsPoint[] }) {
  return (
    <div className="chart">
      <h3>Price &amp; Moving Averages</h3>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#22304a" strokeDasharray="3 3" />
          <XAxis dataKey="date" stroke="#7c8aa5" tick={{ fontSize: 11 }} minTickGap={40} />
          <YAxis stroke="#7c8aa5" tick={{ fontSize: 11 }} domain={["auto", "auto"]} width={56} />
          <Tooltip
            contentStyle={{ background: "#0e1726", border: "1px solid #22304a" }}
            labelStyle={{ color: "#cbd5e1" }}
          />
          <Legend />
          <Line type="monotone" dataKey="close" name="Close" stroke="#38bdf8" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="ma_20" name="MA 20" stroke="#fbbf24" dot={false} strokeWidth={1.5} />
          <Line type="monotone" dataKey="ma_50" name="MA 50" stroke="#f472b6" dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
