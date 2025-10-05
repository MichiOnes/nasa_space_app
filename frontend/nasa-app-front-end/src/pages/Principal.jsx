import '../App.css';
import fondo from "../assets/pngs/fondo.png";
import cabraNormal from "../assets/pngs/CabraNormal.png";
import cabraTriste from "../assets/pngs/CabraTriste.png";
import cabraNasa from "../assets/pngs/CabraNasa.png";
import tomatesBuenos from "../assets/pngs/tomatesBuenos.png";
import tomatesMedios from "../assets/pngs/tomatesMedios.png";
import tomatesPochos from "../assets/pngs/tomatesPochos.png";
import maizBueno from "../assets/pngs/maizPerfecto.png";
import maizMedio from "../assets/pngs/maizMedio.png";
import maizPocho from "../assets/pngs/maizPocho.png";
import trigoBueno from "../assets/pngs/trigoBueno.png";
import trigoMedio from "../assets/pngs/trigoMedio.png";
import trigoPocho from "../assets/pngs/trigoPocho.png";
import grid from "../assets/pngs/grid.jpg";

import bocadillo from "../assets/svgs/bocadilloIII.svg";
import bocadilloGrande from "../assets/svgs/bocadilloGrandeII.svg";
import sueloCabra from "../assets/svgs/sueloCabra.svg";

import React, { useEffect, useState} from 'react';

import { useNavigate } from "react-router-dom";

import { useDatosQuizContext } from "../context/constextInicioPrincipal.jsx";

import axios from 'axios';
import { DIRECTION } from '../constants/constants'
const API_URL = `${DIRECTION}/api`;

