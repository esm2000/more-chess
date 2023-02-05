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