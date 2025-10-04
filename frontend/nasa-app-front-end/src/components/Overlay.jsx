// Componente que se muestra al cargar la página, con información sobre la aplicación y la empresa

import React from 'react';
import { Button, Typography, Box } from "@mui/material";
import LogoMyFarm from "../assets/LogoMyFarm.png";

function Overlay() {
  return (
    <Box
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        background: 'radial-gradient(circle, var(--verde-claro), var(--verde-oscuro))',
        zIndex: 9999,
      }}
    >
      <Box 
        display={"flex"} 
        justifyContent={"center"}
        height={"85%"}
        width={"100%"}
      >
        <Box
          display={"flex"}
          alignItems={"center"}
          justifyContent={"space-between"}
          paddingTop={"1.5rem"}
        >
          <img
            src={LogoMyFarm}
            alt="Imagen logo"
            style={{
              display: "block",
              margin: "0 auto",
              maxWidth: "45vw", // que no se pase del ancho de la pantalla
            }}
          />
        </Box>
      </Box>
      <Box
        position={"absolute"}
        bottom={0}
        left={0}
        height={"7rem"}
        width={"100%"}
        display={"flex"}
        flexDirection={"column"}
        alignItems={"flex-start"}
        justifyContent={"flex-end"}
        padding={"1rem"}
      >
      </Box>
    </Box>
  );
}

export default Overlay;
