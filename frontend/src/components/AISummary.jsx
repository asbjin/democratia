import { useState } from "react";
import api from "../services/api";

// En dessous de ce nombre de mots, le texte est deja court : inutile de resumer.
const MIN_WORDS = 40;

function AISummary({ text, interventionId, context, theme }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const wordCount = text ? text.trim().split(/\s+/).filter(Boolean).length : 0;
  // Pas de bouton de resume pour un texte deja court (regle prof + rapidite)
  if (wordCount < MIN_WORDS) return null;

  const handleGenerate = () => {
    if (loading || summary) return;
    setLoading(true);
    setError(null);

    api
      .post("/ia/resume", {
        text,
        intervention_id: interventionId,
        context: context || "",
        theme: theme || "",
      })
      .then((res) => setSummary(res.data))
      .catch(() => setError("Erreur lors de la generation"))
      .finally(() => setLoading(false));
  };

  if (summary) {
    return (
      <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
            Resume automatique
          </span>
          {summary.cached && (
            <span className="text-xs text-gray-400">en cache</span>
          )}
        </div>
        <p className="text-sm text-gray-700 leading-relaxed">{summary.resume}</p>
      </div>
    );
  }

  if (error) {
    return (
      <p className="mt-2 text-xs text-red-400">{error}</p>
    );
  }

  return (
    <button
      onClick={handleGenerate}
      disabled={loading}
      className="mt-2 text-xs px-3 py-1.5 rounded-lg border border-blue-300 text-blue-600 hover:bg-blue-50 transition-colors disabled:opacity-50"
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <span className="animate-spin inline-block w-3 h-3 border border-blue-400 border-t-transparent rounded-full"></span>
          Generation...
        </span>
      ) : (
        "Generer le resume"
      )}
    </button>
  );
}

export default AISummary;
