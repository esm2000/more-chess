import React, {useState} from 'react';
import { GameStateContextData } from '../context/GameStateContext';
import { IMAGE_MAP, getPiecePrice } from '../utility';


const PieceShopModal = (props) => {

    const price = getPiecePrice(props.type)
    const canAfford = props.playerGoldCount >= price

    const pieceShopModalStyle = {
        width: `${props.isMobile ? 8: 4}vw`,
        marginRight: `${props.isMobile ? 4: 2}vw`,
        marginLeft: props.type === "whitePawn" ? `${props.isMobile ? 5: 2.5}vw`: 0,
        opacity: canAfford ? 1: 0.5
    }
    const pieceShopTitle = {
        marginLeft: props.type === "whitePawn" ? `${props.isMobile ? 5.7: 2.85}vw`: 0,
        fontSize: `${props.isMobile ? 2: 1}vw`,
        opacity: canAfford ? 1: 0.5
    }

    const handleBuyButtonClick = () => {
        console.log(`Buying ${props.type.replace("white", "")}`)
        props.setShopPieceSelected(props.type)
    }

    return(
        <div>
            <img
                src={IMAGE_MAP[props.type]}
                style={pieceShopModalStyle}
            /> 
            <p 
                style={{...pieceShopTitle, marginBottom: `${props.isMobile ? 0.4: 0.2}vw`}}
            >{props.type.replace("white", "")}</p>
            <div style={{display: "flex"}}>
                
                <button  
                    disabled={!canAfford} 
                    style={{
                        ...pieceShopTitle,
                        marginLeft: props.type === "whitePawn" ? `${props.isMobile ? 4.6: 2.3}vw`: 0,
                        marginTop: `${props.isMobile ? 1: 0.5}vw`,
                        marginBottom: `${props.isMobile ? 8: 4}vw`,
                        fontSize: `${props.isMobile ? 1.2: 0.6}vw`,
                        borderRadius: `${props.isMobile ? 1: 0.5}vw`,
                        backgroundColor: "rgb(102, 216, 242)",
                        borderColor: "rgb(150, 216, 242)"
                    }}
                    onClick={() => handleBuyButtonClick()}
                >
                    <img 
                        src={IMAGE_MAP["goldCoin"]}
                        style={{
                            opacity: canAfford ? 1: 0.5, 
                            marginRight: `${props.isMobile ? 0.2: 0.2}vw`,
                            height: `${props.isMobile ? 1.5: 0.75}vw`,
                        }} 
                    />{price} Gold</button>
            </div>
        </div>
    );
}

export default PieceShopModal;