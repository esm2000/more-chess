import React from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS } from '../utility';

const IMAGE_MAP = {
    placeholder: require('../assets/placeholder.png')
}

const Piece = (props) => {
    const gameState = GameStateContextData()
    const topPosition = props.row * 2.55
    const leftPosition = props.col * 2.57

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
                    top: `${topPosition}em`,
                    left: `${leftPosition}em`
                }}
                onClick={() => handlePieceClick()}
            />
        </div>
    );
}


export default Piece;