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
                                            side={pickSide(piece.type)}
                                            key={[row, col]}
                                            row={row} 
                                            col={col}
                                            inPlay={positionInPlay[0] === row && positionInPlay[1] === col} 
                                            type={snakeToCamel(piece.type)}
                                            pawnBuff={piece.pawn_buff}
                                            energizeStacks={piece.energize_stacks}
                                            isStunned={piece.is_stunned}
                                            bishopDebuff={piece.bishop_debuff}
                                        />
                                    );
                                }
                            })}
                            {possibleMoves.map((possibleMove, index) => {
                                if (!possibleCaptures.some((possibleCapture) => JSON.stringify(possibleMove).includes(JSON.stringify(possibleCapture))))
                                return(
                                    <PossibleMove 
                                        key={'pm' + possibleMove[0].toString() + possibleMove[1].toString()}
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