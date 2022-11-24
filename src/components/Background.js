import React from 'react';
import '../index.css';

import setPositionInPlay, { GameStateContextData }  from '../context/GameStateContext';

const GREEN_SQUARE_COLOR = "rgb(100, 133, 68)";
const WHITE_SQUARE_COLOR = "rgb(230, 233, 198)";
const DARK_GREEN_SQUARE_COLOR = "rgb(67, 90, 45)";
const DARK_WHITE_SQUARE_COLOR = "rgb(182, 185, 160)";
const LIGHT_GREEN_SQUARE_COLOR = "rgb(162, 215, 109)";
const LIGHT_WHITE_SQUARE_COLOR = "rgb(252, 255, 213)";
const GREEN_SELECTED_SQUARE_COLOR = "rgb(182, 195, 63)";
const WHITE_SELECTED_SQUARE_COLOR = "rgb(237, 255, 81)";


const determineBackgroundColor = (row, col, positionInPlay) => {
    const offset = row % 2
    let green = GREEN_SQUARE_COLOR
    let white = WHITE_SQUARE_COLOR

    if (
        positionInPlay.toString() !== [null, null].toString() &&
        positionInPlay[0] === row &&
        positionInPlay[1] == col
    ) {
        green = GREEN_SELECTED_SQUARE_COLOR
        white = WHITE_SELECTED_SQUARE_COLOR
    }
    
    return (col + offset) % 2 === 0 ? white : green
}

const determineColor = (row, col) => {
    const offset = row % 2
    return (col + offset) % 2 === 0 ? GREEN_SQUARE_COLOR : WHITE_SQUARE_COLOR
}

const Square = (props) => {
    const row = props.row
    const col = props.col
    const gameState = GameStateContextData();
    const positionInPlay = gameState.positionInPlay

    const backgroundColor = determineBackgroundColor(row, col, positionInPlay)
    const color = determineColor(row, col)

    return (
        <div 
            style={{ backgroundColor }} 
            className="square"
        >
            <p 
                style={{ color, opacity: col === 0 ? 1 : 0 }}
                className='label' >{row + 1}</p>
            <p 
                style={{ 
                    color,
                    alignSelf: "flex-end",
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