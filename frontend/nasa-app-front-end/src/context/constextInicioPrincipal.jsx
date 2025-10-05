import { createContext, useContext, useState } from "react";

// contexto para el mapa de EPIU
// Context to manage the state of the map
// Tener en cuanta que si este se actualiza, se van a redenrizar todos los componentes que depende de este
const DatosQuiz = createContext();

// Proveedor del contexto del mapa de EPIU
// Ademas se definen las funciones para actualizar infovalue y selectionvalue
const DatosQuizProvider = ({ children }) => {

  // Tipo de la capa seleccionada
  const [datosQuiz, setDatosQuiz] = useState(null);

  const updateDatosQuiz = (datos) => {
    setDatosQuiz(datos);
  }

  return (
    <DatosQuiz.Provider
      value={{ datosQuiz, updateDatosQuiz }}
    >
      {children}
    </DatosQuiz.Provider>
  );
};

// Hook personalizado para consumir el contexto
export const useDatosQuizContext = () => {
  const context = useContext(DatosQuiz);
  if (!context) {
    throw new Error("useDatosQuizContext debe usarse dentro de un DatosQuizProvider");
  }
  return context;
};
export default DatosQuizProvider;