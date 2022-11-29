import React from 'react';
import { useState } from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';
import GeneralRules from './GeneralRules';

const Rules = () => {
    const gameState = GameStateContextData()
    const boardState = gameState.boardState
    const positionInPlay = gameState.positionInPlay

    return(
        <div
            className="rules"
        >
            <h2>Rules</h2>
            {
                !positionInPlay[0] && !positionInPlay[1] ? 
                    <GeneralRules />
                : null
            }
        </div>
    );
}

export default Rules;