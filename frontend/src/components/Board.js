import { useState, useEffect } from 'react';

import Background from './Background';
import Piece from './Piece';
import PossibleMove from './PossibleMove';
import Buff from './Buff';
import CapturedPieces from './CapturedPieces';
import HUD from './HUD';
import Victory from './Victory';
import Defeat from './Defeat';
import Draw from './Draw';
import PawnExchangeModal from './PawnExchangeModal';


import { GameStateContextData }  from '../context/GameStateContext';

import { PLAYERS, pickSide, snakeToCamel, useIsMobile } from '../utility';

const Board = () => {
    // positionInPlay used to figure out what piece is being moved by player
    const gameState = GameStateContextData()
    const positionInPlay = gameState.positionInPlay
    const boardState = gameState.boardState
    const possibleMoves = gameState.possibleMoves
    const possibleCaptures = gameState.possibleCaptures
    const castleMoves = gameState.castleMoves || []
    const swordInTheStonePosition = gameState.swordInTheStonePosition
    const turnCount = gameState.turnCount
    const isMobile = useIsMobile()
    const blackDefeat = gameState.blackDefeat
    const whiteDefeat = gameState.whiteDefeat

    const [shopPieceSelected, setShopPieceSelected] = useState(null)
    const [pawnExchangePosition, setPawnExchangePosition] = useState(null)

    useEffect(() => {
        if (turnCount <= 0) {
            setPawnExchangePosition(null)
            return
        }
        if (possibleMoves.length === 0 && possibleCaptures.length === 0) {
            for (let col = 0; col < 8; col++) {
                const square = boardState[0]?.[col]
                if (square?.length) {
                    const whitePawn = square.find(piece => piece.type === "white_pawn")
                    if (whitePawn) {
                        setPawnExchangePosition([0, col])
                        return
                    }
                }
            }
        }
        setPawnExchangePosition(null)
    }, [boardState, possibleMoves, possibleCaptures, turnCount])

    const gutterSize = isMobile ? 2.4 : 1.2
    const borderSize = isMobile ? 0.5 : 0.25
    const bevelSize = isMobile ? 0.3 : 0.15
    const boardSize = isMobile ? 59.2 : 29.6
    const labelFontSize = isMobile ? '1.6vw' : '0.8vw'

    return(
        <div style={isMobile ? {display: "block", margin: "auto"}: null}>
            <div style={{ marginBottom: `${isMobile ? 1 : 0.5}vw` }}>
                <CapturedPieces
                    side={PLAYERS[1]}
                />
            </div>
            <div style={{
                display: 'inline-block',
                backgroundColor: 'rgb(71, 33, 1)',
                border: `${borderSize}vw solid rgb(50, 23, 0)`,
                padding: `${gutterSize * 0.5}vw ${gutterSize}vw ${gutterSize}vw ${gutterSize}vw`,
                boxSizing: 'content-box',
                position: 'relative',
                imageRendering: 'pixelated',
                boxShadow: `inset ${bevelSize}vw ${bevelSize}vw 0 rgb(125, 59, 2), inset -${bevelSize}vw -${bevelSize}vw 0 rgb(40, 18, 0)`,
            }}>
                {/* Row labels (8-1) in the left gutter */}
                <div style={{
                    position: 'absolute',
                    left: 0,
                    top: `${gutterSize * 0.5}vw`,
                    width: `${gutterSize}vw`,
                    height: `${boardSize}vw`,
                    display: 'flex',
                    flexDirection: 'column',
                }}>
                    {[8,7,6,5,4,3,2,1].map(num => (
                        <div key={num} style={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'rgb(230, 233, 198)',
                            fontSize: labelFontSize,
                            fontFamily: 'Basic',
                            fontWeight: 'bold',
                        }}>{num}</div>
                    ))}
                </div>
                {/* Column labels (a-h) in the bottom gutter */}
                <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: `${gutterSize}vw`,
                    width: `${boardSize}vw`,
                    height: `${gutterSize}vw`,
                    display: 'flex',
                    flexDirection: 'row',
                }}>
                    {['a','b','c','d','e','f','g','h'].map(letter => (
                        <div key={letter} style={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'rgb(230, 233, 198)',
                            fontSize: labelFontSize,
                            fontFamily: 'Basic',
                            fontWeight: 'bold',
                        }}>{letter}</div>
                    ))}
                </div>
                {/* The board */}
                <div style={{
                    position: 'relative',
                    outline: `${isMobile ? 0.2 : 0.1}vw solid rgb(40, 18, 0)`,
                }}>
                <Background 
                    possibleCaptures={possibleCaptures}
                    shopPieceSelected={shopPieceSelected}
                    setShopPieceSelected={setShopPieceSelected}
                />
                {
                    boardState.map((pieceRow, row) => {
                        return (
                            <div key={row}>
                                {pieceRow.map((piece_array, col) => {
                                    if (piece_array?.length) {
                                        return(
                                            piece_array.map((piece, i) => {
                                                return (
                                                    <Piece
                                                        side={pickSide(piece.type)}
                                                        key={`${row}-${col}-${i}`}
                                                        row={row}
                                                        col={col}
                                                        inPlay={positionInPlay[0] === row && positionInPlay[1] === col}
                                                        type={snakeToCamel(piece.type)}
                                                        pawnBuff={piece.pawnBuff}
                                                        energizeStacks={piece.energizeStacks}
                                                        isStunned={piece.isStunned}
                                                        bishopDebuff={piece.bishopDebuff}
                                                        checkProtection={piece.checkProtection}
                                                        health={piece.health}
                                                        shopPieceSelected={shopPieceSelected}
                                                        markedForDeath={piece.markedForDeath}
                                                        boardHeraldBuff={piece.boardHeraldBuff}
                                                        neutralBuffLog={gameState.neutralBuffLog}
                                                        // Only white king gets castle buttons; black castling is handled by AI
                                                        castleMoves={piece.type === "white_king" ? castleMoves : []}
                                                    />
                                                );
                                        }));
                                    }
                                })}
                            </div>
                        )
                    })
                }
                {!shopPieceSelected && possibleMoves.map((possibleMove) => {
                    // Filter out possible moves that overlap with capture positions
                    if (!possibleCaptures.some((possibleCapture) => JSON.stringify(possibleMove) === JSON.stringify(possibleCapture[0])))
                        return(
                            <PossibleMove
                                key={'pm' + possibleMove[0].toString() + possibleMove[1].toString()}
                                row={possibleMove[0]}
                                col={possibleMove[1]}
                                shopPieceSelected={shopPieceSelected}
                            />
                        );
                    return null;
                })}
                {swordInTheStonePosition ? 
                    <Buff
                        hide={boardState[swordInTheStonePosition[0]][swordInTheStonePosition[1]] ? true : false}
                        type='swordInTheStone'
                        row={swordInTheStonePosition[0]} 
                        col={swordInTheStonePosition[1]}
                    /> : null
                }
                {blackDefeat && whiteDefeat ?
                    <Draw isMobile={isMobile}/> : blackDefeat ?
                    <Victory isMobile={isMobile}/> : whiteDefeat ?
                    <Defeat isMobile={isMobile}/> : null
                }
                {pawnExchangePosition && (
                    <PawnExchangeModal
                        pawnPosition={pawnExchangePosition}
                        side={PLAYERS[0]}
                        onExchange={() => setPawnExchangePosition(null)}
                    />
                )}
                </div>
            </div>
            <HUD
                shopPieceSelected={shopPieceSelected}
                setShopPieceSelected={setShopPieceSelected}
            />
            <CapturedPieces 
                side={PLAYERS[0]}
            />
        </div>
        
    );
}


export default Board;