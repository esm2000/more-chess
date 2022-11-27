import React from 'react';
import { IMAGE_MAP } from '../utility';

const Buff = (props) => {

    const topPosition = props.row * 3.8
    const leftPosition = props.col * 3.7
    console.log("buff hide", props.hide)

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