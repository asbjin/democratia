import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";
import DeputePage from "./pages/DeputePage";
import GroupesPage from "./pages/GroupesPage";

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/depute/:id" element={<DeputePage />} />
          <Route path="/groupes" element={<GroupesPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
