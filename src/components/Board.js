import React from 'react';

import Background from './Background';
import Piece from './Piece'

import { GameStateContextData }  from '../context/GameStateContext';

const Board = () => {
    // positionInPlay used to figure out what piece is being moved by player
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay

    let row = 3
    let col = 4
    let row2 = 2

    return(
        <div style={{position: 'relative'}}>
            <Background />
            <Piece
                side="white"
                row={row} 
                col={col}
                inPlay={positionInPlay[0] === row && positionInPlay[1] === col} 
                type="placeholder"
            />
            <Piece
                side="white"
                row={row2} 
                col={col}
                inPlay={positionInPlay[0] === row2 && positionInPlay[1] === col} 
                type="placeholder"
            />
        </div>
    );
}


export default Board;