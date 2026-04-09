const SENTIMENT_STYLES = {
  favorable: {
    bg: "bg-green-100",
    text: "text-green-700",
    border: "border-green-300",
  },
  defavorable: {
    bg: "bg-red-100",
    text: "text-red-700",
    border: "border-red-300",
  },
  neutre: {
    bg: "bg-gray-100",
    text: "text-gray-600",
    border: "border-gray-300",
  },
};

function SentimentBadge({ label, score }) {
  const style = SENTIMENT_STYLES[label] || SENTIMENT_STYLES.neutre;
  const percentage = score != null ? Math.round(score * 100) : null;

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full border ${style.bg} ${style.text} ${style.border}`}
    >
      <span className="capitalize">{label}</span>
      {percentage !== null && (
        <span className="opacity-70">({percentage}%)</span>
      )}
    </span>
  );
}

export default SentimentBadge;
