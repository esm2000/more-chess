import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';


const RookRules = (props) => {
    const gameState = GameStateContextData()

    const imageStyle = {
        height: props.isMobile ? "22vw": "11vw", 
        display: "block", 
        margin: !props.isMobile ? "auto" : null
    }

    return(
        <div>
            <h3>Rooks</h3>
            <p>Move vertically and horizontally</p>
            <p>Movement and capture range scales with game length</p>
            <div style={{display: "flex", flexDirection: props.isMobile ? "column" : "row"}}>
                <figure>
                    <img
                        src={IMAGE_MAP["rookMovementTurn0"]}
                        style={imageStyle}
                    />
                    <figcaption>range at turn 0</figcaption>
                </figure>
                <figure>
                    <img
                        src={IMAGE_MAP["rookMovementTurn15"]}
                        style={imageStyle}
                    />
                    <figcaption>range at turn 15</figcaption>
                </figure>
                <figure>
                    <img
                        src={IMAGE_MAP["rookMovementTurn20"]}
                        style={imageStyle}
                    />
                    <figcaption>range at turn 20</figcaption>
                </figure>
            </div>
            
        </div>
    );
}

export default RookRules;