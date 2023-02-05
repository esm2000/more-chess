import React, { useState } from 'react';
import '../index.css';

import { GameStateContextData }  from '../context/GameStateContext';

import { 
    determineBackgroundColor, 
    determineColor, 
    determineIsMobile,
    DRAGON_POSITION, 
    BOARD_HERALD_POSITION, 
    BARON_NASHOR_POSITION,
    PLAYERS,
    camelToSnake,
    getPiecePrice
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
    const isMobile = determineIsMobile()

    const isValidSquare = (row, col) => {
        if (row <= 3) {
            return false
        }
        const bossPositions = []
        if (isDragonActive) bossPositions.push(DRAGON_POSITION)
        if (isHeraldActive) bossPositions.push(BOARD_HERALD_POSITION)
        if (isBaronActive) bossPositions.push(BARON_NASHOR_POSITION)
        
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
        const newBoardState = [...gameState.boardState]
        const selectedShopPieceValue = getPiecePrice(props.shopPieceSelected)
        var newGoldCount = {...gameState.goldCount}

        if (!newBoardState[row][col]) {
            newBoardState[row][col] = [{"type": camelToSnake(props.shopPieceSelected)}]
        } else {
            // player shouldn't be allowed to place piece where another piece is present
            return
        }

        newGoldCount[PLAYERS[0]] -= selectedShopPieceValue ? selectedShopPieceValue : 0
        
        gameState.updateGameState({
            ...gameState, 
            boardState: newBoardState,
            goldCount: newGoldCount
        })
        props.setShopPieceSelected(null)
    }

    const handleSquareClick = () => {

        if (positionInPlay?.[0] != null && positionInPlay?.[1] != null) {
            const newBoardState = [...gameState.boardState]
            const newPositionInPlay = [null, null]
            const pieceInPlay = newBoardState[positionInPlay[0]][positionInPlay[1]].find(piece => piece.type.includes(PLAYERS[0]))
            if (pieceInPlay) {
                if (newBoardState[row][col]) {
                    newBoardState[row][col].push(pieceInPlay)
                } else {
                    newBoardState[row][col] = [pieceInPlay]
                }
                newBoardState[positionInPlay[0]][positionInPlay[1]] = newBoardState[positionInPlay[0]][positionInPlay[1]]?.filter(piece => piece.type !== pieceInPlay.type)
            }
            gameState.updateGameState({
                ...gameState, 
                boardState: newBoardState,
                positionInPlay: newPositionInPlay
            })
        }
    }

    return (
        <div 
            style={{ backgroundColor }} 
            className="square"
            onClick={() => handleSquareClick()}
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
                        right: `${isMobile ? 2.5: 1.8}vw`,
                        top: `${isMobile ? 1: 0.5}vw`,
                        borderRadius: `${isMobile ? 1: 0.5}vw`,
                        borderColor: "green",
                        backgroundColor: "green",
                        padding: `${isMobile ? 0.5 : 0}vw ${isMobile ? 0.75: 0.375}vw`
                    }}
                >Select Position</button>}
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