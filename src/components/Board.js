import React from 'react';

import Background from './Background';
import Piece from './Piece';
import PossibleMove from './PossibleMove';

import { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS } from '../utility';

const pickSide = (pieceName) => {
    if (pieceName.includes("white")) {
        return PLAYERS[0]
    }

    return PLAYERS[1]
}

const snakeToCamel = str =>
  str.toLowerCase().replace(/([-_][a-z])/g, group =>
    group
      .toUpperCase()
      .replace('-', '')
      .replace('_', '')
  );

const getPossibleCaptures = (boardState, possibleMoves) => {
    const possibleCaptures = []
    const possibleMovesJSONString = JSON.stringify(possibleMoves)
    let currPositionString

    boardState.forEach((row, i) => {
        row.forEach((piece, j) => {
            if (piece) {
                currPositionString = JSON.stringify([i, j])
                if (pickSide(piece) === PLAYERS[1] && possibleMovesJSONString.includes(currPositionString)) {
                    possibleCaptures.push([i, j]);
                }
            }
        })
    })

    return possibleCaptures
}

const Board = () => {
    // positionInPlay used to figure out what piece is being moved by player
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const boardState = gameState.boardState
    const possibleMoves = gameState.possibleMoves
    let possibleCaptures = getPossibleCaptures(boardState, possibleMoves)

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