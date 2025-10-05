import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';
import '../css/WorldPage.css';
import '../App.css';
import ventana from "../assets/pngs/ventana.png";

export default function WorldCountryPicker({ markers, setMarkers }) {
  const globeEl = useRef();
  const [hovered, setHovered] = useState(null);

  // initial camera position
  useEffect(() => {
    // optional: auto-rotate and set initial zoom
    const g = globeEl.current;
    if (g) {
      g.controls().autoRotate = true;
      g.controls().autoRotateSpeed = 0.4;
      g.pointOfView({ lat: 10, lng: 0, altitude: 2.4 }, 0);
    }
  }, []);

  // helper to add marker
  const addMarkerAt = (lat, lng) => {
    const id = Date.now();
    const label = 'Here';
    // siempre reemplaza el marcador anterior
    setMarkers([{ id, lat, lng, label }]);
  };

  // remove marker
  const removeMarker = (id) => setMarkers(m => m.filter(x => x.id !== id));

  return (
    <div className="app-root">
      <img className="ventana" src={ventana}></img>
      <div className="globe-wrap">
        <Globe
          ref={globeEl}
          globeImageUrl="https://unpkg.com/three-globe/example/img/earth-day.jpg"
          backgroundColor="rgba(0,0,0,0)"
          pointsData={markers}
          pointLat={(d) => d.lat}
          pointLng={(d) => d.lng}
          pointColor={() => '#ff0000ff'}
          pointAltitude={0.02}
          pointRadius={0.5}
          onGlobeClick={({ lat, lng }) => {
            addMarkerAt(lat, lng); // tu función para crear el marcador
            const g = globeEl.current;
            if (!g) return;
            g.controls().autoRotate = false;
            g.pointOfView({ lat, lng, altitude: 1.6 }, 1000); // 1000 ms de animación
          }}
          onPointHover={(p) => setHovered(p)}
          labelsData={markers}
          labelLat={d => d.lat}
          labelLng={d => d.lng}
          labelText={d => d.label}
          labelSize={2}
          labelDotRadius={0.6}
          labelColor={() => 'red'}
          labelResolution={2}
          width={0.2 * window.innerWidth}
          height={0.2 * window.innerWidth}
        />
      </div>
    </div>
  );
}
