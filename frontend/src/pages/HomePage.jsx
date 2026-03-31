import SearchBar from "../components/SearchBar";

function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4">
      <h1 className="text-5xl font-bold text-primary mb-4">DemocratIA</h1>
      <p className="text-xl text-gray-600 mb-10 text-center max-w-2xl">
        Suivez l'activite de vos deputes. Explorez les votes, interventions et
        amendements de l'Assemblee Nationale.
      </p>
      <SearchBar />
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl w-full">
        <div className="text-center p-6">
          <div className="text-3xl mb-3">🏛️</div>
          <h3 className="font-semibold text-primary mb-2">Transparence</h3>
          <p className="text-sm text-gray-500">
            Acces direct aux donnees officielles de l'Assemblee Nationale
          </p>
        </div>
        <div className="text-center p-6">
          <div className="text-3xl mb-3">📊</div>
          <h3 className="font-semibold text-primary mb-2">Visualisation</h3>
          <p className="text-sm text-gray-500">
            Graphiques et tableaux de bord pour comprendre l'activite
            parlementaire
          </p>
        </div>
        <div className="text-center p-6">
          <div className="text-3xl mb-3">🤖</div>
          <h3 className="font-semibold text-primary mb-2">
            Intelligence Artificielle
          </h3>
          <p className="text-sm text-gray-500">
            Resumes et analyses generes par IA pour une lecture accessible
          </p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
