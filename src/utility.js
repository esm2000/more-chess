const PLAYERS = ["white", "black"]

const IMAGE_MAP = {
    blackBishop: require('./assets/black_bishop.png'),
    blackKing: require("./assets/black_king.png"),
    blackKnight: require("./assets/black_knight.png"),
    blackPawn: require("./assets/black_pawn.png"),
    blackQueen: require("./assets/black_queen.png"),
    blackRook: require("./assets/black_rook.png"),
    whiteBishop: require('./assets/white_bishop.png'),
    whiteKing: require("./assets/white_king.png"),
    whiteKnight: require("./assets/white_knight.png"),
    whitePawn: require("./assets/white_pawn.png"),
    whiteQueen: require("./assets/white_queen.png"),
    whiteRook: require("./assets/white_rook.png"),
}

const GREEN_SQUARE_COLOR = "rgb(100, 133, 68)";
const WHITE_SQUARE_COLOR = "rgb(230, 233, 198)";
const DARK_GREEN_SQUARE_COLOR = "rgb(67, 90, 45)";
const DARK_WHITE_SQUARE_COLOR = "rgb(182, 185, 160)";
const LIGHT_GREEN_SQUARE_COLOR = "rgb(162, 215, 109)";
const LIGHT_WHITE_SQUARE_COLOR = "rgb(252, 255, 213)";
const GREEN_SELECTED_SQUARE_COLOR = "rgb(182, 195, 63)";
const WHITE_SELECTED_SQUARE_COLOR = "rgb(237, 255, 81)";
const RED_SQUARE_COLOR = "rgb(186, 0, 0)"

const getPossibleCaptures = (boardState, possibleMoves) => {
    const possibleCaptures = []
    const possibleMovesJSONString = JSON.stringify(possibleMoves)
    let currPositionString

    boardState.forEach((row, i) => {
        row.forEach((piece, j) => {
            if (piece) {
                currPositionString = JSON.stringify([i, j])
                if (pickSide(piece) === PLAYERS[1] && possibleMovesJSONString.includes(currPositionString)) {
                    possibleCaptures.push([i, j]);
                }
            }
        })
    })

    return possibleCaptures
}

const pickSide = (pieceName) => {
    if (pieceName.includes("neutral")) {
        return "neutral"
    } else if (pieceName.includes("white")) {
        return PLAYERS[0]
    }

    return PLAYERS[1]
}

const snakeToCamel = str =>
  str.toLowerCase().replace(/([-_][a-z])/g, group =>
    group
      .toUpperCase()
      .replace('-', '')
      .replace('_', '')
  );

const determineBackgroundColor = (row, col, positionInPlay, possibleCaptures) => {
    const offset = row % 2
    const currentPosition = [row, col]
    let green = GREEN_SQUARE_COLOR
    let white = WHITE_SQUARE_COLOR

    if(JSON.stringify(possibleCaptures).includes(JSON.stringify(currentPosition))) {
        return RED_SQUARE_COLOR
    }

    if (
        positionInPlay.toString() !== [null, null].toString() &&
        positionInPlay[0] === row &&
        positionInPlay[1] == col
    ) {
        green = GREEN_SELECTED_SQUARE_COLOR
        white = WHITE_SELECTED_SQUARE_COLOR
    }
    
    return (col + offset) % 2 === 0 ? white : green
}

const determineColor = (row, col) => {
    const offset = row % 2
    return (col + offset) % 2 === 0 ? GREEN_SQUARE_COLOR : WHITE_SQUARE_COLOR
}

export { 
    PLAYERS, 
    IMAGE_MAP, 
    getPossibleCaptures, 
    pickSide, 
    snakeToCamel, 
    determineBackgroundColor,
    determineColor 
};