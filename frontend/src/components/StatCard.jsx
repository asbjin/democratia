function StatCard({ label, value, subtext, color = "text-accent" }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 text-center">
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
      {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
    </div>
  );
}

export default StatCard;
