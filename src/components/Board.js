import React from 'react';

import Background from './Background';
import Piece from './Piece';
import PossibleMove from './PossibleMove';

import { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS, getPossibleCaptures, pickSide, snakeToCamel } from '../utility';

const Board = () => {
    // positionInPlay used to figure out what piece is being moved by player
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const boardState = gameState.boardState
    const possibleMoves = gameState.possibleMoves
    const possibleCaptures = gameState.possibleCaptures

    console.log("boardState", boardState)
    console.log("possibleMoves", possibleMoves)
    console.log("possibleCaptures", possibleCaptures)

    return(
        <div style={{position: 'relative'}}>
            <Background 
                possibleCaptures={possibleCaptures}
            />
            {
                boardState.map((pieceRow, row) => {
                    return (
                        <div>
                            {pieceRow.map((piece, col) => {
                                if (piece) {  
                                    return (
                                        <Piece
                                            side={pickSide(piece)}
                                            key={[row, col]}
                                            row={row} 
                                            col={col}
                                            inPlay={positionInPlay[0] === row && positionInPlay[1] === col} 
                                            type={snakeToCamel(piece)}
                                        />
                                    );
                                }
                            })}
                            {possibleMoves.map((possibleMove, index) => {
                                if (!possibleCaptures.some((possibleCapture) => JSON.stringify(possibleMove).includes(JSON.stringify(possibleCapture))))
                                return(
                                    <PossibleMove 
                                        row={possibleMove[0]}
                                        col={possibleMove[1]}
                                    />
                                );
                            })}
                        </div>
                        
                    )
                })
            }
        </div>
    );
}


export default Board;