import React, { useState } from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

const PossibleMove = (props) => {
    const gameState = GameStateContextData()
    const isMobile = gameState.isMobile
    const topPosition = props.row * 3.7 * (gameState.isMobile ? 2: 1)
    const leftPosition = props.col * 3.7 * (gameState.isMobile ? 2: 1)
    const [isMouseOverSquare, setIsMouseOverSquare] = useState(false)


    return(
        <div
            onMouseOver={() => setIsMouseOverSquare(true)}
            onMouseLeave={() => setIsMouseOverSquare(false)}
        >
            <img 
                src={require('../assets/possible_move.png')} 
                alt='possible_move' 
                className='possible-move'
                style={{
                    top: `${topPosition}vw`,
                    left: `${leftPosition}vw`,
                    pointerEvents: 'none',
                    opacity: (!props.shopPieceSelected || (!isMouseOverSquare)) ? 1 : 0
                }}
            />
            
        </div>
    );
}

export default PossibleMove;