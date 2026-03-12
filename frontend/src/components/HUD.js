import React, {useState, useEffect, useRef} from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, PLAYERS, useIsMobile } from '../utility';
import Shop from './Shop';


const HUD = (props) => {
    const gameState = GameStateContextData()
    const turnCount = gameState.turnCount
    const goldCount = gameState.goldCount?.[PLAYERS[0]] || 0
    const enemyGoldCount = gameState.goldCount?.[PLAYERS[1]] || 0
    const isMobile = useIsMobile()
    const [toggleShop, setToggleShop] = useState(false)
    const [showRestartConfirm, setShowRestartConfirm] = useState(false)
    const [turnFlashClass, setTurnFlashClass] = useState('')
    const prevTurnCount = useRef(turnCount)
    const isInitialLoad = useRef(true)

    useEffect(() => {
        const prev = prevTurnCount.current
        prevTurnCount.current = turnCount

        if (isInitialLoad.current) {
            isInitialLoad.current = false
            return
        }

        if (prev === turnCount) return

        const prevIsPlayerTurn = prev % 2 === 0
        const currIsPlayerTurn = turnCount % 2 === 0

        if (prevIsPlayerTurn === currIsPlayerTurn) {
            const flashClass = currIsPlayerTurn ? 'turn-flash-green' : 'turn-flash-red'
            setTurnFlashClass(flashClass)
            const timer = setTimeout(() => setTurnFlashClass(''), 1000)
            return () => clearTimeout(timer)
        }
    }, [turnCount])

    const handleShopButtonClick = () => {
        setToggleShop(!toggleShop)
    }

    const isWhiteTurn = turnCount % 2 === 0
    const isKingOnHomeSquare = gameState.boardState[7][4]?.[0]?.type === "white_king"

    const handleConfirmRestart = () => {
        setShowRestartConfirm(false)
        setToggleShop(false)
        props.setShopPieceSelected(null)
        gameState.restartGame()
    }

    const confirmBtnStyle = {
        fontSize: `${isMobile ? 1.4 : 0.7}vw`,
        padding: `${isMobile ? 0.4 : 0.2}vw ${isMobile ? 1 : 0.5}vw`,
        borderRadius: `${isMobile ? 0.6 : 0.3}vw`
    }

    useEffect(() => {
        if (!isWhiteTurn || !isKingOnHomeSquare) {
            setToggleShop(false)
            props.setShopPieceSelected(null)
        }
    }, [isWhiteTurn, isKingOnHomeSquare])
    return(
        <div>
            <div style={{
                backgroundColor: 'rgb(71, 33, 1)',
                border: `${isMobile ? 0.4 : 0.2}vw solid rgb(50, 23, 0)`,
                padding: `${isMobile ? 1.5 : 0.75}vw ${isMobile ? 2 : 1}vw`,
                fontFamily: 'Basic',
                color: 'white',
                marginTop: `${isMobile ? 1 : 0.5}vw`,
                width: isMobile ? '59.2vw' : '29.6vw',
                boxSizing: 'border-box'
            }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: `${isMobile ? 1 : 0.5}vw`
                }}>
                    <span className={turnFlashClass} style={{ fontSize: `${isMobile ? 2.5 : 1.25}vw`, display: 'inline-block' }}>Turn: {turnCount}</span>
                    {isWhiteTurn && isKingOnHomeSquare ?
                        <button
                            className="pixel-btn"
                            onClick={() => handleShopButtonClick()}
                            style={{
                                fontSize: `${isMobile ? 1.8 : 0.9}vw`,
                                padding: `${isMobile ? 0.6 : 0.3}vw ${isMobile ? 1.5 : 0.75}vw`,
                                borderRadius: `${isMobile ? 0.6 : 0.3}vw`
                            }}
                        >{toggleShop ? "Close Shop" : "Open Shop"}</button> :
                        null
                    }
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', gap: `${isMobile ? 3 : 1.5}vw`, alignItems: 'center' }}>
                        <div className="gold-display" style={{ fontSize: `${isMobile ? 2 : 1}vw` }}>
                            <span style={{ color: 'rgb(230, 233, 198)' }}>You:</span>
                            <img
                                src={IMAGE_MAP["goldCoin"]}
                                alt="gold"
                                style={{ height: `${isMobile ? 2.5 : 1.25}vw` }}
                            />
                            <span style={{ color: 'rgb(230, 233, 198)' }}>{goldCount}</span>
                        </div>
                        <div className="gold-display" style={{ fontSize: `${isMobile ? 2 : 1}vw`, opacity: 0.7 }}>
                            <span style={{ color: 'rgb(180, 180, 180)' }}>Enemy:</span>
                            <img
                                src={IMAGE_MAP["goldCoin"]}
                                alt="enemy gold"
                                style={{ height: `${isMobile ? 2.5 : 1.25}vw`, filter: 'grayscale(100%)' }}
                            />
                            <span style={{ color: 'rgb(180, 180, 180)' }}>{enemyGoldCount}</span>
                        </div>
                    </div>
                    {showRestartConfirm ?
                        <div style={{ display: 'flex', gap: `${isMobile ? 0.6 : 0.3}vw`, alignItems: 'center' }}>
                            <span style={{ fontSize: `${isMobile ? 1.4 : 0.7}vw`, opacity: 0.8 }}>Restart?</span>
                            <button
                                className="pixel-btn"
                                onClick={handleConfirmRestart}
                                style={confirmBtnStyle}
                            >Yes</button>
                            <button
                                className="pixel-btn"
                                onClick={() => setShowRestartConfirm(false)}
                                style={confirmBtnStyle}
                            >No</button>
                        </div> :
                        <button
                            className="pixel-btn"
                            onClick={() => setShowRestartConfirm(true)}
                            style={{...confirmBtnStyle, opacity: 0.7}}
                        >Restart</button>
                    }
                </div>
            </div>
            {
                toggleShop ?
                 <Shop
                    shopPieceSelected={props.shopPieceSelected}
                    setShopPieceSelected={props.setShopPieceSelected}
                 /> :
                 null
            }
        </div>
    );
}

export default HUD;
