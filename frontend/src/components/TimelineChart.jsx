import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function TimelineChart({ data }) {
  if (!data || data.length === 0) return null;

  // Show last 12 months
  const last12 = data.slice(-12);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-primary mb-4">
        Activite sur les 12 derniers mois
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={last12}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" tick={{ fontSize: 11 }} />
          <YAxis />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#1B3A5C"
            fill="#2E75B6"
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TimelineChart;
