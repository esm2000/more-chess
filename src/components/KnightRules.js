import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';


const KnightRules = (props) => {
    const gameState = GameStateContextData()

    const imageStyle = {
        height: props.isMobile ? "15vw": "7.5vw", 
        display: "block", 
        margin: "auto"
    }

    return(
        <div>
            <h3>Knights</h3>
            <p>Move in a L-shape, 2 squares in one direction, 1 square perpendicular to the direction chosen.</p>
            <p>CANNOT JUMP OVER OTHER PIECES</p>
        </div>
    );
}

export default KnightRules;