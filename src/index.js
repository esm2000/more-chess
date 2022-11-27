import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

import { GameStateProvider } from './context/GameStateContext';

import Board from './components/Board';
import HUD from './components/HUD';
import CapturedPieces from './components/CapturedPieces';
import { PLAYERS } from './utility';


 
class App extends React.Component {
    constructor(props) {
        super(props);
    }
    
    render() {
        return (
            <div>
                <GameStateProvider>
                    <CapturedPieces 
                        side={PLAYERS[0]}
                    />
                    <Board />
                    <HUD />
                    <CapturedPieces 
                        side={PLAYERS[1]}
                    />
                </GameStateProvider>
            </div>
        );
    }
  }
  
  // ========================================
  
  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(<App />);
  
  