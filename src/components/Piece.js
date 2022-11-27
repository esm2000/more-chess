import React from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS, IMAGE_MAP } from '../utility';

const Piece = (props) => {
    const gameState = GameStateContextData()
    const topPosition = props.row * 3.7
    const leftPosition = props.col * 3.7

    const handlePieceClick = () => {
        if (props.side === PLAYERS[0] && !props.isStunned) {
            
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
    }

    const pickClassName = () => {
        if (props.side !== 'neutral') return 'regular_piece'
        if (props.type.toLowerCase().includes('dragon')) return 'dragon_piece'
        if (props.type.toLowerCase().includes('herald')) return 'herald_piece'
        if (props.type.toLowerCase().includes('nashor')) return 'nashor_piece'
    }

    const image_src = props.pawnBuff ? props.type + `${props.pawnBuff + 1}` : props.type

    if (props.type.includes("Pawn")) {
        console.log(image_src)
    }

    return(
        <div>
            <img 
                src={IMAGE_MAP[image_src]} 
                alt={image_src} 
                className={pickClassName()}
                style={{
                    top: `${topPosition}vw`,
                    left: `${leftPosition}vw`
                }}
                onClick={() => handlePieceClick()}
            />
            {props.isStunned ?
                <img
                    src={IMAGE_MAP['stunned']}
                    alt='stunned'
                    className={pickClassName()}
                    style={{
                        top: `${topPosition}vw`,
                        left: `${leftPosition - 0.3}vw`,
                        width: '2.5vw'
                    }}
                /> : null}
            {props.energizeStacks ? 
                <p 
                    className={pickClassName()}
                    style={{
                        top: `${topPosition + 2.55}vw`,
                        left: `${leftPosition - 0.75}vw`,
                        fontWeight: 'bold',
                        background: '-webkit-linear-gradient(white, blue)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}
                >
                    {props.energizeStacks}
                </p> : null}
        </div>
    );
}

export default Piece;