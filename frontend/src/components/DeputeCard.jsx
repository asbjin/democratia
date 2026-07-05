import { Link } from "react-router-dom";

function DeputeCard({ depute, groupes, countLabel = "interventions" }) {
  const groupe = groupes?.[depute.groupe_politique_id];
  const groupeLabel = groupe?.sigle || groupe?.nom || depute.groupe_politique_id;

  return (
    <Link
      to={`/depute/${depute.id}`}
      className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-5"
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-primary">
          {depute.prenom} {depute.nom}
        </h3>
        {depute.groupe_politique_id && (
          <span className="text-xs font-medium px-2 py-1 rounded-full bg-accent/10 text-accent">
            {groupeLabel}
          </span>
        )}
      </div>
      {depute.departement && (
        <p className="text-sm text-gray-500">{depute.departement}</p>
      )}
      {depute.nb_interventions !== undefined && (
        <p className="text-sm text-gray-600 mt-2">
          <span className="font-medium">{depute.nb_interventions}</span>{" "}
          {countLabel}
        </p>
      )}
    </Link>
  );
}

export default DeputeCard;
