import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, LIGHT_BLUE_SQUARE_COLOR} from '../utility';


const KingRules = (props) => {
    const gameState = GameStateContextData()

    const imageStyle = {
        height: props.isMobile ? "30vw": "15vw", 
        display: "block", 
        margin: "auto"
    }

    return(
        <div>
            <h3>Kings</h3>
            <p>Can move in any direction one square at a time</p>
            <img
                src={IMAGE_MAP["kingMovement"]}
                style={imageStyle}
            />
            <p>Every 10 turns, the <span style={{color: LIGHT_BLUE_SQUARE_COLOR}}>Sword in the Stone</span> spawns at a random location in the map. Picking it up gives the king protection from one instance of check or checkmate. It can only be picked up by a king.</p>
            <img
                src={IMAGE_MAP["kingSwordInStoneCheckProtection"]}
                style={imageStyle}
            />
            <p>If a king returns to it's original square, shop access is granted. Using gold retrieved from kills, any non-neutral piece except for a queen or king can be bought.</p>
        </div>
    );
}

export default KingRules;