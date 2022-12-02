import React from 'react';
import { useState } from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';
import GeneralRules from './GeneralRules';
import PawnRules from './PawnRules';
import KnightRules from './KnightRules';
import RookRules from './RookRules';
import BishopRules from './BishopRules';
import QueenRules from './QueenRules';

const Rules = () => {
    const gameState = GameStateContextData()
    const boardState = gameState.boardState
    const positionInPlay = gameState.positionInPlay
    const isMobile = gameState.isMobile

    return(
        <div
            className="rules"
        >
            <h2>Rules</h2>
            {
                (!positionInPlay[0] && positionInPlay[0] !== 0) && (!positionInPlay[1] && positionInPlay[1] !== 0) ? 
                    <GeneralRules 
                        isMobile={isMobile}
                    />
                : null
            }
            {
                (positionInPlay[0] || positionInPlay[0] === 0) && (positionInPlay[1] || positionInPlay[1] === 0) ?
                    boardState?.[positionInPlay[0]]?.[positionInPlay[1]]?.some((piece) => piece.type.includes("pawn")) ?
                        <PawnRules 
                            isMobile={isMobile}
                        />
                    : null
                : null
            }
            {
                (positionInPlay[0] || positionInPlay[0] === 0) && (positionInPlay[1] || positionInPlay[1] === 0) ?
                    boardState?.[positionInPlay[0]]?.[positionInPlay[1]]?.some((piece) => piece.type.includes("knight")) ?
                    <KnightRules 
                        isMobile={isMobile}
                    />
                    : null
                : null
            }
            {
                (positionInPlay[0] || positionInPlay[0] === 0) && (positionInPlay[1] || positionInPlay[1] === 0) ?
                    boardState?.[positionInPlay[0]]?.[positionInPlay[1]]?.some((piece) => piece.type.includes("bishop")) ?
                    <BishopRules 
                        isMobile={isMobile}
                    />
                    : null
                : null
            }
            {
                (positionInPlay[0] || positionInPlay[0] === 0) && (positionInPlay[1] || positionInPlay[1] === 0) ?
                    boardState?.[positionInPlay[0]]?.[positionInPlay[1]]?.some((piece) => piece.type.includes("rook")) ?
                    <RookRules 
                        isMobile={isMobile}
                    />
                    : null
                : null
            }
            {
                (positionInPlay[0] || positionInPlay[0] === 0) && (positionInPlay[1] || positionInPlay[1] === 0) ?
                    boardState?.[positionInPlay[0]]?.[positionInPlay[1]]?.some((piece) => piece.type.includes("queen")) ?
                    <QueenRules 
                        isMobile={isMobile}
                    />
                    : null
                : null
            }
        </div>
    );
}

export default Rules;