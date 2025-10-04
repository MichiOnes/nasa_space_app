import { useState, useEffect } from 'react'
import Overlay from "./components/Overlay";
import { Routes, Route, useLocation } from "react-router-dom";
import './App.css'

function App() {
  const [showOverlay, setShowOverlay] = useState(true); // Initially show overlay
  const location = useLocation();
  const closeOverlay = () => {
    setShowOverlay(false);
  };

  useEffect(() => {
    if (showOverlay) {
      const timer = setTimeout(() => {
        closeOverlay();
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [showOverlay]);

  const shouldShowOverlay = showOverlay && location.pathname === "/";

  return (
    <>
      {shouldShowOverlay && <Overlay/>}
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<></>} />
      </Routes>
    </>
  )
}

export default App
