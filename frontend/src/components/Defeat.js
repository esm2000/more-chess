import React from 'react';
import { IMAGE_MAP } from '../utility';

const Defeat = (props) => {

    const topPosition = props.isMobile ? 22 : 11
    const leftPosition = props.isMobile ? 16 : 8
    const height = props.isMobile ? 13 : 6.5

    return(
        <div>
            <img 
                src={IMAGE_MAP["defeat"]}
                style={
                    {
                        position: "absolute", 
                        top: `${topPosition}vw`, 
                        left: `${leftPosition}vw`,
                        height: `${height}vw`
                    }}
            />
        </div>
    );
}

export default Defeat;