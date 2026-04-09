import { useState, useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import api from "../services/api";

const FRANCE_CENTER = [46.603354, 1.888334];
const FRANCE_ZOOM = 6;

// 6 color stops from light to dark blue
const COLORS = ["#D4E6F1", "#85C1E9", "#5DADE2", "#2E86C1", "#1B6CA8", "#154360"];
const NO_DATA_COLOR = "#F0F0F0";

function stripAccents(str) {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function buildDynamicScale(activityData) {
  const values = Object.values(activityData)
    .map((d) => d.nb_interventions || 0)
    .filter((v) => v > 0);

  if (values.length === 0) return [];

  const maxVal = Math.max(...values);
  const step = Math.max(1, Math.ceil(maxVal / COLORS.length));

  return COLORS.map((color, i) => ({
    min: i * step,
    max: i === COLORS.length - 1 ? Infinity : (i + 1) * step,
    color,
  }));
}

function getColor(value, scale) {
  if (!value || value === 0) return NO_DATA_COLOR;
  for (const level of scale) {
    if (value >= level.min && value < level.max) return level.color;
  }
  return COLORS[COLORS.length - 1];
}

function MapView({ onDepartmentClick, theme }) {
  const [geoData, setGeoData] = useState(null);
  const [activityData, setActivityData] = useState({});

  useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
    )
      .then((res) => res.json())
      .then(setGeoData)
      .catch(() => {
        // Fallback to local file if CDN fails
        fetch("/departements.geojson")
          .then((res) => res.json())
          .then(setGeoData)
          .catch(() => {});
      });
  }, []);

  useEffect(() => {
    const params = {};
    if (theme) params.theme = theme;

    api
      .get("/dashboard/geo", { params })
      .then((res) => {
        const map = {};
        (res.data || []).forEach((d) => {
          map[d.departement] = d;
        });
        setActivityData(map);
      })
      .catch(() => setActivityData({}));
  }, [theme]);

  if (!geoData) return null;

  const scale = buildDynamicScale(activityData);

  const style = (feature) => {
    const nom = stripAccents(feature.properties.nom || feature.properties.code || "");
    const info = activityData[nom] || {};
    const nb = info.nb_interventions || 0;

    return {
      fillColor: getColor(nb, scale),
      weight: 1,
      opacity: 1,
      color: "#fff",
      fillOpacity: 0.8,
    };
  };

  const onEachFeature = (feature, layer) => {
    const nomDisplay = feature.properties.nom || feature.properties.code || "";
    const nom = stripAccents(nomDisplay);
    const info = activityData[nom] || {};

    layer.bindTooltip(
      `<strong>${nomDisplay}</strong><br/>` +
        `${info.nb_deputes_actifs || 0} deputes actifs<br/>` +
        `${info.nb_interventions || 0} interventions`,
      { sticky: true }
    );

    layer.on({
      mouseover: (e) => {
        e.target.setStyle({ weight: 3, color: "#2E86C1", fillOpacity: 0.9 });
      },
      mouseout: (e) => {
        e.target.setStyle({ weight: 1, color: "#fff", fillOpacity: 0.75 });
      },
      click: () => {
        if (onDepartmentClick) onDepartmentClick(nom); // Send unaccented name to match backend
      },
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold text-primary mb-3">
        Carte de l'activite parlementaire
      </h3>
      <div className="rounded-lg overflow-hidden">
        <MapContainer
          center={FRANCE_CENTER}
          zoom={FRANCE_ZOOM}
          style={{ height: "500px", width: "100%" }}
          scrollWheelZoom={false}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          <GeoJSON
            key={JSON.stringify(activityData)}
            data={geoData}
            style={style}
            onEachFeature={onEachFeature}
          />
        </MapContainer>
      </div>
      <div className="flex items-center gap-2 mt-3 text-xs text-gray-500 flex-wrap">
        <span>Interventions :</span>
        <div className="flex items-center gap-1">
          <div className="w-4 h-3 rounded-sm" style={{ backgroundColor: NO_DATA_COLOR }} />
          <span>0</span>
        </div>
        {scale.map((level, i) => (
          <div key={i} className="flex items-center gap-1">
            <div
              className="w-4 h-3 rounded-sm"
              style={{ backgroundColor: level.color }}
            />
            <span>{level.min === 0 ? 1 : level.min}+</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MapView;
