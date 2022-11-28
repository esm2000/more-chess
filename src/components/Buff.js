import React from 'react';
import { IMAGE_MAP } from '../utility';
import  { GameStateContextData }  from '../context/GameStateContext';

const Buff = (props) => {
    const gameState = GameStateContextData()
    const topPosition = props.row * 3.8 * (gameState.isMobile ? 3: 1)
    const leftPosition = props.col * 3.7 * (gameState.isMobile ? 3: 1)

    return(
        <div>
            {props.hide ? 
                null
            : <img 
                src={IMAGE_MAP[props.type]} 
                alt={props.type} 
                className='regular_piece'
                // className={pickClassName()}
                style={{
                    top: `${topPosition}vw`,
                    left: `${leftPosition}vw`
                }}
            />
            }
        </div>
    );
}

export default Buff;