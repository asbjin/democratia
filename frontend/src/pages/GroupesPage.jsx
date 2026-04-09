import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function GroupesPage() {
  const [groupes, setGroupes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/groupes")
      .then((res) => setGroupes(res.data.items || []))
      .catch(() => setError("Erreur lors du chargement des groupes"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg text-gray-500">Chargement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 text-center">
        <p className="text-red-500 text-lg">{error}</p>
      </div>
    );
  }

  const totalMembres = groupes.reduce((sum, g) => sum + (g.nb_membres || 0), 0);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-2">
        Groupes politiques
      </h1>
      <p className="text-gray-500 mb-8">
        {groupes.length} groupes &mdash; {totalMembres} deputes
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {groupes.map((groupe) => {
          const pct = totalMembres > 0
            ? ((groupe.nb_membres / totalMembres) * 100).toFixed(1)
            : 0;

          return (
            <button
              key={groupe.id}
              onClick={() => navigate(`/dashboard?q=&groupe=${groupe.id}`)}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 text-left"
            >
              <div className="flex items-center gap-4 mb-4">
                <div
                  className="w-4 h-12 rounded-full"
                  style={{ backgroundColor: groupe.couleur || "#94a3b8" }}
                />
                <div>
                  <h2 className="text-lg font-semibold text-primary">
                    {groupe.nom}
                  </h2>
                  {groupe.sigle && (
                    <span className="text-sm text-gray-500">{groupe.sigle}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold" style={{ color: groupe.couleur || "#475569" }}>
                    {groupe.nb_membres}
                  </p>
                  <p className="text-xs text-gray-400">membres</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-gray-600">{pct}%</p>
                  <p className="text-xs text-gray-400">de l'assemblee</p>
                </div>
              </div>

              {/* Progress bar */}
              <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: groupe.couleur || "#94a3b8",
                  }}
                />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default GroupesPage;
