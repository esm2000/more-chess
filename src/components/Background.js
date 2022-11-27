import React from 'react';
import '../index.css';

import setPositionInPlay, { GameStateContextData }  from '../context/GameStateContext';

import { determineBackgroundColor, determineColor, BARON_NASHOR_POSITION } from '../utility';

const Square = (props) => {
    const row = props.row
    const col = props.col
    const gameState = GameStateContextData();
    const isBaronActive = gameState.boardState[BARON_NASHOR_POSITION[0]][BARON_NASHOR_POSITION[1]] === "neutral_baron_nashor"
    const positionInPlay = gameState.positionInPlay
    const possibleCaptures = gameState.possibleCaptures
    const swordInTheStonePosition = gameState.swordInTheStonePosition

    const backgroundColor = determineBackgroundColor(row, col, positionInPlay, possibleCaptures, isBaronActive, swordInTheStonePosition)
    const color = determineColor(row, col, isBaronActive)

    return (
        <div 
            style={{ backgroundColor }} 
            className="square"
        >
            <p 
                style={{ color, fontSize: "1vw", opacity: col === 0 ? 1 : 0 }}
                className='label' >{8-row}</p>
            <p 
                style={{ 
                    color,
                    alignSelf: "flex-end",
                    fontSize: "1vw",
                    opacity: row === 7 ? 1 : 0
                }}
                className='label'
            >{String.fromCharCode(97 + col)}</p>
        </div>
    )
}


const Row = (props) => {
    return (
        <div style={{ display: 'flex', flexDirection: "row" }}>
            {
                new Array(8).fill(0).map((_, i) => (
                    <Square key={i} row={props.row} col={i}/>
                ))
            }
        </div>
    );
}


const Background = () => {
    return (
        <div style={{ display: 'flex', flexDirection: "column" }}>
            {
                new Array(8).fill(0).map((_, i) => (
                    <Row key={i} row={i} />
                ))
            }
        </div>
    );
}


export default Background;