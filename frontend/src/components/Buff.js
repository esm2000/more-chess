import React from 'react';
import { IMAGE_MAP, determineIsMobile } from '../utility';
import  { GameStateContextData }  from '../context/GameStateContext';

const Buff = (props) => {
    const gameState = GameStateContextData()
    const isMobile = determineIsMobile()
    const topPosition = props.row * 3.8 * (isMobile ? 2: 1)
    const leftPosition = props.col * 3.7 * (isMobile ? 2: 1)

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