import { useState } from 'react';

import Background from './Background';
import Piece from './Piece';
import PossibleMove from './PossibleMove';
import Buff from './Buff';
import CapturedPieces from './CapturedPieces';
import HUD from './HUD';
import Victory from './Victory';
import Defeat from './Defeat';


import { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS, pickSide, snakeToCamel } from '../utility';

const Board = () => {
    // positionInPlay used to figure out what piece is being moved by player
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const boardState = gameState.boardState
    const possibleMoves = gameState.possibleMoves
    const possibleCaptures = gameState.possibleCaptures
    const swordInTheStonePosition = gameState.swordInTheStonePosition
    const isMobile = gameState.isMobile
    const playerVictory = gameState.playerVictory
    const playerDefeat = gameState.playerDefeat

    const [shopPieceSelected, setShopPieceSelected] = useState(null)

    return(
        <div style={isMobile ? {display: "block", margin: "auto"}: null}>
            <CapturedPieces 
                side={PLAYERS[1]}
            />
            <div style={{position: 'relative'}}>
                <Background 
                    possibleCaptures={possibleCaptures}
                    shopPieceSelected={shopPieceSelected}
                    setShopPieceSelected={setShopPieceSelected}
                />
                {
                    boardState.map((pieceRow, row) => {
                        return (
                            <div>
                                {pieceRow.map((piece_array, col) => {
                                    if (piece_array) {  
                                        return(
                                            piece_array.map((piece) => {
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
                                                        checkProtection={piece.check_protection}
                                                        health={piece.health}
                                                    />
                                                );
                                        }));
                                    }
                                })}
                                {possibleMoves.map((possibleMove, index) => {
                                    if (!possibleCaptures.some((possibleCapture) => JSON.stringify(possibleMove).includes(JSON.stringify(possibleCapture))))
                                        if (!shopPieceSelected || (possibleMove[0] <= 3)) {
                                            return(
                                                <PossibleMove 
                                                    key={'pm' + possibleMove[0].toString() + possibleMove[1].toString()}
                                                    row={possibleMove[0]}
                                                    col={possibleMove[1]}
                                                    shopPieceSelected={shopPieceSelected}
                                                />
                                            );
                                        }   
                                })}
                            </div>
                            
                        )
                    })
                }
                {swordInTheStonePosition ? 
                    <Buff
                        hide={boardState[swordInTheStonePosition[0]][swordInTheStonePosition[1]] ? true : false}
                        type='swordInTheStone'
                        row={swordInTheStonePosition[0]} 
                        col={swordInTheStonePosition[1]}
                    /> : null
                }
                {playerVictory ?
                    <Victory isMobile={isMobile}/> : playerDefeat ?
                    <Defeat isMobile={isMobile}/> : null
                }
            </div>
            <HUD 
                shopPieceSelected={shopPieceSelected}
                setShopPieceSelected={setShopPieceSelected}
            />
            <CapturedPieces 
                side={PLAYERS[0]}
            />
        </div>
        
    );
}


export default Board;