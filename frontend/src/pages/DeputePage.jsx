import { useState, useEffect } from "react";
import { useParams, Link, useSearchParams } from "react-router-dom";
import api from "../services/api";
import AISummary from "../components/AISummary";
import SentimentBadge from "../components/SentimentBadge";

const TABS = [
  { key: "activite", label: "Activite" },
  { key: "votes", label: "Votes" },
  { key: "questions", label: "Questions" },
  { key: "resume", label: "Resume IA" },
];

function DeputePage() {
  const { id } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [filter, setFilter] = useState(searchParams.get("q") || "");
  const [searchInput, setSearchInput] = useState(searchParams.get("q") || "");
  const [depute, setDepute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("activite");
  const [activite, setActivite] = useState(null);
  const [votes, setVotes] = useState(null);
  const [tabLoading, setTabLoading] = useState(false);
  const [groupeNom, setGroupeNom] = useState(null);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/deputes/${id}`)
      .then((res) => {
        setDepute(res.data);
        if (res.data.groupe_politique_id) {
          api
            .get(`/groupes/${res.data.groupe_politique_id}`)
            .then((gRes) => setGroupeNom(gRes.data.sigle || gRes.data.nom))
            .catch(() => setGroupeNom(res.data.groupe_politique_id));
        }
      })
      .catch(() => setError("Depute non trouve"))
      .finally(() => setLoading(false));
  }, [id]);

  // Load activite and votes (optionally filtered by the active search term)
  useEffect(() => {
    if (!depute) return;
    const params = filter ? { theme: filter } : {};

    api
      .get(`/deputes/${id}/activite`, { params })
      .then((res) => setActivite(res.data))
      .catch(() =>
        setActivite({
          depute_id: id,
          interventions: [],
          votes: [],
          amendements: [],
          total_interventions: 0,
          total_votes: 0,
          total_amendements: 0,
        })
      );

    api
      .get(`/deputes/${id}/votes`, { params })
      .then((res) => setVotes(res.data))
      .catch(() => setVotes({ total: 0, items: [] }));
  }, [id, depute, filter]);

  const applyFilter = (e) => {
    e.preventDefault();
    const v = searchInput.trim();
    setFilter(v);
    setSearchParams(v ? { q: v } : {});
  };

  const clearFilter = () => {
    setSearchInput("");
    setFilter("");
    setSearchParams({});
  };

  // Le retour au dashboard conserve le filtre actif (persistance de la recherche)
  const backTo = filter ? `/dashboard?q=${encodeURIComponent(filter)}` : "/dashboard";

  // Handle tab-specific loading states
  useEffect(() => {
    if (!depute) return;

    if (activeTab === "activite" && !activite) {
      setTabLoading(true);
    } else if (activeTab === "votes" && !votes) {
      setTabLoading(true);
    } else {
      setTabLoading(false);
    }
  }, [activeTab, activite, votes, depute]);

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

  if (error || !depute) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 text-center">
        <p className="text-red-500 text-lg">{error || "Depute non trouve"}</p>
        <Link to={backTo} className="text-accent underline mt-4 block">
          Retour au dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Link
        to={backTo}
        className="text-accent hover:underline text-sm mb-4 block"
      >
        &larr; Retour au dashboard
      </Link>

      {/* Search bar to filter this deputy's activity */}
      <form onSubmit={applyFilter} className="flex gap-2 mb-3">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder={`Filtrer l'activite de ${depute.prenom} ${depute.nom}...`}
          className="flex-1 px-4 py-2 rounded-lg border-2 border-accent focus:outline-none focus:border-primary text-gray-700"
        />
        <button
          type="submit"
          className="px-5 py-2 bg-accent text-white font-semibold rounded-lg hover:bg-primary transition-colors"
        >
          Rechercher
        </button>
        {filter && (
          <button
            type="button"
            onClick={clearFilter}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
          >
            Tout afficher
          </button>
        )}
      </form>

      {filter && (
        <div className="mb-4 text-sm bg-blue-50 text-primary rounded-lg px-4 py-2">
          Activite filtree sur &laquo; <strong>{filter}</strong> &raquo;
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <div className="flex items-start gap-6">
          {depute.photo_url && (
            <img
              src={depute.photo_url}
              alt={`${depute.prenom} ${depute.nom}`}
              className="w-32 h-32 rounded-lg object-cover"
            />
          )}
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-primary">
              {depute.prenom} {depute.nom}
            </h1>
            {depute.groupe_politique_id && (
              <span className="inline-block mt-2 text-sm font-medium px-3 py-1 rounded-full bg-accent/10 text-accent">
                {groupeNom || depute.groupe_politique_id}
              </span>
            )}

            {/* Indicators */}
            <div className="flex gap-6 mt-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {activite?.total_interventions ?? activite?.interventions?.length ?? 0}
                </p>
                <p className="text-xs text-gray-500">Interventions</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {votes?.total ?? activite?.total_votes ?? 0}
                </p>
                <p className="text-xs text-gray-500">Votes</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">
                  {activite?.total_amendements ?? activite?.amendements?.length ?? 0}
                </p>
                <p className="text-xs text-gray-500">Amendements</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {depute.departement && (
            <div>
              <p className="text-gray-400">Departement</p>
              <p className="font-medium">{depute.departement}</p>
            </div>
          )}
          {depute.circonscription && (
            <div>
              <p className="text-gray-400">Circonscription</p>
              <p className="font-medium">{depute.circonscription}</p>
            </div>
          )}
          {depute.date_naissance && (
            <div>
              <p className="text-gray-400">Naissance</p>
              <p className="font-medium">{depute.date_naissance}</p>
            </div>
          )}
          {depute.profession && (
            <div>
              <p className="text-gray-400">Profession</p>
              <p className="font-medium">{depute.profession}</p>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="flex border-b">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "text-primary border-b-2 border-primary bg-blue-50"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {tabLoading ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <>
              {/* Activite tab */}
              {activeTab === "activite" && activite && (
                <div>
                  <h3 className="font-semibold text-lg mb-4">
                    Dernieres interventions
                  </h3>
                  {activite.interventions?.length > 0 ? (
                    <ul className="space-y-4">
                      {activite.interventions.map((intervention, idx) => (
                        <li
                          key={idx}
                          className="border-l-4 border-blue-400 pl-4 py-2"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-xs text-gray-400">
                              {intervention.date} &mdash;{" "}
                              {intervention.type_seance || "Seance"}
                            </p>
                            {intervention.sentiment_label && (
                              <SentimentBadge
                                label={intervention.sentiment_label}
                                score={intervention.sentiment_score}
                              />
                            )}
                          </div>
                          <p className="text-sm text-gray-700 line-clamp-3">
                            {intervention.texte?.slice(0, 300)}
                            {intervention.texte?.length > 300 ? "..." : ""}
                          </p>
                          <AISummary
                            text={intervention.texte}
                            interventionId={intervention.id}
                            context={`Intervention de ${depute.prenom} ${depute.nom}`}
                          />
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-400 text-center py-6">
                      Aucune intervention enregistree
                    </p>
                  )}

                  {activite.amendements?.length > 0 && (
                    <>
                      <h3 className="font-semibold text-lg mt-8 mb-4">
                        Derniers amendements
                      </h3>
                      <ul className="space-y-3">
                        {activite.amendements.map((a, idx) => (
                          <li
                            key={idx}
                            className="border-l-4 border-purple-400 pl-4 py-2"
                          >
                            <p className="text-xs text-gray-400 mb-1">
                              {a.date} &mdash; {a.sort || "En cours"}
                            </p>
                            <p className="text-sm text-gray-700 line-clamp-2">
                              {a.objet || a.texte?.slice(0, 200)}
                            </p>
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              )}

              {/* Votes tab */}
              {activeTab === "votes" && votes && (
                <div>
                  <h3 className="font-semibold text-lg mb-4">
                    Historique des votes ({votes.total ?? 0})
                  </h3>
                  {votes.items?.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="text-left px-3 py-2">Date</th>
                            <th className="text-left px-3 py-2">Scrutin</th>
                            <th className="text-center px-3 py-2">Position</th>
                            <th className="text-center px-3 py-2">Resultat</th>
                          </tr>
                        </thead>
                        <tbody>
                          {votes.items.map((v, idx) => (
                            <tr key={idx} className="border-b">
                              <td className="px-3 py-2 text-gray-500">
                                {v.date}
                              </td>
                              <td className="px-3 py-2 max-w-xs truncate">
                                {v.titre}
                              </td>
                              <td className="px-3 py-2 text-center">
                                <span
                                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                    v.position === "pour"
                                      ? "bg-green-100 text-green-700"
                                      : v.position === "contre"
                                      ? "bg-red-100 text-red-700"
                                      : "bg-gray-100 text-gray-700"
                                  }`}
                                >
                                  {v.position}
                                </span>
                              </td>
                              <td className="px-3 py-2 text-center text-xs text-gray-500">
                                {v.nb_pour}P / {v.nb_contre}C / {v.nb_abstention}A
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-gray-400 text-center py-6">
                      Aucun vote enregistre
                    </p>
                  )}
                </div>
              )}

              {/* Questions tab */}
              {activeTab === "questions" && activite && (
                <div>
                  <h3 className="font-semibold text-lg mb-4">
                    Questions au gouvernement
                  </h3>
                  <p className="text-gray-400 text-center py-6">
                    Les questions seront affichees dans une prochaine mise a jour.
                  </p>
                </div>
              )}

              {/* Resume IA tab */}
              {activeTab === "resume" && (
                <div>
                  <h3 className="font-semibold text-lg mb-4">
                    Resumes par intelligence artificielle
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Cliquez sur &laquo; Generer le resume &raquo; pour obtenir un resume accessible de chaque intervention.
                  </p>
                  {activite?.interventions?.length > 0 ? (
                    <ul className="space-y-4">
                      {activite.interventions.map((intervention, idx) => (
                        <li
                          key={idx}
                          className="border-l-4 border-blue-400 pl-4 py-2"
                        >
                          <p className="text-xs text-gray-400 mb-1">
                            {intervention.date} &mdash;{" "}
                            {intervention.type_seance || "Seance"}
                          </p>
                          <p className="text-sm text-gray-700 line-clamp-2">
                            {intervention.texte?.slice(0, 200)}
                            {intervention.texte?.length > 200 ? "..." : ""}
                          </p>
                          <AISummary
                            text={intervention.texte}
                            interventionId={intervention.id}
                            context={`Intervention de ${depute.prenom} ${depute.nom}`}
                          />
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-400 text-center py-6">
                      Aucune intervention disponible pour generer un resume.
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default DeputePage;
