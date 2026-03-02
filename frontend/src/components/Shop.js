// Shop.js — REWORK NEEDED
// ========================
// Current state: functional but visually basic. Needs pixel art retro overhaul.
//
// TODO - VISUAL REWORK:
//   - Replace plain HTML button/text styling with pixel art aesthetic
//   - Add a pixel art shop counter / storefront backdrop
//   - Piece sprites should sit on a shelf or display stand, not just float
//   - Gold display should feel like a coin counter (pixel coin sprites, not just text)
//   - "~ Shop ~" title could be a pixel art banner or sign
//   - Consider a shopkeeper character sprite for personality
//   - Close/Open button in HUD.js should also match the retro theme
//
// TODO - UX IMPROVEMENTS:
//   - Show piece placement preview on the board when a piece is selected
//   - Add a "Cancel" option to deselect a piece without placing it
//   - Visual feedback when purchase completes (gold deduction animation, etc.)
//   - Error state if backend rejects placement (currently no error handling)
//   - Consider showing which squares are valid for placement while piece is selected
//     (currently handled in Background.js via isValidSquare but the green buttons
//      are not very discoverable)
//
// NOTE: The buy flow itself works — PieceShopModal sets the selected piece,
// Background.js handles placement and sends the state update to the backend.
// Only the visual presentation needs reworking.

import React, { useState } from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, PLAYERS, getPiecePrice, determineIsMobile } from '../utility';
import PieceShopModal from './PieceShopModal';


const Shop = (props) => {
    const gameState = GameStateContextData()
    const playerGoldCount = gameState.goldCount[PLAYERS[0]] - (getPiecePrice(props.shopPieceSelected) || 0)
    const isMobile = determineIsMobile()

    return(
        <div
            className="shop"
            style={{
                width: `${isMobile ? 55: 27.15}vw`,
                marginTop: `${isMobile ? 3: 1.5}vw`,
                border: `${isMobile ? 2.5: 1.25}vw solid rgb(71, 33, 1)`,
                backgroundColor: "rgb(125, 59, 2)"
            }}
        >
            <p style={{fontSize: `${isMobile ? 3: 1.5}vw`, marginTop: `${isMobile ? 5: 2.5}vw`, textAlign: "center"}}>~ Shop ~</p>
            <div style={{display: "flex"}}>
                <PieceShopModal 
                    type="whitePawn"
                    playerGoldCount={playerGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
                <PieceShopModal 
                    type="whiteKnight"
                    playerGoldCount={playerGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
                <PieceShopModal 
                    type="whiteBishop"
                    playerGoldCount={playerGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
                <PieceShopModal 
                    type="whiteRook"
                    playerGoldCount={playerGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
            </div>
            <div style={{display: "flex", marginBottom: `${isMobile ? 1 : 0.5}vw`}}>
                <img 
                    src={IMAGE_MAP["goldCoin"]}
                    style={{
                        height: `${isMobile ? 3 : 1.5}vw`,
                        marginLeft: `${isMobile ? 1.5 : 0.75}vw`,
                        marginRight: `${isMobile ? 1: 0.5}vw`
                    }}
                />
                <p style={{
                    fontSize: `${isMobile ? 2 : 1}vw`,
                    margin: 0,
                }}>{playerGoldCount} Gold</p>
            </div>
            
        </div>
    );
}

export default Shop;