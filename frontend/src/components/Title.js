import React from 'react';
import { useIsMobile } from '../utility';


const Title = () => {
    const isMobile = useIsMobile()

    return(
        <div>
            <div className="title" style={{ textAlign: 'left' }}>
                <h1 style={{display: "inline", wordSpacing: "-0.5em"}}>League of Chess</h1>
                <h6 style={{display: "inline", marginLeft: "1em"}}>patch 1.1</h6>
                <hr style={{clear:"both"}}/>
            </div>
        </div>
    );
}

export default Title;