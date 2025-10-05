import '../App.css';
import grid from "../assets/pngs/grid.jpg";
import cabraNasa from "../assets/pngs/CabraNasa.png";
import bocadilloGrande from "../assets/svgs/bocadilloGrande.svg";
import bocadillo from "../assets/svgs/bocadillo.svg";
import React, { useEffect, useState, useRef} from 'react';
import WorldCountryPicker from "./WorldPage.jsx";
import axios from 'axios';
import { DIRECTION } from '../constants/constants'
import { useDatosQuizContext } from "../context/constextInicioPrincipal.jsx";
import { useNavigate } from "react-router-dom";

const API_URL = `${DIRECTION}/api`;

const ANTARTIC_CUT_OFF = -60

function Inicio() {

  const navigate = useNavigate();

  const [estado, setEstado] = useState(0);
  const [tamaño, setTamaño] = useState("pequeño");
  const [tipo, setTipo] = useState("tomate");

  const [markers, setMarkers] = useState([]); // { id, lat, lng, label }

  const { datosQuiz, updateDatosQuiz } = useDatosQuizContext();

  useEffect(() => {
  if (datosQuiz) {
    console.log('Respuesta en el contexto (actualizada):', datosQuiz);
  }
}, [datosQuiz]);

  let response_climate = null;
  let response_quiz = null;

  const primero = () => {
    setEstado(1);
  }

  const segundo = () => {
    if (markers.length == 0) {
      alert("Please, select a location on the globe!");
      return;
    }
    setEstado(2);
  }

  const pequeño = () => {
    setTamaño("pequeño")
    setEstado(3);
  }

  const grande = () => {
    setTamaño("grande")
    setEstado(3);
  }

  const tomate = () => {
    setTipo("tomate")
    setEstado(4);
  }

  const maiz = () => {
    setTipo("maiz")
    setEstado(4);
  }

  const trigo = () => {
    setTipo("trigo")
    setEstado(4);
  }

  const atrás = () => {
    setEstado(estado-1);
  }

  const enviarDatos = async () => {
    if (markers.length == 0) {
      alert("Please, select a location on the globe!");
      return;
    }
    const datos = {
      lat: markers[0].lat,
      lon: markers[0].lng,
      tamano: tamaño,
      tipo: tipo
    };

    if (datos.lat < ANTARTIC_CUT_OFF){
        alert("The selected location is in the Antartic region. Please, select a different location.");
        setEstado(1);
        return;
    }

    try {
      const response = await axios.post(`${API_URL}/climate`, datos);
      console.log('Datos enviados al clima:', datos);
      response_climate = response.data;
      console.log('Respuesta del clima:', response_climate);
      // Aquí puedes manejar la respuesta del servidor si es necesario
      if (response_climate.climate == "Ocean") {
        alert("The selected location has an oceanic climate. Please, select a different location.");
        setEstado(1);
        return;
      }
      if (response_climate.climate == "Frozen water"){
        alert("The selected location is a mass of Fronzen Water. Please, select a different location.");
        setEstado(1);
        return;
      }
    } catch (error) {
        console.error('Error al enviar los datos:', error);
    }

    const datos_quiz = {...datos};
    datos_quiz.category = response_climate.climate;
    datos_quiz.num_options = 4;

    try {
      const response = await axios.post(`${API_URL}/quiz`, datos_quiz);
      console.log('Datos enviados a la quiz:', datos_quiz);
      response_quiz = response.data;
      response_quiz.tipo = tipo;
      response_quiz.climate = response_climate.climate;
      response_quiz.tamano = datos.tamano;
      updateDatosQuiz(response_quiz);
      console.log('Respuesta del quiz con tipo y clima añadido por nosotros:', response_quiz);
      navigate("/principal"); // redirige a la página del globo
    } catch (error) {
        console.error('Error al enviar los datos:', error);
    }
  }

  if (estado == 0) {
        return (
          <div className="inicio">
            <img src={grid} className='grid'></img>
            <img src={cabraNasa} className='cabra Nasa'></img>
            <div className='master'>
              <img src={bocadillo} className='bocadillo'></img>
              <p className='texto'>Hello, nice to meet you! I’m Croppy! <br />
                I will help you to optimise your crops!<br />
                Let’s personalize your terrain! Beee!</p>
              <button className='mainButton' onClick={primero}>LET'S GO!</button>
            </div>
          </div>
        );
      }
    if (estado == 1) {
        return (
          <div className="inicio">
            <img src={grid} className='grid'></img>
            <img src={cabraNasa} className='cabra Nasa'></img>
            <div className='masterIII'>
              <img src={bocadilloGrande} className='bocadilloGrande'></img>
              <p className='textoIII'>First of all, where is your crop? <br/> Click on the globe! </p>
              <div className="globeContainer">
                <WorldCountryPicker markers={markers} setMarkers={setMarkers} />
              </div>
              <button className='mainButtonIII' onClick={segundo}>There it is!</button>
            </div>
          </div>
        );
      }
    if (estado == 2) {
        return (
          <div className="inicio">
            <img src={grid} className='grid'></img>
            <img src={cabraNasa} className='cabra Nasa'></img>
            <div className='master'>
              <img src={bocadillo} className='bocadillo'></img>
              <p className='texto'>What a nice place to farm! <br />
                Plase, tell me more!<br />
                Which definition fits better to you?</p>
              <div className='buttonWrapper'> 
                <button className='mainButton tamaño' onClick={pequeño}>I'm a local farmer, small scale business.</button>
                <button className='mainButton tamaño' onClick={grande}>I have an industry, large scale business.</button>
              </div>
              <button className='secondButton' onClick={atrás}>Back</button>
            </div>
          </div>
        );
      }
    if (estado == 3) {
        return (
          <div className="inicio">
            <img src={grid} className='grid'></img>
            <img src={cabraNasa} className='cabra Nasa'></img>
            <div className='master'>
              <img src={bocadillo} className='bocadillo'></img>
              <p className='texto'>Ok, that's nice! <br />
                Lastly, what crop do you farm?</p>
              <div className='buttonWrapper horizontal'> 
                <button className='mainButton tamaño' onClick={tomate}>Fruits</button>
                <button className='mainButton tamaño' onClick={maiz}>Corn</button>
                <button className='mainButton tamaño' onClick={trigo}>Wheat</button>
              </div>
              <button className='secondButton' onClick={atrás}>Back</button>
            </div>
          </div>
        );
      }
    if (estado == 4) {
        return (
          <div className="inicio">
            <img src={grid} className='grid'></img>
            <img src={cabraNasa} className='cabra Nasa'></img>
            <div className='master'>
              <img src={bocadillo} className='bocadillo'></img>
              <p className='texto'>Everything ready? <br />
                Let's start!</p>
                <button className='mainButton' onClick={enviarDatos}>YES!</button>
              <button className='secondButton' onClick={atrás}>Back</button>
            </div>
          </div>
        );
      }

  }

export default Inicio;
