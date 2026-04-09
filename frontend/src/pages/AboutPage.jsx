function AboutPage() {
  const team = [
    { nom: "Tebti Mohamed Anis", role: "IA / Tech Lead", desc: "Architecture IA, prompts, analyse de sentiment, extraction de themes" },
    { nom: "Rais Walid", role: "Backend", desc: "API FastAPI, endpoints REST, cache, rate limiting, vues materialisees" },
    { nom: "Aiche Youva", role: "Data / ETL", desc: "Pipeline de donnees, parsing Open Data AN, fixtures, photos deputes" },
    { nom: "Ceran Mohamed", role: "Frontend", desc: "Interface React, graphiques Recharts, carte Leaflet, dark mode" },
    { nom: "Chabla Yassine", role: "DevOps", desc: "Docker, CI/CD, Nginx, monitoring, tests, documentation" },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-4">A propos de DemocratIA</h1>

      <section className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-primary mb-3">Le projet</h2>
        <p className="text-gray-600 leading-relaxed mb-4">
          DemocratIA est un tableau de bord citoyen qui rend l'activite parlementaire
          francaise accessible a tous. En exploitant les donnees ouvertes de l'Assemblee
          Nationale, la plateforme permet de suivre les interventions, votes et amendements
          des deputes de la XVIIe legislature.
        </p>
        <p className="text-gray-600 leading-relaxed mb-4">
          Un module d'intelligence artificielle genere des resumes accessibles des textes
          parlementaires et analyse le sentiment des debats, rendant les discussions
          legislatives comprehensibles pour chaque citoyen.
        </p>
        <p className="text-gray-600 leading-relaxed">
          Ce projet a ete realise dans le cadre d'un projet universitaire en 2025.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold text-primary mb-4">L'equipe</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {team.map((member) => (
            <div
              key={member.nom}
              className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow"
            >
              <h3 className="font-semibold text-primary">{member.nom}</h3>
              <p className="text-sm text-accent font-medium mt-1">{member.role}</p>
              <p className="text-xs text-gray-500 mt-2">{member.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-primary mb-3">Ressources</h2>
        <ul className="space-y-2 text-sm">
          <li>
            <span className="text-gray-500">Donnees source : </span>
            <a
              href="https://data.assemblee-nationale.fr/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline"
            >
              Open Data Assemblee Nationale
            </a>
          </li>
          <li>
            <span className="text-gray-500">Code source : </span>
            <a
              href="https://github.com/asbjin/democratia"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline"
            >
              github.com/asbjin/democratia
            </a>
          </li>
          <li>
            <span className="text-gray-500">Stack : </span>
            <span className="text-gray-600">
              React 18, FastAPI, PostgreSQL 16, Docker, Tailwind CSS
            </span>
          </li>
        </ul>
      </section>
    </div>
  );
}

export default AboutPage;
