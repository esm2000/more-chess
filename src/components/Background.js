import React from 'react';
import '../index.css';


const WHITE_SQUARE_COLOR = "rgb(100, 133, 68)";
const GREEN_SQUARE_COLOR = "rgb(230, 233, 198)";


const Square = (props) => {
    const row = props.row
    const col = props.col
    const offset = row % 2
    const backgroundColor = (col + offset) % 2 === 0 ? WHITE_SQUARE_COLOR : GREEN_SQUARE_COLOR
    const color = (col + offset) % 2 === 0 ? GREEN_SQUARE_COLOR : WHITE_SQUARE_COLOR
    return (
        <div 
            style={{ backgroundColor }} 
            className="square"
        >
            <p 
                style={{ color, opacity: col === 0 ? 1 : 0 }}
                className='label' >{row + 1}</p>
            <p 
                style={{ 
                    color,
                    alignSelf: "flex-end",
                    opacity: row === 7 ? 1 : 0
                }}
                className='label'
            >{String.fromCharCode(97 + col)}</p>
        </div>
    )
}


const Row = (props) => {
    return (
        <div style={{ display: 'flex', flexDirection: "row" }}>
            {
                new Array(8).fill(0).map((_, i) => (
                    <Square key={i} row={props.row} col={i}/>
                ))
            }
        </div>
    );
}


const Background = () => {
    return (
        <div style={{ display: 'flex', flexDirection: "column" }}>
            {
                new Array(8).fill(0).map((_, i) => (
                    <Row key={i} row={i} />
                ))
            }
        </div>
    );
}


export default Background;