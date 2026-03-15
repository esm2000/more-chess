import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, PLAYERS, getPiecePrice, useIsMobile } from '../utility';
import PieceShopModal from './PieceShopModal';


const Shop = (props) => {
    const gameState = GameStateContextData()
    const currentGold = gameState.goldCount[PLAYERS[0]]
    const projectedGoldCount = currentGold - (getPiecePrice(props.shopPieceSelected) || 0)
    const isMobile = useIsMobile()

    return(
        <div
            className="pixel-panel"
            style={{
                width: `${isMobile ? 65.0 : 32.5}vw`,
                marginTop: `${isMobile ? 3 : 1.5}vw`,
                borderWidth: `${isMobile ? 2.5 : 1.25}vw`,
                boxSizing: 'border-box',
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
                borderBottom: `${isMobile ? 0.3 : 0.15}vw solid rgb(71, 33, 1)`,
                cursor: projectedGoldCount < 2 ? 'not-allowed' : 'default'
            }}>
                <PieceShopModal
                    type="whitePawn"
                    projectedGoldCount={projectedGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
                <PieceShopModal
                    type="whiteKnight"
                    projectedGoldCount={projectedGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
                <PieceShopModal
                    type="whiteBishop"
                    projectedGoldCount={projectedGoldCount}
                    isMobile={isMobile}
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                />
                <PieceShopModal
                    type="whiteRook"
                    projectedGoldCount={projectedGoldCount}
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
                    <span>{projectedGoldCount} Gold</span>
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