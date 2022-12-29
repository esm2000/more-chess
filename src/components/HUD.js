import React, {useState} from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import Shop from './Shop';


const HUD = () => {
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
                toggleShop ? <Shop /> : null
            }
        </div>
    );
}

export default HUD;