function Principal() {

  let plot_base64;

  const { datosQuiz, updateDatosQuiz } = useDatosQuizContext();
  const navigate = useNavigate();

  let respuestaSelec;
  
  const [respuestaFeedback, setRespuestaFeedback] = useState(null)

  const [tipo, setTipo] = useState(datosQuiz ? datosQuiz.tipo : null);

  const [tamano, setTamano] = useState(datosQuiz ? datosQuiz.tamano : null);

  const [plotSrc, setPlotSrc] = useState(null);

  let fases = []
  let tipo_ingles = ""
  let tamno_granja_ingles = ""

  if (tipo == "tomate") {
    fases = [tomatesBuenos, tomatesMedios, tomatesPochos];
    tipo_ingles = "Tomato"
  } else if (tipo == "trigo") {
    fases = [trigoBueno, trigoMedio, trigoPocho];
    tipo_ingles = "Wheat"
  } else{
    fases = [maizBueno, maizMedio, maizPocho];
    tipo_ingles = "Corn"
  }

  if (tamano == "pequeño") {
    tamno_granja_ingles = "Small-Scale / Household"
  } else {
    tamno_granja_ingles = "Industrial Scale"
  }
  const preguntasFiltradas = datosQuiz
    ? datosQuiz.quiz.filter(
        (q) =>
          q.category.includes(tipo_ingles) &&
          q.category.includes(tamno_granja_ingles) &&
          tipo_ingles &&
          tamno_granja_ingles
      )
      .slice(0,2)
    : null;

  console.log("Preguntas filtradas por tipo y tamaño:", preguntasFiltradas);

  const [preguntas, setPreguntas] = useState(preguntasFiltradas);

  const [numeroPregunta, setNumeroPregunta] = useState(0);

  const [respuestaCorrecta, setRespuestaCorrecta] = useState(datosQuiz ? preguntas[numeroPregunta].answer : null);

  const [utlimaPreguntaIncorrecta, setUtlimaPreguntaIncorrecta] = useState(false);

  const aumentarPregunta = () => {
    if (numeroPregunta < preguntas.length - 1) {
      setNumeroPregunta(numeroPregunta + 1);
      setRespuestaCorrecta(preguntas ? preguntas[numeroPregunta + 1].answer : null);
    }
    else{
        setEstado(4)
    }
      // Por ejemplo, podrías reiniciar el cuestionario o mostrar un mensaje de finalización
      // setNumeroPregunta(0); // Reinicia al principio
      // setRespuestaCorrecta(preguntas ? preguntas[0].answer : null);
  };

  const [numRespuestaCorrectas, setNumRespuestaCorrectas] = useState(0)
  const [numRespuestaIncorrectas, setNumRespuestaIncorrectas] = useState(0)

  const [estado, setEstado] = useState(0);
  const [visible1, setVisible1] = useState(true);
  const [visible2, setVisible2] = useState(true);
  const [visible3, setVisible3] = useState(true);
  const [visible4, setVisible4] = useState(true);

  const [color, setColor] = useState("radial-gradient(ellipse 50% 30% at 50% 70%, var(--gris-oscuro), var(--negro))");

  const [acierto, setAcierto] = useState(false);

   // Redirige a "/" si no hay datosQuiz (por ejemplo, al recargar)
  useEffect(() => {
    if (!datosQuiz) {
      navigate("/", { replace: true });
    }
  }, [datosQuiz, navigate]);

  const [cultivo, setCultivo] = useState(fases[0]);

  const animarCambio = (a) => {
    
    const timer = setTimeout(() => {
      setEstado(1);

      if (a == respuestaCorrecta){
        const timer = setTimeout(() => {
          setColor("radial-gradient(ellipse 50% 30% at 50% 70%, #CBFF79 , #235800)")
          const timer = setTimeout(() => {
            setEstado(0);
            setVisible1(true);
            setVisible2(true);
            setVisible3(true);
            setVisible4(true);
            setColor("radial-gradient(ellipse 50% 30% at 50% 70%, var(--gris-oscuro), var(--negro))")
            setNumRespuestaCorrectas(numRespuestaCorrectas + 1);
            aumentarPregunta();
          }, 3000);
        }, 2000);
      } else{
        const timer = setTimeout(() => {
        setColor("radial-gradient(ellipse 50% 30% at 50% 70%, #FF7979, #580000)")
        const timer = setTimeout(() => {
          setCultivo(fases[1]);
          const timer = setTimeout(() => {
            setCultivo(fases[2]);
            const timer = setTimeout(() => {
              respuesta_incorrecta();
              setEstado(2)
              setVisible1(true);
              setVisible2(true);
              setVisible3(true);
              setVisible4(true);
              setColor("radial-gradient(ellipse 50% 30% at 50% 70%, var(--gris-oscuro), var(--negro))")
              setNumRespuestaIncorrectas(numRespuestaIncorrectas + 1);
              if (numeroPregunta < preguntas.length - 1) {
                aumentarPregunta();
              } else{
                setUtlimaPreguntaIncorrecta(true)
              }
            }, 3000);
          }, 400);
        }, 1000);
      }, 2000);
      }
    }, 1000);
  }

  const seleccionado1 = () => {
    respuestaSelec = "A"
    setVisible2(false);
    setVisible3(false);
    setVisible4(false);

    if (respuestaCorrecta == "A"){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio("A");
  }

  const seleccionado2 = () => {
    respuestaSelec = "B"
    setVisible1(false);
    setVisible3(false);
    setVisible4(false);

    if (respuestaCorrecta == "B"){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio("B");
  }

  const seleccionado3 = () => {
    respuestaSelec = "C"
    setVisible2(false);
    setVisible1(false);
    setVisible4(false);

    if (respuestaCorrecta == "C"){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio("C");
  }

  const seleccionado4 = () => {
    respuestaSelec = "D"
    setVisible2(false);
    setVisible3(false);
    setVisible1(false);

    if (respuestaCorrecta == "D"){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio("D");
  }

  const volver = () => {
    setEstado(0);
    setCultivo(fases[0]);
    if (utlimaPreguntaIncorrecta){
        setEstado(4);
    }
  }

  const volver_a_inicio = () => {
    navigate("/", { replace: true });
  }

  const irAPlot = () => {
    setEstado(3);
  }
  
  const respuesta_incorrecta = async () => {
    
    const datos = {
      user_input: {
        category: `${tipo_ingles} – ${tamno_granja_ingles}`,
        qid: preguntas[numeroPregunta].qid,
        text: preguntas[numeroPregunta].text,
        options: preguntas[numeroPregunta].options,
        selected_answer: respuestaSelec,
        correct_answer: respuestaCorrecta,
        fb: preguntas[numeroPregunta].fb,
        latitude: datosQuiz.lat,
        longitude: datosQuiz.lon
      }
    };

    try {
      const response = await axios.post(`${API_URL}/feedback`, datos);
      console.log('Datos enviados al clima:', datos);
      console.log('Respuesta del clima:', response.data);
      setRespuestaFeedback(response.data)

      // Si tu backend devuelve { plot_base64, format }, usa el formato; si no, asume PNG
      plot_base64 = response.data.plot_base64;

      // Construye el src para <img>
      if (plot_base64) {
        setPlotSrc(`data:/image/png;base64,${plot_base64}`);
      } else {
        setPlotSrc(null);
      }

      console.log("Estado plotSrc", plotSrc)

    } catch (error) {
        console.error('Error al enviar los datos:', error);
    }
  }
  
  if (estado == 0){
    return (
      <div className="principal">
        <img src={fondo} className='fondo'></img>
        <img src={cabraNormal} className='cabra Normal'></img>
        <img src={sueloCabra} className='suelo'></img>
        <div className='masterII'>
          <img src={bocadillo} className='bocadilloII'></img>
          <p className='textoII'>{preguntas ? preguntas[numeroPregunta].text : "Loading..."}</p>
          <div className='optionWrapper'>
            <button className='optionButton' style={{ visibility: visible1 ? 'visible' : 'hidden' }} onClick={seleccionado1}>{preguntas ? preguntas[numeroPregunta].options.A : "Loading..."}</button>
            <button className='optionButton' style={{ visibility: visible2 ? 'visible' : 'hidden' }} onClick={seleccionado2}>{preguntas ? preguntas[numeroPregunta].options.B : "Loading..."}</button>
            <button className='optionButton' style={{ visibility: visible3 ? 'visible' : 'hidden' }} onClick={seleccionado3}>{preguntas ? preguntas[numeroPregunta].options.C : "Loading..."}</button>
            <button className='optionButton' style={{ visibility: visible4 ? 'visible' : 'hidden' }} onClick={seleccionado4}>{preguntas ? preguntas[numeroPregunta].options.D : "Loading..."}</button>
          </div>
          <img src={cultivo} className='cultivo'></img>
        </div>
      </div>
    );
    }
  if (estado == 1){
    return (
      <div className="drama" style = {{background: color}}>
        <img src={cultivo} className='cultivoGrande'></img>
      </div>
    )
  }
  if (estado == 2){
    return (
      <div className="inicio">
        <img src={grid} className='grid'></img>
        <img src={cabraTriste} className='cabra Triste'></img>
        <div className='masterFail'>
          <img src={bocadilloGrande} className='bocadilloFail'></img>
          <p className='textoFail'>
            {respuestaFeedback && Array.isArray(respuestaFeedback.message)
              ? respuestaFeedback.message.map((linea, idx) => (
                  <React.Fragment key={idx}>
                    {linea}
                    <br />
                  </React.Fragment>
                ))
              : (respuestaFeedback ? respuestaFeedback.message : "Loading...")}
          </p>
          <button className='mainButtonFail' onClick={irAPlot}>Next</button>
        </div>
      </div>
    )
  }
  if (estado == 3){
  return (
    <div className="inicio">
      <img src={grid} className='grid' />
      <img src={cabraTriste} className='cabra Triste' />
      <div className='masterFail_2'>
        <img src={bocadilloGrande} className='bocadilloFail_2' />
        {plotSrc ? (
          <div>
            <img
              src={plotSrc}
              alt="Gráfico generado"
              className='grafico'
            />
            <div className='buttonWrapper_Fail'>
            <button className="secondButton_failIII"
              onClick={() => {
                if (!plotSrc) return;
                const link = document.createElement('a');
                link.href = plotSrc;           // data URL o blob URL
                link.download = 'grafico.png';
                document.body.appendChild(link);
                link.click();
                link.remove();
            }}
            > 
              Download Plot
            </button>
            <button className='mainButton_failIII' onClick={volver}>Next</button>
            </div>
          </div>
        ) : (
          <p className='textoFail_2'>Generando gráfico…</p>
        )}
      </div>
    </div>
    )
  }
  if (estado == 4){
    return (
      <div className="principal">
        <img src={fondo} className='fondo'></img>
        <img src={cabraNormal} className='cabra Normal'></img>
        <img src={sueloCabra} className='suelo'></img>
        <div className='masterII'>
          <img src={bocadillo} className='bocadilloII'></img>
          <p className='textoII'>Great job! <br />
            Feel free to play again!<br />
            Thank you!</p>
          <div className='optionWrapper'>
            <p className='textoFinal'>
              You answered right {numRespuestaCorrectas} out of {preguntasFiltradas.length} questions! <br />
              You answered wrong {numRespuestaIncorrectas} out of {preguntasFiltradas.length} questions! <br />
            </p>
          </div>
          <button className='mainButtonFinal' onClick={volver_a_inicio}>Go To Inicial Page</button>
          <img src={cultivo} className='cultivo'></img>
        </div>
      </div>
    );
    }
}
export default Principal;
