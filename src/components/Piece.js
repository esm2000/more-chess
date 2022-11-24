import React from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS } from '../utility';

const IMAGE_MAP = {
    blackBishop: require('../assets/black_bishop.png'),
    blackKing: require("../assets/black_king.png"),
    blackKnight: require("../assets/black_knight.png"),
    blackPawn: require("../assets/black_pawn.png"),
    blackQueen: require("../assets/black_queen.png"),
    blackRook: require("../assets/black_rook.png"),
    whiteBishop: require('../assets/white_bishop.png'),
    whiteKing: require("../assets/white_king.png"),
    whiteKnight: require("../assets/white_knight.png"),
    whitePawn: require("../assets/white_pawn.png"),
    whiteQueen: require("../assets/white_queen.png"),
    whiteRook: require("../assets/white_rook.png"),
}

const Piece = (props) => {
    const gameState = GameStateContextData()
    const topPosition = props.row * 3.7
    const leftPosition = props.col * 3.7

    const handlePieceClick = () => {
        if (props.side === PLAYERS[0]) {
            
            if(
                gameState.positionInPlay.toString() === [null, null].toString() || 
                (gameState.positionInPlay[0] !== props.row || gameState.positionInPlay[1] !== props.col)
            ) {
                gameState.setPositionInPlay([props.row, props.col])
            } else if(gameState.positionInPlay[0] === props.row && gameState.positionInPlay[1] === props.col) {
                gameState.setPositionInPlay([null, null])
            }
        }
        console.log("position in play")
    }

    return(
        <div>
            <img 
                src={IMAGE_MAP[props.type]} 
                alt={props.type} 
                className='piece'
                style={{
                    top: `${topPosition}vw`,
                    left: `${leftPosition}vw`
                }}
                onClick={() => handlePieceClick()}
            />
        </div>
    );
}

export default Piece;