import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="bg-primary text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold tracking-tight">
            DemocratIA
          </Link>
          <div className="flex space-x-6">
            <Link
              to="/"
              className="hover:text-blue-200 transition-colors font-medium"
            >
              Accueil
            </Link>
            <Link
              to="/dashboard"
              className="hover:text-blue-200 transition-colors font-medium"
            >
              Dashboard
            </Link>
            <Link
              to="/groupes"
              className="hover:text-blue-200 transition-colors font-medium"
            >
              Groupes
            </Link>
            <a
              href="#about"
              className="hover:text-blue-200 transition-colors font-medium"
            >
              A propos
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
