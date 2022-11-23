import React from 'react';


const IMAGE_MAP = {
    placeholder: require('../assets/placeholder.png')
}

const Piece = (props) => {
    const top_position = props.row * 2.55
    const left_position = props.col * 2.57
    return(
        <div>
            <img 
                src={IMAGE_MAP[props.type]} 
                alt={props.type} 
                className='piece'
                style={{
                    top: `${top_position}em`,
                    left: `${left_position}em`
                }}
            />
        </div>
    );
}


export default Piece;