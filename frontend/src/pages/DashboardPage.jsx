import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../services/api";
import DeputeCard from "../components/DeputeCard";
import SearchBar from "../components/SearchBar";

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 text-center">
      <p className="text-3xl font-bold text-accent">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function DashboardPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const params = {};
    if (query) params.theme = query;

    api
      .get("/dashboard", { params })
      .then((res) => setData(res.data))
      .catch((err) => setError("Erreur lors du chargement des donnees"))
      .finally(() => setLoading(false));
  }, [query]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <p className="text-lg text-gray-500">Chargement...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <SearchBar />
        <p className="text-center text-red-500 mt-10">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <SearchBar />
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
          />
          <StatCard
            label="Interventions"
            value={data.stats.nb_interventions.toLocaleString("fr-FR")}
          />
          <StatCard
            label="Scrutins"
            value={data.stats.nb_scrutins.toLocaleString("fr-FR")}
          />
        </div>
      )}

      {/* Top deputes */}
      {data?.top_deputes?.length > 0 && (
        <section className="mb-10">
          <h3 className="text-xl font-semibold text-primary mb-4">
            Top 10 deputes les plus actifs
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.top_deputes.map((d) => (
              <DeputeCard key={d.id} depute={d} />
            ))}
          </div>
        </section>
      )}

      {/* Par groupe - BarChart */}
      {data?.par_groupe?.length > 0 && (
        <section className="mb-10">
          <h3 className="text-xl font-semibold text-primary mb-4">
            Deputes par groupe politique
          </h3>
          <div className="bg-white rounded-lg shadow p-6">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={data.par_groupe}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="groupe" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#2E75B6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {/* Timeline - AreaChart */}
      {data?.timeline?.length > 0 && (
        <section className="mb-10">
          <h3 className="text-xl font-semibold text-primary mb-4">
            Interventions par mois
          </h3>
          <div className="bg-white rounded-lg shadow p-6">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.timeline}>
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
        </section>
      )}
    </div>
  );
}

export default DashboardPage;
