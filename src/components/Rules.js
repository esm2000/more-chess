import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';


const Rules = () => {
    const gameState = GameStateContextData()

    return(
        <div
            className="rules"
        >
            <h3>Rules</h3>
        </div>
    );
}

export default Rules;