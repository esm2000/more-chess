import React from 'react';
import { IMAGE_MAP } from '../utility';

const Victory = ({ isMobile }) => {

    const width = isMobile ? 49 : 24.5

    return(
        <img
            src={IMAGE_MAP["victory"]}
            alt="Victory"
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

export default Victory;
