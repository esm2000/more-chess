const PLAYERS = ["white", "black"]

const IMAGE_MAP = {
    blackBishop: require('./assets/black_bishop.png'),
    blackKing: require("./assets/black_king.png"),
    blackKnight: require("./assets/black_knight.png"),
    blackPawn: require("./assets/black_pawn.png"),
    blackPawn2: require("./assets/black_pawn_2.png"),
    blackPawn3: require("./assets/black_pawn_3.png"),
    blackQueen: require("./assets/black_queen.png"),
    blackRook: require("./assets/black_rook.png"),
    neutralDragon: require("./assets/neutral_dragon.png"),
    neutralBaronNashor: require('./assets/neutral_baron_nashor.gif'),
    neutralBoardHerald: require('./assets/neutral_board_herald.png'),
    whiteBishop: require('./assets/white_bishop.png'),
    whiteKing: require("./assets/white_king.png"),
    whiteKnight: require("./assets/white_knight.png"),
    whitePawn: require("./assets/white_pawn.png"),
    whitePawn2: require("./assets/white_pawn_2.png"),
    whitePawn3: require("./assets/white_pawn_3.png"),
    whiteQueen: require("./assets/white_queen.png"),
    whiteRook: require("./assets/white_rook.png"),
    stunned: require("./assets/stunned.png"),
    bishopDebuff: require("./assets/bishop_debuff.png"),
    swordInTheStone: require("./assets/sword_in_the_stone.png")
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
const BOSS_SQUARE_COLORS = {
    // dark color, light color
    "dragon": ["rgb(245, 175, 66)", "rgb(245, 221, 66)"],
    "board_herald": ["rgb(79, 22, 144)", "rgb(134, 73, 203)"],
    "baron_nashor": ["rgb(45, 13, 81)", "rgb(97, 61, 138)"]
}
const LIGHT_BLUE_SQUARE_COLOR = "rgb(102, 216, 242)"

const DRAGON_POSITION = [3, 7]
const BOARD_HERALD_POSITION = [4, 0]
const BARON_NASHOR_POSITION = [4, 0]

const BOSS_POSITIONS = {
    "dragon": DRAGON_POSITION,
    "board_herald": BOARD_HERALD_POSITION,
    "baron_nashor": BARON_NASHOR_POSITION
}

const MAX_BOSS_HEALTH = {
    "dragon": 5,
    "herald": 5,
    "nashor": 10
}

const getBossDangerZonePositions = (isBaronActive) => {

    const bossDangerZonePositions = {}
    const DangerZonePositions = []

    !isBaronActive ? delete BOSS_POSITIONS.baron_nashor : delete BOSS_POSITIONS.board_herald

    for (let boss in BOSS_POSITIONS) {
        DangerZonePositions.push(BOSS_POSITIONS[boss])
        DangerZonePositions.push([BOSS_POSITIONS[boss][0] - 1, BOSS_POSITIONS[boss][1]])
        DangerZonePositions.push([BOSS_POSITIONS[boss][0] + 1, BOSS_POSITIONS[boss][1]])

        if (boss === "dragon") {
            DangerZonePositions.push([BOSS_POSITIONS[boss][0] - 1, BOSS_POSITIONS[boss][1] - 1])
            DangerZonePositions.push([BOSS_POSITIONS[boss][0], BOSS_POSITIONS[boss][1] - 1])
            DangerZonePositions.push([BOSS_POSITIONS[boss][0] + 1, BOSS_POSITIONS[boss][1] - 1])
        }

        if (boss.includes("nashor") || boss.includes("herald")) {
            DangerZonePositions.push([BOSS_POSITIONS[boss][0] - 1, BOSS_POSITIONS[boss][1] + 1])
            DangerZonePositions.push([BOSS_POSITIONS[boss][0], BOSS_POSITIONS[boss][1] + 1])
            DangerZonePositions.push([BOSS_POSITIONS[boss][0] + 1, BOSS_POSITIONS[boss][1] + 1])
        }
        

        bossDangerZonePositions[boss] = [...DangerZonePositions]
        DangerZonePositions.length = 0
    }
    
    return bossDangerZonePositions

}

const getPossibleCaptures = (boardState, possibleMoves) => {
    const possibleCaptures = []
    const possibleMovesJSONString = JSON.stringify(possibleMoves)
    let currPositionString

    boardState.forEach((row, i) => {
        row.forEach((piece, j) => {
            if (piece) {
                currPositionString = JSON.stringify([i, j])
                if (pickSide(piece.type) === PLAYERS[1] && possibleMovesJSONString.includes(currPositionString)) {
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

const capitalizeFirstLetter = (string) =>  {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

const determineBackgroundColor = (row, col, positionInPlay, possibleCaptures, isBaronActive, swordInTheStonePosition) => {
    const offset = row % 2
    const currentPosition = [row, col]
    let green = GREEN_SQUARE_COLOR
    let white = WHITE_SQUARE_COLOR

    const dangerZonePositions = getBossDangerZonePositions(isBaronActive)
    
    if(JSON.stringify(possibleCaptures).includes(JSON.stringify(currentPosition))) {
        return RED_SQUARE_COLOR
    }

    if (swordInTheStonePosition && swordInTheStonePosition[0] === row && swordInTheStonePosition[1] === col) {
        return LIGHT_BLUE_SQUARE_COLOR
    }

    for(const boss in dangerZonePositions) {
        if (dangerZonePositions[boss].some((danger_zone_position, i) => 
            JSON.stringify(currentPosition) === JSON.stringify(danger_zone_position))) {
            return (col + offset) % 2 === 0 ? BOSS_SQUARE_COLORS[boss][1] : BOSS_SQUARE_COLORS[boss][0]
        }
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

const determineColor = (row, col, isBaronActive) => {
    const offset = row % 2
    const currentPosition = [row, col]

    const dangerZonePositions = getBossDangerZonePositions(isBaronActive)
    
    for(const boss in dangerZonePositions) {
        if (dangerZonePositions[boss].some((danger_zone_position, i) => 
            JSON.stringify(currentPosition) === JSON.stringify(danger_zone_position))) {
            return (col + offset) % 2 === 0 ? BOSS_SQUARE_COLORS[boss][0] : BOSS_SQUARE_COLORS[boss][1]
        }
    }

    return (col + offset) % 2 === 0 ? GREEN_SQUARE_COLOR : WHITE_SQUARE_COLOR
}

export { 
    PLAYERS, 
    IMAGE_MAP, 
    BARON_NASHOR_POSITION,
    MAX_BOSS_HEALTH,
    getPossibleCaptures, 
    pickSide, 
    snakeToCamel, 
    determineBackgroundColor,
    determineColor, 
    capitalizeFirstLetter
};