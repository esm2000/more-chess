import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';


const QueenRules = (props) => {
    const gameState = GameStateContextData()

    const imageStyle = {
        height: props.isMobile ? "30vw": "15vw", 
        display: "block", 
        margin: "auto"
    }

    return(
        <div>
            <h3>Queens</h3>
            <p>Can move in any direction (vertically, horizontally, and diagonally)</p>
            <img
                src={IMAGE_MAP["queenMovement"]}
                style={imageStyle}
            />
            <p>If a queen moves but does not capture an enemy piece, it stuns all enemy pieces adjacent to it</p>
            <img
                src={IMAGE_MAP["queenStun"]}
                style={imageStyle}
            />
            <p>On kills and assists queens are reset. If a queen captures a piece or assists in the capture of a piece and is not in danger of capture, <span style={{fontWeight: "bold"}}>it gains the ability to move again.</span> Assists are defined as being able to capture a piece but allowing another piece to capture it instead.</p>
        </div>
    );
}

export default QueenRules;