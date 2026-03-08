import React from 'react';

import  { updateGameState, GameStateContextData }  from '../context/GameStateContext';

import { 
    PLAYERS, 
    IMAGE_MAP, 
    MAX_BOSS_HEALTH, 
    useIsMobile, 
    snakeToCamel,
    camelToSnake
} from '../utility';

const Piece = (props) => {
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const isMobile = useIsMobile()
    const topPosition = props.row * 3.7 * (isMobile ? 2: 1)
    const leftPosition = props.col * 3.7 * (isMobile ? 2: 1)

    const handlePieceClick = () => {
        if (props.shopPieceSelected) return

        const isNeutralPiecePresent = () => {
            if (props.side === "neutral") return true
            const square = gameState.boardState[props.row]?.[props.col] || []
            return square.some(piece => piece.type.includes("neutral"))
        }

        const capturePiece = (type) => {
            const newBoardState = [...gameState.boardState]
            const newPositionInPlay = [null, null]
            const pieceInPlay = newBoardState[positionInPlay[0]][positionInPlay[1]].find(piece => piece.type.includes(PLAYERS[0]))
            const newCapturedPieces = {...gameState.capturedPieces}

            for (let i = 0; i < newBoardState[props.row][props.col]?.length; i++) {
                if (snakeToCamel(newBoardState[props.row][props.col][i]?.type) === type) {
                    newCapturedPieces[PLAYERS[0]].push(newBoardState[props.row][props.col][i].type)
                    newBoardState[props.row][props.col].splice(i, 1);
                }
            }

            newBoardState[props.row][props.col] = newBoardState[props.row][props.col].filter(piece => !piece.type.includes(PLAYERS[1]))
            newBoardState[props.row][props.col].push(pieceInPlay)
            newBoardState[positionInPlay[0]][positionInPlay[1]] = newBoardState[positionInPlay[0]][positionInPlay[1]]?.filter(piece => piece.type !== pieceInPlay.type)

            gameState.updateGameState({
                ...gameState,
                capturedPieces: newCapturedPieces,
                boardState: newBoardState,
                positionInPlay: newPositionInPlay
            })
        }
        
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
        else if (props.side === PLAYERS[1] && positionInPlay?.[0] != null && positionInPlay?.[1] != null) {
            capturePiece(props.type)
        }

        // scenario 0 - a neutral monster is present with another friendly piece and there's no piece in play make it the piece in play
        else if (
            isNeutralPiecePresent() && 
            positionInPlay?.[0] === null &&
            positionInPlay?.[1] === null &&
            gameState.boardState[props.row][props.col].some((piece) => piece.type.includes(PLAYERS[0]))
        ) {
            gameState.updateGameState({...gameState, positionInPlay: [props.row, props.col]})

        }

        else if (isNeutralPiecePresent() && positionInPlay?.[0] != null && positionInPlay?.[1] != null) {
            const newBoardState = [...gameState.boardState]
            const pieceInPlay = newBoardState[positionInPlay[0]][positionInPlay[1]].find(piece => piece.type.includes(PLAYERS[0]))
            const newCapturedPieces = {...gameState.capturedPieces}
            var newGoldCount = {...gameState.goldCount}

            // scenario 1 - only a neutral monster is present with greater than 1 health
            // scenario 2 - only a neutral monster is present with 1 health
            if (gameState.boardState[props.row][props.col].length == 1) {
                for (let i = 0; i < newBoardState[props.row][props.col]?.length; i++) {
                    if (snakeToCamel(newBoardState[props.row][props.col][i]?.type) === props.type) {
                        // damage handled by backend
                        newBoardState[props.row][props.col].push(pieceInPlay)
                        newBoardState[positionInPlay[0]][positionInPlay[1]] = newBoardState[positionInPlay[0]][positionInPlay[1]].filter(piece => !piece.type.includes(PLAYERS[0]));
                    }
                }
                gameState.updateGameState({
                    ...gameState, 
                    capturedPieces: newCapturedPieces,
                    goldCount: newGoldCount,
                    boardState: newBoardState,
                    positionInPlay: [null, null]
                })
            }
            // scenario 3 - a neutral monster is present with greater than 1 health and another piece is present
            // scenario 4 - a neutral monster is present with 1 health and another piece is present
            else {
                // if the piece is friendly do nothing
                const square = gameState.boardState[props.row][props.col]
                // if the piece is an enemy piece capture it and damage the neutral monster
                // damage/capture on neutral monster handled by backend
                const enemyPiece = square.find(piece => piece.type.includes(PLAYERS[1]))
                
                if (enemyPiece) capturePiece(enemyPiece.type)
            }

            
        }   
    }

    const handleCastleClick = () => {
        const newBoardState = [...gameState.boardState]
        const kingRow = props.row
        const isQueenside = props.col === 0
        const kingCol = 4
        const kingTarget = isQueenside ? 2 : 6
        const rookTarget = isQueenside ? 3 : 5

        // Move king
        const kingPiece = newBoardState[kingRow][kingCol].find(piece => piece.type.includes('king'))
        newBoardState[kingRow][kingCol] = newBoardState[kingRow][kingCol].filter(piece => !piece.type.includes('king'))
        if (!newBoardState[kingRow][kingTarget]) newBoardState[kingRow][kingTarget] = []
        newBoardState[kingRow][kingTarget].push(kingPiece)

        // Move rook
        const rookPiece = newBoardState[kingRow][props.col].find(piece => piece.type.includes('rook'))
        newBoardState[kingRow][props.col] = newBoardState[kingRow][props.col].filter(piece => !piece.type.includes('rook'))
        if (!newBoardState[kingRow][rookTarget]) newBoardState[kingRow][rookTarget] = []
        newBoardState[kingRow][rookTarget].push(rookPiece)

        gameState.updateGameState({
            ...gameState,
            boardState: newBoardState,
            positionInPlay: [null, null]
        })
    }

    const isCastleAvailable = () => {
        if (!props.type.toLowerCase().includes('rook')) return false
        if (!gameState.castleMoves || gameState.castleMoves.length === 0) return false
        const targetCol = props.col === 0 ? 2 : 6
        return gameState.castleMoves.some(move => move[0] === props.row && move[1] === targetCol)
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
        var i = 0
        while (i < newBoardState[props.row][props.col]?.length) {
            if (snakeToCamel(newBoardState[props.row][props.col][i]?.type) === props.type) {
                newCapturedPieces[PLAYERS[0]].push(newBoardState[props.row][props.col][i].type)
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

        gameState.updateGameState({
            ...gameState,
            bishopSpecialCaptures: newBishopSpecialCaptures,
            boardState: newBoardState,
            capturedPieces: newCapturedPieces,
        })
        
    }

    const pickClassName = () => {
        if (props.side !== 'neutral') return 'regular_piece'
        if (props.type.toLowerCase().includes('dragon')) return 'dragon_piece'
        if (props.type.toLowerCase().includes('herald')) return 'herald_piece'
        if (props.type.toLowerCase().includes('nashor')) return 'nashor_piece'
    }

    const buffedSrc = props.pawnBuff ? props.type + `${props.pawnBuff + 1}` : props.type
    const image_src = IMAGE_MAP[buffedSrc] ? buffedSrc : props.type

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
            {isCastleAvailable() ?
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
                        borderColor: "#FFD700",
                        color: "white",
                        backgroundColor: "#DAA520",
                        cursor: "pointer",
                    }}
                    onClick={() => handleCastleClick()}
                >Castle</button>
                : null
            }
        </div>
    );
}

export default Piece;