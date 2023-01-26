import React, { useState } from 'react';
import '../index.css';

import setPositionInPlay, { GameStateContextData }  from '../context/GameStateContext';

import { 
    determineBackgroundColor, 
    determineColor, 
    DRAGON_POSITION, 
    BOARD_HERALD_POSITION, 
    BARON_NASHOR_POSITION
} from '../utility';

const isBossActive = (boardState, bossPosition, bossType) => {
    return !boardState[bossPosition[0]][bossPosition[1]] ? 
        false :
    boardState[bossPosition[0]][bossPosition[1]].some((piece) => piece.type === bossType)
}

const Square = (props) => {
    const row = props.row
    const col = props.col
    const gameState = GameStateContextData();
    const boardState = gameState.boardState
    const isDragonActive = isBossActive(gameState.boardState, DRAGON_POSITION, "neutral_dragon")
    const isHeraldActive = isBossActive(gameState.boardState, BOARD_HERALD_POSITION, "neutral_board_herald")
    const isBaronActive = isBossActive(gameState.boardState, BARON_NASHOR_POSITION, "neutral_baron_nashor")
    const positionInPlay = gameState.positionInPlay
    const possibleCaptures = gameState.possibleCaptures
    const swordInTheStonePosition = gameState.swordInTheStonePosition

    const backgroundColor = determineBackgroundColor(row, col, positionInPlay, possibleCaptures, isDragonActive, isHeraldActive, isBaronActive, swordInTheStonePosition)
    const color = determineColor(row, col, isDragonActive, isHeraldActive, isBaronActive)
    const isMobile = gameState.isMobile

    const isValidSquare = (row, col) => {
        if (row <= 3) {
            return false
        }
        const bossPositions = [DRAGON_POSITION, BOARD_HERALD_POSITION, BARON_NASHOR_POSITION]
        for (let i = 0; i < bossPositions.length; i++) {
            if ([0, 1].includes(Math.abs(row - bossPositions[i][0])) && [0, 1].includes(Math.abs(col - bossPositions[i][1]))) {
                return false
            }
        }

        if (JSON.stringify([row, col]) === JSON.stringify(swordInTheStonePosition)){
            return false
        }

        if (boardState[row][col]) {
            return false
        }
    
        return true
    }

    const handleSquareSelectionClick = () => {
        props.setShopPieceSelected(null)
        // TODO: add an API call to update gameState with new positions and gold count
    }

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
            {
                props.shopPieceSelected && 
                isValidSquare(row, col) &&
                <button
                    onClick={() => handleSquareSelectionClick()}
                    style={{
                        fontSize: `${isMobile ? 1: 0.5}vw`,
                        height: `${isMobile ? 5: 1.75}vw`,
                        position: "relative",
                        right: `${isMobile ? 2.5: 1.9}vw`,
                        top: `${isMobile ? 1: 0.5}vw`,
                        borderRadius: `${isMobile ? 1: 0.5}vw`,
                        borderColor: "green",
                        backgroundColor: "green",
                        padding: `${isMobile ? 0.5 : 0}vw ${isMobile ? 0.75: 0.375}vw`
                    }}
                >Select Square</button>}
        </div>
    )
}


const Row = (props) => {
    return (
        <div style={{ display: 'flex', flexDirection: "row" }}>
            {
                new Array(8).fill(0).map((_, i) => (
                    <Square 
                        key={i} 
                        row={props.row} 
                        col={i}
                        shopPieceSelected={props.shopPieceSelected}
                        setShopPieceSelected={props.setShopPieceSelected}    
                    />
                ))
            }
        </div>
    );
}


const Background = (props) => {
    return (
        <div style={{ display: 'flex', flexDirection: "column" }}>
            {
                new Array(8).fill(0).map((_, i) => (
                    <Row 
                        key={i} 
                        row={i} 
                        shopPieceSelected={props.shopPieceSelected}
                        setShopPieceSelected={props.setShopPieceSelected}    
                    />
                ))
            }
        </div>
    );
}


export default Background;