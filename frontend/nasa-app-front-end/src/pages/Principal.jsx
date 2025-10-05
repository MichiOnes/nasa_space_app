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

import React, { useEffect, useState, useRef } from 'react';



function Principal() {

  const [tipo, setTipo] = useState("maiz");

  const [estado, setEstado] = useState(0);
  const [visible1, setVisible1] = useState(true);
  const [visible2, setVisible2] = useState(true);
  const [visible3, setVisible3] = useState(true);
  const [visible4, setVisible4] = useState(true);



  const [color, setColor] = useState("radial-gradient(ellipse 50% 30% at 50% 70%, var(--gris-oscuro), var(--negro))");
  
  const [respuestaCorrecta, setRespuestaCorrecta] = useState(1);
  const [acierto,setAcierto] = useState(false);

  let fases = []

  if (tipo == "tomate") {
    fases = [tomatesBuenos, tomatesMedios, tomatesPochos];
  } else if (tipo == "trigo") {
    fases = [trigoBueno, trigoMedio, trigoPocho];
  } else{
    fases = [maizBueno, maizMedio, maizPocho];
  }

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
              setEstado(2);
              setVisible1(true);
              setVisible2(true);
              setVisible3(true);
              setVisible4(true);
              setColor("radial-gradient(ellipse 50% 30% at 50% 70%, var(--gris-oscuro), var(--negro))")
            }, 3000);
          }, 400);
        }, 1000);
      }, 2000);
      }
      
    }, 1000);
  }


  const seleccionado1 = () => {
    setVisible2(false);
    setVisible3(false);
    setVisible4(false);

    if (respuestaCorrecta == 1){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio(1);
  }

  const seleccionado2 = () => {
    setVisible1(false);
    setVisible3(false);
    setVisible4(false);

    if (respuestaCorrecta == 2){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio(2);
  }

  const seleccionado3 = () => {
    setVisible2(false);
    setVisible1(false);
    setVisible4(false);

    if (respuestaCorrecta == 3){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio(3);
  }

  const seleccionado4 = () => {
    setVisible2(false);
    setVisible3(false);
    setVisible1(false);

    if (respuestaCorrecta == 4){
      setAcierto(true);
    } else {
      setAcierto(false);
    }

    animarCambio(4);
  }

  const volver = () => {
    setEstado(0);
    setCultivo(fases[0]);
  }
  
  if (estado == 0){
    return (
      <div className="principal">
        <img src={fondo} className='fondo'></img>
        <img src={cabraNormal} className='cabra Normal'></img>
        <img src={sueloCabra} className='suelo'></img>
        <div className='masterII'>
          <img src={bocadillo} className='bocadilloII'></img>
          <p className='textoII'>Hello, nice to meet you! I’m Croppy! <br />
            I will help you to optimise your crops!<br />
            Let’s personalize your terrain! Beee!</p>
          <div className='optionWrapper'>
            <button className='optionButton' style={{ visibility: visible1 ? 'visible' : 'hidden' }} onClick={seleccionado1}>Opción 1</button>
            <button className='optionButton' style={{ visibility: visible2 ? 'visible' : 'hidden' }} onClick={seleccionado2}>Opción 2</button>
            <button className='optionButton' style={{ visibility: visible3 ? 'visible' : 'hidden' }} onClick={seleccionado3}>Opción 3</button>
            <button className='optionButton' style={{ visibility: visible4 ? 'visible' : 'hidden' }} onClick={seleccionado4}>Opción 4</button>
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
          <p className='textoFail'>Hello, nice to meet you! I’m Croppy! <br />
            I will help you to optimise your crops!<br />
            Let’s personalize your terrain! Beee!</p>
          <button className='mainButtonFail' onClick={volver}>Next</button>
        </div>
      </div>
    )
  }
}
export default Principal;
