import React from 'react';

import  { updateGameState, GameStateContextData }  from '../context/GameStateContext';

import { 
    PLAYERS, 
    IMAGE_MAP, 
    MAX_BOSS_HEALTH, 
    determineIsMobile, 
    snakeToCamel,
    getPiecePrice,
    camelToSnake
} from '../utility';

const Piece = (props) => {
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const isMobile = determineIsMobile()
    const topPosition = props.row * 3.7 * (isMobile ? 2: 1)
    const leftPosition = props.col * 3.7 * (isMobile ? 2: 1)

    const handlePieceClick = () => {
        if (props.side === PLAYERS[0] && !props.isStunned) {
            
            if(
                gameState.positionInPlay.toString() === [null, null].toString() || 
                (gameState.positionInPlay[0] !== props.row || gameState.positionInPlay[1] !== props.col)
            ) {
                gameState.updateGameState({...gameState, positionInPlay: [props.row, props.col]})
            } else if(gameState.positionInPlay[0] === props.row && gameState.positionInPlay[1] === props.col) {
                gameState.updateGameState({...gameState, positionInPlay: [null, null]})
            }
        }
        if (props.side === PLAYERS[1] && positionInPlay?.[0] != null && positionInPlay?.[1] != null) {
            const newBoardState = [...gameState.boardState]
            const newPositionInPlay = [null, null]
            const pieceInPlay = newBoardState[positionInPlay[0]][positionInPlay[1]].find(piece => piece.type.includes(PLAYERS[0]))
            const newCapturedPieces = {...gameState.capturedPieces}
            var newGoldCount = {...gameState.goldCount}
            var capturedPiece
            var capturedPieceValue

            for (let i = 0; i < newBoardState[props.row][props.col]?.length; i++) {
                if (snakeToCamel(newBoardState[props.row][props.col][i]?.type) === props.type) {
                    capturedPiece = newBoardState[props.row][props.col][i]
                    capturedPieceValue = getPiecePrice(snakeToCamel(capturedPiece.type))
                    newCapturedPieces[PLAYERS[0]].push(capturedPiece.type)
                    newBoardState[props.row][props.col].splice(i, 1);
                }
            }
            newGoldCount[PLAYERS[0]] += capturedPieceValue ? capturedPieceValue : 0

            newBoardState[props.row][props.col] = newBoardState[props.row][props.col].filter(piece => piece.type === props.type)
            newBoardState[props.row][props.col].push(pieceInPlay)
            newBoardState[positionInPlay[0]][positionInPlay[1]] = newBoardState[positionInPlay[0]][positionInPlay[1]]?.filter(piece => piece.type !== pieceInPlay.type)

            gameState.updateGameState({
                ...gameState, 
                capturedPieces: newCapturedPieces,
                goldCount: newGoldCount,
                boardState: newBoardState,
                positionInPlay: newPositionInPlay
            })
        }
    }

    const handleSpareButtonClick = () => {
        const newBoardState = [...gameState.boardState]
        for (let i = 0; i < newBoardState[props.row][props.col].length; i++) {
            if (snakeToCamel(newBoardState[props.row][props.col][i]?.type) === props.type) {
                newBoardState[props.row][props.col][i].bishop_debuff = 0
            }
        }
        
        gameState.updateGameState({
            ...gameState, 
            boardState: newBoardState
        })
    }

    const handleCaptureButtonClick = () => {
        const newBoardState = [...gameState.boardState]
        const newCapturedPieces = {...gameState.capturedPieces}
        var newGoldCount = {...gameState.goldCount}
        var capturedPiece
        var capturedPieceValue
        var i = 0 
        while (i < newBoardState[props.row][props.col]?.length) {
            if (snakeToCamel(newBoardState[props.row][props.col][i]?.type) === props.type) {
                capturedPiece = newBoardState[props.row][props.col][i]
                capturedPieceValue = getPiecePrice(snakeToCamel(capturedPiece.type))
                newCapturedPieces[PLAYERS[0]].push(capturedPiece.type)
                newBoardState[props.row][props.col].splice(i, 1);
            }
            i++
        }
        
        const newBishopSpecialCaptures = [
            {
                position: [props.row, props.col],
                type: camelToSnake(props.type) 
            }
        ]
        
        newGoldCount[PLAYERS[0]] += capturedPieceValue ? capturedPieceValue : 0
        gameState.updateGameState({
            ...gameState, 
            bishopSpecialCaptures: newBishopSpecialCaptures,
            boardState: newBoardState,
            capturedPieces: newCapturedPieces,
            goldCount: newGoldCount
        })
        
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
                        top: `${topPosition + (3.25 * (isMobile ? 2: 1)) }vw`,
                        left: `${leftPosition + (0.15 * (isMobile ? 2: 1))}vw`
                    }}
                /> : null}
            {props.isStunned ?
                <img
                    src={IMAGE_MAP['stunned']}
                    alt='stunned'
                    className={pickClassName()}
                    style={{
                        top: `${topPosition}vw`,
                        left: `${leftPosition - (0.3 * (isMobile ? 2: 1))}vw`,
                        width: isMobile ? '5vw': '2.5vw'
                    }}
                    onClick={() => handlePieceClick()}
                /> : null}
            {props.energizeStacks || props.energizeStacks === 0 ? 
                <p 
                    className={pickClassName()}
                    style={{
                        top: `${topPosition + (2.55 * (isMobile ? 2: 1))}vw`,
                        left: `${leftPosition - (0.75 * (isMobile ? 2: 1))}vw`,
                        fontWeight: 'bold',
                        background: '-webkit-linear-gradient(white, blue)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontSize: isMobile ? '2.4vw': '1.2vw'
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
                            width: isMobile ? '2vw': '1vw',
                            height: isMobile ? '2vw': '1vw',
                            top: `${topPosition}vw`,
                            left: `${leftPosition - (isMobile ? 3.5: 1.75) + (count * (isMobile ? 2.5: 1.2))}vw`
                        }}
                    />);
                }): null
            }
            {
                // TODO: add onClick functions that make API calls to capture or spare piece
                props.bishopDebuff === 3 && props.side === PLAYERS[1]?
                <div>
                    <button
                        className={pickClassName()}
                        style={{
                            top: `${(topPosition + 0.75) * (isMobile ? 1: 1)}vw`,
                            left: `${(leftPosition + 0) * (isMobile ? 1: 1)}vw`,
                            borderRadius: `${0.4 * (isMobile ? 2: 1)}vw`,
                            padding: `${0.15 * (isMobile ? 2: 1)}vw`,
                            height: `${1.25 * (isMobile ? 2: 1)}vw`,
                            width: `${4 * (isMobile ? 2: 1)}vw`,
                            fontSize: `0.5em`,
                            positon: "absolute",
                            textAlign: "center",
                            textDecoration: "none",
                            outline: "none",
                            borderColor: "#63bbf2",
                            color: "white",
                            backgroundColor: "#24a0ed",
                        }}
                        onClick={() => handleCaptureButtonClick()}
                    >Capture</button>
                    <button
                        className={pickClassName()}
                        style={{
                            top: `${(topPosition + (isMobile? 3.5: 2.25))}vw`,
                            left: `${(leftPosition + 0.5) * (isMobile ? 1.005: 1)}vw`,
                            borderRadius: `${0.4 * (isMobile ? 2: 1)}vw`,
                            padding: `${0.15 * (isMobile ? 2: 1)}vw`,
                            height: `${1.25 * (isMobile ? 2: 1)}vw`,
                            width: `${3 * (isMobile ? 2: 1)}vw`,
                            fontSize: `0.5em`,
                            positon: "absolute",
                            textAlign: "center",
                            textDecoration: "none",
                            outline: "none",
                            borderColor: "#ff4040",
                            color: "white",
                            backgroundColor: "#fd0e35",
                        }}
                        onClick={() => handleSpareButtonClick()}
                    >Spare</button>
                </div>
                : null
            }
            {props.checkProtection ?
                Array.from({length: props.checkProtection}, (_, i) => i + 1).map((count) => {
                    return(
                    <img 
                        src={IMAGE_MAP['checkProtection']}
                        className={pickClassName()}
                        style={{
                            width: isMobile ? '2.3vw': '1.15vw',
                            height: isMobile ? '2.3vw': '1.15vw',
                            top: `${topPosition}vw`,
                            left: `${leftPosition - (isMobile ? 3.5: 1.75) + (count * (isMobile ? 3.6: 1.2))}vw`
                        }}
                    />);
                }): null
            }
        </div>
    );
}

export default Piece;