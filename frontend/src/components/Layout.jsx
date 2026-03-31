import Navbar from "./Navbar";

function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">{children}</main>
      <footer className="bg-primary text-white text-center py-4 text-sm">
        <p>DemocratIA &mdash; Donnees ouvertes de l'Assemblee Nationale</p>
        <p className="text-blue-200 mt-1">Projet universitaire 2025</p>
      </footer>
    </div>
  );
}

export default Layout;
