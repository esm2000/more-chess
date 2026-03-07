import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, PLAYERS, getPiecePrice, determineIsMobile } from '../utility';
import PieceShopModal from './PieceShopModal';


const Shop = (props) => {
    const gameState = GameStateContextData()
    const playerGoldCount = gameState.goldCount[PLAYERS[0]] - (getPiecePrice(props.shopPieceSelected) || 0)
    const isMobile = determineIsMobile()

    return(
        <div
            className="pixel-panel"
            style={{
                width: `${isMobile ? 55 : 27.15}vw`,
                marginTop: `${isMobile ? 3 : 1.5}vw`,
                borderWidth: `${isMobile ? 2.5 : 1.25}vw`,
            }}
        >
            <div style={{
                backgroundColor: 'rgb(71, 33, 1)',
                padding: `${isMobile ? 1 : 0.5}vw 0`,
                textAlign: 'center'
            }}>
                <p style={{
                    fontFamily: 'Basic',
                    fontSize: `${isMobile ? 3 : 1.5}vw`,
                    margin: 0
                }}>~ Shop ~</p>
            </div>
            <div style={{
                display: "flex",
                justifyContent: "center",
                padding: `${isMobile ? 2 : 1}vw 0`,
                borderBottom: `${isMobile ? 0.3 : 0.15}vw solid rgb(71, 33, 1)`
            }}>
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
            <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: `${isMobile ? 1 : 0.5}vw ${isMobile ? 1.5 : 0.75}vw`
            }}>
                <div className="gold-display" style={{ fontSize: `${isMobile ? 2 : 1}vw` }}>
                    <img
                        src={IMAGE_MAP["goldCoin"]}
                        alt="gold"
                        style={{ height: `${isMobile ? 3 : 1.5}vw` }}
                    />
                    <span>{playerGoldCount} Gold</span>
                </div>
                {props.shopPieceSelected && (
                    <button
                        className="pixel-btn"
                        onClick={() => props.setShopPieceSelected(null)}
                        style={{
                            fontSize: `${isMobile ? 1.5 : 0.75}vw`,
                            padding: `${isMobile ? 0.5 : 0.25}vw ${isMobile ? 1 : 0.5}vw`,
                            borderRadius: `${isMobile ? 0.6 : 0.3}vw`
                        }}
                    >Cancel</button>
                )}
            </div>
        </div>
    );
}

export default Shop;