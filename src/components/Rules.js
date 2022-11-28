import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';


const Rules = () => {
    const gameState = GameStateContextData()

    return(
        <div
            className="rules"
        >
            <h1>Rules</h1>
        </div>
    );
}

export default Rules;