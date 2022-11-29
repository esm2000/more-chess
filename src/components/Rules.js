import React from 'react';
import { useState } from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';
import GeneralRules from './GeneralRules';

const Rules = () => {
    const gameState = GameStateContextData()
    const boardState = gameState.boardState
    const positionInPlay = gameState.positionInPlay
    const isMobile = gameState.isMobile

    console.log(boardState)
    console.log(positionInPlay)
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
                        <div>
                            <h3>Pawns</h3>
                            <div display="flex">
                                <img
                                    src={IMAGE_MAP["whitePawn"]}
                                    style={{float: "left", height: "2vw"}}
                                />
                                <h4 style={{position: "relative", top: "1vw", left: "1vw"}}>Normal</h4>
                            </div>
                            <ul>
                                <li>Moves forward one square (except first move with pawn can be two squares)</li>
                                <li>Captures diagonally one square at a time</li>
                            </ul>
                            <div display="flex">
                                <img
                                    src={IMAGE_MAP["whitePawn2"]}
                                    style={{float: "left", height: "2vw"}}
                                />
                                <h4 style={{position: "relative", top: "1vw", left: "0.8vw"}}>Buff after getting 2+ capture point advantage</h4>
                            </div>
                            <ul>
                                <li>Can also capture enemy pawns directly in front of them</li>
                            </ul>
                            <div display="flex">
                                <img
                                    src={IMAGE_MAP["whitePawn3"]}
                                    style={{float: "left", height: "2vw"}}
                                />
                                <h4 style={{position: "relative", top: "1vw", left: "0.6vw"}}>Buff after getting 3+ capture point advantage</h4>
                            </div>
                            <ul>
                                <li>Cannot get captured by enemy pawns</li>
                            </ul>
                        </div>
                    : null
                : null
            }
        </div>
    );
}

export default Rules;