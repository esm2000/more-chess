import React from 'react';
import { useIsMobile } from '../utility';


const Title = () => {
    const isMobile = useIsMobile()

    return(
        <div>
            <div className="title" style={{ textAlign: isMobile ? 'center' : 'left' }}>
                <h1 style={{display: "inline"}}>Chess</h1>
                <h6 style={{display: "inline"}}>patch 1.1</h6>
                <hr style={{clear:"both"}}/>
            </div>
        </div>
    );
}

export default Title;