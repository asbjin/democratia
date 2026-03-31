import { useState } from "react";
import { useNavigate } from "react-router-dom";

function SearchBar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/dashboard?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-xl mx-auto">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Rechercher un sujet, un depute, un theme..."
        className="flex-1 px-4 py-3 rounded-l-lg border-2 border-r-0 border-accent focus:outline-none focus:border-primary text-gray-700"
      />
      <button
        type="submit"
        className="px-6 py-3 bg-accent text-white font-semibold rounded-r-lg hover:bg-primary transition-colors"
      >
        Rechercher
      </button>
    </form>
  );
}

export default SearchBar;
