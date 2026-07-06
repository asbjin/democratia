import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import TimelineChart from "../components/TimelineChart";

function StatBox({ label, value, color }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-5 text-center">
      <p className="text-2xl font-bold" style={color ? { color } : undefined}>
        {value}
      </p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function GroupeDetailPage() {
  const { id } = useParams();
  const [detail, setDetail] = useState(null);
  const [dash, setDash] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([api.get(`/groupes/${id}`), api.get(`/groupes/${id}/dashboard`)])
      .then(([dRes, dashRes]) => {
        setDetail(dRes.data);
        setDash(dashRes.data);
      })
      .catch(() => setError("Groupe non trouve"))
      .finally(() => setLoading(false));
  }, [id]);

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

  if (error || !detail) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 text-center">
        <p className="text-red-500 text-lg">{error || "Groupe non trouve"}</p>
        <Link to="/groupes" className="text-accent underline mt-4 block">
          Retour aux groupes
        </Link>
      </div>
    );
  }

  const couleur = detail.couleur || "#475569";
  const membres = detail.deputes || [];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Link to="/groupes" className="text-accent hover:underline text-sm mb-4 block">
        &larr; Retour aux groupes
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6 flex items-center gap-5">
        <div className="w-4 h-16 rounded-full" style={{ backgroundColor: couleur }} />
        <div>
          <h1 className="text-3xl font-bold text-primary">{detail.nom}</h1>
          {detail.sigle && <span className="text-gray-500">{detail.sigle}</span>}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatBox label="Membres" value={detail.nb_membres} color={couleur} />
        <StatBox label="Interventions" value={(dash?.stats?.nb_interventions ?? 0).toLocaleString("fr-FR")} />
        <StatBox label="Amendements" value={dash?.stats?.nb_amendements ?? 0} />
        <StatBox label="Cohesion" value={dash?.cohesion != null ? `${dash.cohesion}%` : "—"} />
      </div>

      {/* Top deputes */}
      {dash?.top_deputes?.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-4">
            Deputes les plus actifs
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dash.top_deputes.map((d) => (
              <Link
                key={d.id}
                to={`/depute/${d.id}`}
                className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-5"
              >
                <p className="font-semibold text-primary">
                  {d.prenom} {d.nom}
                </p>
                {d.departement && (
                  <p className="text-sm text-gray-500">{d.departement}</p>
                )}
                <p className="text-sm text-gray-600 mt-2">
                  <span className="font-medium">{d.nb_interventions}</span> interventions
                </p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Timeline */}
      {dash?.timeline?.length > 0 && (
        <section className="mb-8">
          <TimelineChart data={dash.timeline} />
        </section>
      )}

      {/* All members */}
      <section>
        <h2 className="text-xl font-semibold text-primary mb-4">
          Membres ({membres.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {membres.map((d) => (
            <Link
              key={d.id}
              to={`/depute/${d.id}`}
              className="flex items-center justify-between bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow px-4 py-3"
            >
              <span className="text-sm font-medium text-gray-700">
                {d.prenom} {d.nom}
              </span>
              {d.departement && (
                <span className="text-xs text-gray-400">{d.departement}</span>
              )}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default GroupeDetailPage;
