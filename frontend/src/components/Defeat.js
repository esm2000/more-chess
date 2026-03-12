import React from 'react';
import { IMAGE_MAP } from '../utility';

const Defeat = (props) => {

    const width = props.isMobile ? 49 : 24.5

    return(
        <div>
            <img
                src={IMAGE_MAP["defeat"]}
                style={
                    {
                        position: "absolute",
                        top: "45%",
                        left: "50%",
                        width: `${width}vw`,
                        transform: "translate(-50%, -50%)",
                        opacity: 0.6
                    }}
            />
        </div>
    );
}

export default Defeat;