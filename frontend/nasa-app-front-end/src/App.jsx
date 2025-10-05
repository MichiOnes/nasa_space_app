import { useState, useEffect } from 'react'
import Overlay from "./components/Overlay";
import { Routes, Route, useLocation } from "react-router-dom";
import Principal from "./pages/Principal.jsx";
import Inicio from './pages/Inicio.jsx';

import './App.css'

function App() {
  const [showOverlay, setShowOverlay] = useState(true); // Initially show overlay
  const location = useLocation();
  const closeOverlay = () => {
    setShowOverlay(false);
  };

  const [esHorizontal, setEsHorizontal] = useState(window.innerWidth > window.innerHeight);

  useEffect(() => {
    const handleResize = () => {
      setEsHorizontal(window.innerWidth > window.innerHeight);
    };

    window.addEventListener("resize", handleResize);
    window.addEventListener("orientationchange", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("orientationchange", handleResize);
    };
  }, []);

  useEffect(() => {
    if (showOverlay) {
      const timer = setTimeout(() => {
        closeOverlay();
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [showOverlay]);

  if (!esHorizontal) {
    return (
      <div
        style={{
          height: "100vh",
          width: "100vw",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#111",
          color: "white",
          fontSize: "1.5rem",
          textAlign: "center",
          padding: "1rem",
        }}
      >
        🔄 Gira tu dispositivo para usar la app en orientación horizontal.
      </div>
    );
  }
  
  const shouldShowOverlay = showOverlay && location.pathname === "/";

  return (
    <>
      {shouldShowOverlay && <Overlay/>}
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Inicio />} />
        <Route path="/Principal" element={<Principal />} />
      </Routes>
    </>
  )
}

export default App
