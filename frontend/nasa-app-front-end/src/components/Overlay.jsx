import React from 'react';
import logo from '../assets/pngs/logo.png';
import fondo from "../assets/pngs/fondo.png"

function Overlay() {
  return (
      <div className="carga">
        <img src={fondo} className='fondo'></img>
        <img src={logo} className='logo'></img>
      </div>
    );
}

export default Overlay;