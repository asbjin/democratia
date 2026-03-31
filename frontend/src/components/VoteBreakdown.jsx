import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = { pour: "#27AE60", contre: "#E74C3C", abstention: "#95A5A6" };
const LABELS = { pour: "Pour", contre: "Contre", abstention: "Abstention" };

function VoteBreakdown({ scrutin }) {
  if (!scrutin) return null;

  const data = [
    { name: LABELS.pour, value: scrutin.nb_pour || 0 },
    { name: LABELS.contre, value: scrutin.nb_contre || 0 },
    { name: LABELS.abstention, value: scrutin.nb_abstention || 0 },
  ].filter((d) => d.value > 0);

  if (data.length === 0) return null;

  const colorList = [COLORS.pour, COLORS.contre, COLORS.abstention];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h4 className="text-sm font-semibold text-primary mb-3 truncate" title={scrutin.titre}>
        {scrutin.titre}
      </h4>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={80}
            dataKey="value"
            label={({ name, value }) => `${name}: ${value}`}
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={colorList[index]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default VoteBreakdown;
