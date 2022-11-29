import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP } from '../utility';


const PawnRules = (props) => {
    const gameState = GameStateContextData()

    const pieceImageStyle = {
        height: props.isMobile ? "4vw": "2vw", 
        float: "left"
    }

    const h4Style = {
        position: "relative", 
        top: "1vw" 
    }

    return(
        <div>
            <h3>Pawns</h3>
            <div display="flex">
                <img
                    src={IMAGE_MAP["whitePawn"]}
                    style={pieceImageStyle}
                />
                <h4 style={{...h4Style, left: "1vw"}}>Normal</h4>
            </div>
            <ul>
                <li>Moves forward one square (except first move with pawn can be two squares)</li>
                <li>Captures diagonally one square at a time</li>
            </ul>
            <div display="flex">
                <img
                    src={IMAGE_MAP["whitePawn2"]}
                    style={pieceImageStyle}
                />
                <h4 style={{...h4Style, left: "0.8vw"}}>Buff after getting 2+ capture point advantage</h4>
            </div>
            <ul>
                <li>Can also capture enemy pawns directly in front of them</li>
            </ul>
            <div display="flex">
                <img
                    src={IMAGE_MAP["whitePawn3"]}
                    style={pieceImageStyle}
                />
                <h4 style={{...h4Style, left: "0.6vw"}}>Buff after getting 3+ capture point advantage</h4>
            </div>
            <ul>
                <li>Cannot get captured by enemy pawns</li>
            </ul>
        </div>
    );
}

export default PawnRules;