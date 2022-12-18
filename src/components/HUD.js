import React, {useState} from 'react';
import { GameStateContextData } from '../context/GameStateContext';


const HUD = () => {
    const gameState = GameStateContextData()
    const turnCount = gameState.turnCount
    const [toggleShop, setToggleShop] = useState(false)

    const handleShopButtonClick = () => {
        setToggleShop(!toggleShop)
        console.log("toggleShop", toggleShop)
    }

    const isKingOnHomeSquare = gameState.boardState[7][4]?.[0].type === "white_king"
    return(
        <div>
            <h3># of Turns: {turnCount}</h3>
            {isKingOnHomeSquare ? 
                <button onClick={() => handleShopButtonClick()}>{toggleShop ? "Close": "Open"} Shop</button>:
                null
            }
        </div>
    );
}

export default HUD;