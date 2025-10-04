import React from 'react';
import { Box } from "@mui/material";
import LogoMyFarm from "../assets/LogoMyFarm.png";

function Overlay() {
  return (
    <Box
      sx={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: 'radial-gradient(circle, var(--verde-claro), var(--verde-oscuro))',
        zIndex: 9999,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <img
        src={LogoMyFarm}
        alt="Imagen logo"
        style={{
          maxWidth: "60vw",
          maxHeight: "60vh",
          width: "100%",
          height: "auto",
        }}
      />
    </Box>
  );
}

export default Overlay;