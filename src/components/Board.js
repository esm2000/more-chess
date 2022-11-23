import React from 'react';

import Background from './Background';
import Piece from './Piece'


const Board = () => {
    return(
        <div style={{position: 'relative'}}>
            <Background />
            {new Array(8).fill(0).map((piece, i) => (
                <Piece key={i} row={i} col={i} type="placeholder"/>
            ))}
        </div>
    );
}


export default Board;