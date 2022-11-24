import React from 'react';

import  { GameStateContextData }  from '../context/GameStateContext';

const PossibleMove = (props) => {
    const gameState = GameStateContextData()
    const topPosition = props.row * 3.7
    const leftPosition = props.col * 3.7

    return(
        <div>
            <img 
                src={require('../assets/possible_move.png')} 
                alt='possible_move' 
                className='possible-move'
                style={{
                    top: `${topPosition}vw`,
                    left: `${leftPosition}vw`
                }}
            />
        </div>
    );
}

export default PossibleMove;