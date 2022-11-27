import React from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, snakeToCamel, capitalizeFirstLetter } from '../utility';


const CapturedPieces = (props) => {
    const gameState = GameStateContextData()
    const capturedPieces = gameState.capturedPieces[props.side]

    return(
        <div>
            <h2 style={{marginBottom: "0"}}>{capitalizeFirstLetter(props.side)}'s Captured Pieces</h2>
            {capturedPieces.map((capturedPiece) => {
                return(
                    <img 
                        src={IMAGE_MAP[snakeToCamel(capturedPiece)]} 
                        alt={capturedPiece} 
                        className={capturedPiece.includes('neutral') ? 'neutral_captured_piece': 'captured_piece'}
                    />
                );
                
            })}
        </div>
    );
}

export default CapturedPieces;