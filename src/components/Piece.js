import React from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS, IMAGE_MAP } from '../utility';

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
            // TODO: add API call to update gameState.possibleMoves
        }
        console.log("position in play")
    }

    const pickClassName = () => {
        if (props.side !== 'neutral') return 'regular_piece'
        if (props.type.toLowerCase().includes('dragon')) return 'dragon_piece'
    }

    return(
        <div>
            <img 
                src={IMAGE_MAP[props.type]} 
                alt={props.type} 
                className={pickClassName()}
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