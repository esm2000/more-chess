import React from 'react';
import '../index.css';

import setPositionInPlay, { GameStateContextData }  from '../context/GameStateContext';

import { determineBackgroundColor, determineColor, DRAGON_POSITION, BOARD_HERALD_POSITION, BARON_NASHOR_POSITION } from '../utility';

const isBossActive = (boardState, bossPosition, bossType) => {
    return !boardState[bossPosition[0]][bossPosition[1]] ? 
        false :
    boardState[bossPosition[0]][bossPosition[1]].type === bossType
}

const Square = (props) => {
    const row = props.row
    const col = props.col
    const gameState = GameStateContextData();
    const isDragonActive = isBossActive(gameState.boardState, DRAGON_POSITION, "neutral_dragon")
    const isHeraldActive = isBossActive(gameState.boardState, BOARD_HERALD_POSITION, "neutral_board_herald")
    const isBaronActive = isBossActive(gameState.boardState, BARON_NASHOR_POSITION, "neutral_baron_nashor")
    const positionInPlay = gameState.positionInPlay
    const possibleCaptures = gameState.possibleCaptures
    const swordInTheStonePosition = gameState.swordInTheStonePosition

    const backgroundColor = determineBackgroundColor(row, col, positionInPlay, possibleCaptures, isDragonActive, isHeraldActive, isBaronActive, swordInTheStonePosition)
    const color = determineColor(row, col, isDragonActive, isHeraldActive, isBaronActive)

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