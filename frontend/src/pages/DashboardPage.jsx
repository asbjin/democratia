import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../services/api";
import DeputeCard from "../components/DeputeCard";
import SearchBar from "../components/SearchBar";
import StatCard from "../components/StatCard";
import ActivityChart from "../components/ActivityChart";
import TimelineChart from "../components/TimelineChart";
import VoteBreakdown from "../components/VoteBreakdown";
import MapView from "../components/MapView";

function DashboardPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [departement, setDepartement] = useState("");
  const [scrutins, setScrutins] = useState([]);
  const [groupes, setGroupes] = useState({});

  useEffect(() => {
    api
      .get("/groupes")
      .then((res) => {
        const map = {};
        (res.data.items || []).forEach((g) => { map[g.id] = g; });
        setGroupes(map);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const params = {};
    if (query) params.theme = query;
    if (departement) params.departement = departement;

    api
      .get("/dashboard", { params })
      .then((dashRes) => setData(dashRes.data))
      .catch(() => setError("Erreur lors du chargement des donnees"))
      .finally(() => setLoading(false));

    api
      .get("/scrutins", { params: { theme: query || undefined, size: 5 } })
      .then((scrutinRes) => setScrutins(scrutinRes.data.items || []))
      .catch(() => setScrutins([]));
  }, [query, departement]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg text-gray-500">Chargement des donnees...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <SearchBar />
        <div className="text-center mt-10">
          <p className="text-red-500 text-lg mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            Reessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <SearchBar />
      </div>

      {/* Department filter */}
      <div className="mb-6 flex items-center gap-4 flex-wrap">
        <label htmlFor="dept-filter" className="text-sm font-medium text-gray-700">
          Filtrer par departement :
        </label>
        <select
          id="dept-filter"
          value={departement}
          onChange={(e) => setDepartement(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-primary"
        >
          <option value="">Tous les departements</option>
          <option value="Paris">Paris</option>
          <option value="Bouches-du-Rhone">Bouches-du-Rhone</option>
          <option value="Nord">Nord</option>
          <option value="Rhone">Rhone</option>
          <option value="Gironde">Gironde</option>
          <option value="Hauts-de-Seine">Hauts-de-Seine</option>
          <option value="Seine-Saint-Denis">Seine-Saint-Denis</option>
          <option value="Val-de-Marne">Val-de-Marne</option>
          <option value="Yvelines">Yvelines</option>
          <option value="Essonne">Essonne</option>
        </select>
        {departement && (
          <button
            onClick={() => setDepartement("")}
            className="flex items-center gap-1 px-3 py-1.5 bg-accent text-white text-sm rounded-full hover:bg-primary transition-colors"
          >
            {departement}
            <span className="ml-1 font-bold">&times;</span>
          </button>
        )}
      </div>

      {query && (
        <h2 className="text-2xl font-bold text-primary mb-6">
          Resultats pour : &laquo; {query} &raquo;
        </h2>
      )}

      {/* Stats Cards */}
      {data?.stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <StatCard
            label="Deputes actifs"
            value={data.stats.nb_deputes.toLocaleString("fr-FR")}
            subtext="dans la legislature en cours"
            color="text-blue-600"
          />
          <StatCard
            label="Interventions"
            value={data.stats.nb_interventions.toLocaleString("fr-FR")}
            subtext="en seance publique"
            color="text-green-600"
          />
          <StatCard
            label="Scrutins"
            value={data.stats.nb_scrutins.toLocaleString("fr-FR")}
            subtext="votes enregistres"
            color="text-purple-600"
          />
        </div>
      )}

      {/* Map + Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <MapView
          onDepartmentClick={(dept) => setDepartement(dept)}
          theme={query || undefined}
          departement={departement || undefined}
        />
        {data?.par_groupe?.length > 0 && <ActivityChart data={data.par_groupe} />}
      </div>

      {/* Timeline */}
      <div className="grid grid-cols-1 gap-6 mb-10">
        {data?.timeline?.length > 0 && <TimelineChart data={data.timeline} />}
      </div>

      {/* Top deputes */}
      {data?.top_deputes?.length > 0 && (
        <section className="mb-10">
          <h3 className="text-xl font-semibold text-primary mb-4">
            {query
              ? `Deputes les plus actifs sur « ${query} »`
              : "Top 10 deputes les plus actifs"}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.top_deputes.map((d) => (
              <DeputeCard
                key={d.id}
                depute={d}
                groupes={groupes}
                countLabel={query ? "interventions sur ce theme" : "interventions"}
              />
            ))}
          </div>
        </section>
      )}

      {/* Vote breakdowns */}
      {scrutins.length > 0 && (
        <section className="mb-10">
          <h3 className="text-xl font-semibold text-primary mb-4">
            Derniers scrutins
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scrutins.map((s) => (
              <VoteBreakdown key={s.id} scrutin={s} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default DashboardPage;
