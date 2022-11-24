import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

import { GameStateProvider } from './context/GameStateContext';

import Board from './components/Board';
import HUD from './components/HUD'

 
class App extends React.Component {
    constructor(props) {
        super(props);
    }
    
    render() {
        return (
            <div>
                <GameStateProvider>
                    <Board />
                    <HUD />
                </GameStateProvider>
            </div>
        );
    }
  }
  
  // ========================================
  
  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(<App />);
  
  