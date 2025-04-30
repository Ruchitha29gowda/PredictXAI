// import { useState } from 'preact/hooks'
// import preactLogo from './assets/preact.svg'
// import viteLogo from '/vite.svg'
import './app.css'
import Form from './form'
import {useState} from 'react';

export function App() {
  const [isVisible, setIsVisible] = useState(false);
  const togglevisisbilty=()=>{
    setIsVisible(!isVisible);
  }

  return (
    <>
      {
        !isVisible && 
        <div id='welcome'>
          <div id="msg">
          <h3>
            Your Heart Health Matters: Assess Your Stroke Risk and Take Control Today.
            </h3>
          </div>
          <div id="img">
            <h1>Your heart , your Responsibility</h1>
          </div>
          <div id="predict">
            <button id="pred-button" onClick={togglevisisbilty}>
              Predict heart stroke
            </button>
          </div>
        </div>
      }

      {
        isVisible && <div id='form-vis'>
          <Form/>
          <br /><br /><br />
          <div id="but">
            <button id='back-button' onClick={togglevisisbilty}>Back to home page</button>
          </div>
        </div>
      }
    </>
  )
}
