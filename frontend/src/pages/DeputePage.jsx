import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";

function DeputePage() {
  const { id } = useParams();
  const [depute, setDepute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/deputes/${id}`)
      .then((res) => setDepute(res.data))
      .catch(() => setError("Depute non trouve"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <p className="text-lg text-gray-500">Chargement...</p>
      </div>
    );
  }

  if (error || !depute) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 text-center">
        <p className="text-red-500 text-lg">{error || "Depute non trouve"}</p>
        <Link to="/dashboard" className="text-accent underline mt-4 block">
          Retour au dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        to="/dashboard"
        className="text-accent hover:underline text-sm mb-6 block"
      >
        &larr; Retour au dashboard
      </Link>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-start gap-6">
          {depute.photo_url && (
            <img
              src={depute.photo_url}
              alt={`${depute.prenom} ${depute.nom}`}
              className="w-32 h-32 rounded-lg object-cover"
            />
          )}
          <div>
            <h1 className="text-3xl font-bold text-primary">
              {depute.prenom} {depute.nom}
            </h1>
            {depute.groupe_politique_id && (
              <span className="inline-block mt-2 text-sm font-medium px-3 py-1 rounded-full bg-accent/10 text-accent">
                {depute.groupe_politique_id}
              </span>
            )}
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          {depute.departement && (
            <div>
              <p className="text-sm text-gray-400">Departement</p>
              <p className="font-medium">{depute.departement}</p>
            </div>
          )}
          {depute.circonscription && (
            <div>
              <p className="text-sm text-gray-400">Circonscription</p>
              <p className="font-medium">{depute.circonscription}</p>
            </div>
          )}
          {depute.date_naissance && (
            <div>
              <p className="text-sm text-gray-400">Date de naissance</p>
              <p className="font-medium">{depute.date_naissance}</p>
            </div>
          )}
          {depute.profession && (
            <div>
              <p className="text-sm text-gray-400">Profession</p>
              <p className="font-medium">{depute.profession}</p>
            </div>
          )}
          {depute.sexe && (
            <div>
              <p className="text-sm text-gray-400">Civilite</p>
              <p className="font-medium">{depute.sexe}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DeputePage;
