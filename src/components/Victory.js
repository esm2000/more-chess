import React from 'react';
import { IMAGE_MAP } from '../utility';

const Victory = (props) => {

    const topPosition = props.isMobile ? 22 : 11
    const leftPosition = props.isMobile ? 13 : 6.5

    return(
        <div>
            <img 
                src={IMAGE_MAP["victory"]}
                style={
                    {
                        position: "absolute", 
                        top: `${topPosition}vw`, 
                        left: `${leftPosition}vw`,
                        height: `${leftPosition}vw`
                    }}
            />
        </div>
    );
}

export default Victory;