import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';


const HUD = () => {
    const gameState = GameStateContextData()
    const turnCount = gameState.turnCount

    return(
        <div>
            <h3># of Turns: {turnCount}</h3>
        </div>
    );
}

export default HUD;