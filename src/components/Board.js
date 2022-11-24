import React from 'react';

import Background from './Background';
import Piece from './Piece'

import { GameStateContextData }  from '../context/GameStateContext';

const pickSide = (pieceName) => {
    if (pieceName.includes("white")) {
        return "white"
    }

    return "black"
}

const snakeToCamel = str =>
  str.toLowerCase().replace(/([-_][a-z])/g, group =>
    group
      .toUpperCase()
      .replace('-', '')
      .replace('_', '')
  );

const Board = () => {
    // positionInPlay used to figure out what piece is being moved by player
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const boardState = gameState.boardState
    console.log("boardState", boardState)

    let row = 3
    let col = 4
    let row2 = 2

    return(
        <div style={{position: 'relative'}}>
            <Background />
            {
                boardState.map((pieceRow, row) => {
                    return (
                        <div>
                            {pieceRow.map((piece, col) => {
                                if (piece) {
                                    return (
                                        <Piece
                                            side={pickSide(piece)}
                                            row={row} 
                                            col={col}
                                            inPlay={positionInPlay[0] === row && positionInPlay[1] === col} 
                                            type={snakeToCamel(piece)}
                                        />
                                    );
                                }
                            })}
                        </div>
                    )
                })
            }
        </div>
    );
}


export default Board;