import React from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS, IMAGE_MAP, MAX_BOSS_HEALTH } from '../utility';

const Piece = (props) => {
    const gameState = GameStateContextData()
    const topPosition = props.row * 3.7 * (gameState.isMobile ? 3: 1)
    const leftPosition = props.col * 3.7 * (gameState.isMobile ? 3: 1)
    console.log("isMobile", gameState.isMobile)

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
            {props.health ?
                <progress 
                    className={pickClassName()}
                    value={props.health} 
                    max={MAX_BOSS_HEALTH[pickClassName().replace("_piece", "")]}
                    style={{
                        top: `${topPosition + (3.25 * (gameState.isMobile ? 3: 1)) }vw`,
                        left: `${leftPosition + (0.15 * (gameState.isMobile ? 3: 1))}vw`
                    }}
                /> : null}
            {props.isStunned ?
                <img
                    src={IMAGE_MAP['stunned']}
                    alt='stunned'
                    className={pickClassName()}
                    style={{
                        top: `${topPosition}vw`,
                        left: `${leftPosition - (0.3 * (gameState.isMobile ? 3: 1))}vw`,
                        width: gameState.isMobile ? '7.5vw': '2.5vw'
                    }}
                /> : null}
            {props.energizeStacks ? 
                <p 
                    className={pickClassName()}
                    style={{
                        top: `${topPosition + (2.55 * (gameState.isMobile ? 3: 1))}vw`,
                        left: `${leftPosition - (0.75 * (gameState.isMobile ? 3: 1))}vw`,
                        fontWeight: 'bold',
                        background: '-webkit-linear-gradient(white, blue)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontSize: gameState.isMobile ? '3.6vw': '1.2vw'
                    }}
                >
                    {props.energizeStacks}
                </p> : null
            }
            {props.bishopDebuff ?
                Array.from({length: props.bishopDebuff}, (_, i) => i + 1).map((count) => {
                    return(
                    <img 
                        src={IMAGE_MAP['bishopDebuff']}
                        className={pickClassName()}
                        style={{
                            width: gameState.isMobile ? '3vw': '1vw',
                            height: gameState.isMobile ? '3vw': '1vw',
                            top: `${topPosition}vw`,
                            left: `${leftPosition - (gameState.isMobile ? 5.25: 1.75) + (count * (gameState.isMobile ? 3.6: 1.2))}vw`
                        }}
                    />);
                }): null
            }
        </div>
    );
}

export default Piece;