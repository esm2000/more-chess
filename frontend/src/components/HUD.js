// HUD.js — REWORK NEEDED
// =======================
// Heads-up display: turn counter + shop toggle.
//
// TODO - VISUAL REWORK:
//   - Turn counter should use pixel font, maybe framed in a pixel art panel
//   - Shop Open/Close button should be a pixel art icon (chest, store sign, etc.)
//     instead of a plain green/red HTML button
//   - Consider adding gold count display here too (always visible, not just in shop)
//   - Layout should feel like a game HUD bar, not a plain div with text

import React, {useState} from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import Shop from './Shop';


const HUD = (props) => {
    const gameState = GameStateContextData()
    const turnCount = gameState.turnCount
    const [toggleShop, setToggleShop] = useState(false)

    const handleShopButtonClick = () => {
        setToggleShop(!toggleShop)
    }

    const isKingOnHomeSquare = gameState.boardState[7][4]?.[0].type === "white_king"
    return(
        <div>
            <h3># of Turns: {turnCount}</h3>
            {isKingOnHomeSquare ? 
                <button 
                    onClick={() => handleShopButtonClick()}
                    style={{
                        backgroundColor: toggleShop ? "red": "green",
                        borderColor: toggleShop ? "red": "green",
                        borderRadius: "0.5vw"
                    }}    
                >{toggleShop ? "Close": "Open"} Shop</button>:
                null
            }
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