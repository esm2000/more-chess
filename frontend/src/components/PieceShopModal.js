import React from 'react';
import { IMAGE_MAP, getPiecePrice } from '../utility';


const PieceShopModal = (props) => {

    const price = getPiecePrice(props.type)
    const canAfford = props.playerGoldCount >= price
    const isSelected = props.shopPieceSelected === props.type

    const handleCardClick = () => {
        if (isSelected) {
            props.setShopPieceSelected(null)
        } else if (canAfford) {
            props.setShopPieceSelected(props.type)
        }
    }

    const cardClasses = `piece-card${isSelected ? ' piece-card-selected' : ''}${!canAfford ? ' piece-card-locked' : ''}`

    return(
        <div
            className={cardClasses}
            onClick={handleCardClick}
            style={{
                cursor: canAfford ? 'pointer' : 'not-allowed',
                position: 'relative',
                width: `${props.isMobile ? 10 : 5}vw`,
                marginRight: `${props.isMobile ? 1.5 : 0.75}vw`,
                marginLeft: props.type === "whitePawn" ? `${props.isMobile ? 2 : 1}vw` : 0,
            }}
        >
            <div style={{ position: 'relative' }}>
                <img
                    src={IMAGE_MAP[props.type]}
                    alt={props.type}
                    style={{
                        width: `${props.isMobile ? 8 : 4}vw`,
                        display: 'block',
                        imageRendering: 'pixelated'
                    }}
                />
                {!canAfford && (
                    <div style={{
                        position: 'absolute',
                        top: 0, left: 0, right: 0, bottom: 0,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        paddingTop: '85%',
                        fontSize: `${props.isMobile ? 9 : 4.5}vw`,
                        color: 'rgb(220, 30, 30)',
                        fontFamily: 'Basic',
                        fontWeight: 'bold',
                        textShadow: '2px 2px 0 black',
                        pointerEvents: 'none'
                    }}>X</div>
                )}
            </div>
            <p style={{
                fontFamily: 'Basic',
                fontSize: `${props.isMobile ? 1.5 : 0.75}vw`,
                margin: `${props.isMobile ? 0.4 : 0.2}vw 0`,
                color: 'rgb(71, 33, 1)'
            }}>{props.type.replace("white", "")}</p>
            <div className="gold-display" style={{
                justifyContent: 'center',
                fontSize: `${props.isMobile ? 1.2 : 0.6}vw`,
                color: 'rgb(71, 33, 1)'
            }}>
                <img
                    src={IMAGE_MAP["goldCoin"]}
                    alt="gold"
                    style={{ height: `${props.isMobile ? 1.5 : 0.75}vw` }}
                />
                <span>{price}</span>
            </div>
        </div>
    );
}

export default PieceShopModal;