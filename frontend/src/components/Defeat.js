import React from 'react';
import { IMAGE_MAP } from '../utility';

const Defeat = ({ isMobile }) => {

    const width = isMobile ? 49 : 24.5

    return(
        <img
            src={IMAGE_MAP["defeat"]}
            alt="Defeat"
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
    );
}

export default Defeat;
