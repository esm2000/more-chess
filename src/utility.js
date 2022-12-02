const PLAYERS = ["white", "black"]

const IMAGE_MAP = {
    blackBishop: require('./assets/pieces/black_bishop.png'),
    blackKing: require("./assets/pieces/black_king.png"),
    blackKnight: require("./assets/pieces/black_knight.png"),
    blackPawn: require("./assets/pieces/black_pawn.png"),
    blackPawn2: require("./assets/pieces/black_pawn_2.png"),
    blackPawn3: require("./assets/pieces/black_pawn_3.png"),
    blackQueen: require("./assets/pieces/black_queen.png"),
    blackRook: require("./assets/pieces/black_rook.png"),
    neutralDragon: require("./assets/pieces/neutral_dragon.png"),
    neutralBaronNashor: require('./assets/pieces/neutral_baron_nashor.gif'),
    neutralBoardHerald: require('./assets/pieces/neutral_board_herald.png'),
    whiteBishop: require('./assets/pieces/white_bishop.png'),
    whiteKing: require("./assets/pieces/white_king.png"),
    whiteKnight: require("./assets/pieces/white_knight.png"),
    whitePawn: require("./assets/pieces/white_pawn.png"),
    whitePawn2: require("./assets/pieces/white_pawn_2.png"),
    whitePawn3: require("./assets/pieces/white_pawn_3.png"),
    whiteQueen: require("./assets/pieces/white_queen.png"),
    whiteRook: require("./assets/pieces/white_rook.png"),
    stunned: require("./assets/statuses/stunned.png"),
    bishopDebuff: require("./assets/statuses/bishop_debuff.png"),
    swordInTheStone: require("./assets/sword_in_the_stone.png"),
    checkProtection: require("./assets/statuses/check_protection.png"),
    centerOfBoard: require("./assets/rules/center_of_board.png"),
    blackStart: require("./assets/rules/black_start.png"),
    neutralCombat1: require("./assets/rules/neutral_combat1.gif"),
    neutralCombat2: require("./assets/rules/neutral_combat2.gif"),
    normalPawnMovement: require("./assets/rules/normal_pawn_movement.gif"),
    normalPawnCombat: require("./assets/rules/normal_pawn_combat.gif"),
    buffedPawnCombat: require("./assets/rules/buff1_pawn_combat.gif"),
    knightMovement: require("./assets/rules/knight_movement.png"),
    knightLimits: require("./assets/rules/knight_limits.png"),
    rookMovementTurn0: require("./assets/rules/rook_movement_turn_0.png"),
    rookMovementTurn15: require("./assets/rules/rook_movement_turn_15.png"),
    rookMovementTurn20: require("./assets/rules/rook_movement_turn_20.png"),
    bishopMovement: require("./assets/rules/bishop_movement.png"),
    bishopStacksMovement: require("./assets/rules/bishop_stacks_movement.gif"),
    bishopStacksCapture: require("./assets/rules/bishop_stacks_capture.gif"),
    bishopEnergizedCapture: require("./assets/rules/bishop_energized_capture.gif"),
    bishopDebuffEx: require("./assets/rules/bishop_debuff.gif"),
    bishopCapture: require("./assets/rules/bishop_capture.gif"),
    queenMovement: require("./assets/rules/queen_movement.png"),
    queenStun: require("./assets/rules/queen_stun.gif"),
    kingMovement: require("./assets/rules/king_movement.png"),
    kingSwordInStoneCheckProtection: require("./assets/rules/sword_in_stone_check_protection.gif")
}

const GREEN_SQUARE_COLOR = "rgb(100, 133, 68)";
const WHITE_SQUARE_COLOR = "rgb(230, 233, 198)";
const DARK_GREEN_SQUARE_COLOR = "rgb(48, 64, 32)";
const DARK_WHITE_SQUARE_COLOR = "rgb(140, 143, 124)";
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

const getBossDangerZonePositions = (isDragonActive, isHeraldActive, isBaronActive) => {

    const bossDangerZonePositions = {}
    const DangerZonePositions = []

    const CURRENT_BOSS_POSITIONS = {}
    
    if (isDragonActive) {
        CURRENT_BOSS_POSITIONS["dragon"] = BOSS_POSITIONS.dragon
    } 
    
    if (isHeraldActive) {
        CURRENT_BOSS_POSITIONS["board_herald"] = BOSS_POSITIONS.board_herald
    }
    
    if (isBaronActive) {
        CURRENT_BOSS_POSITIONS["baron_nashor"] = BOSS_POSITIONS.baron_nashor
    } 

    for (let boss in CURRENT_BOSS_POSITIONS) {
        DangerZonePositions.push(CURRENT_BOSS_POSITIONS[boss])
        DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0] - 1, CURRENT_BOSS_POSITIONS[boss][1]])
        DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0] + 1, CURRENT_BOSS_POSITIONS[boss][1]])

        if (boss === "dragon") {
            DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0] - 1, CURRENT_BOSS_POSITIONS[boss][1] - 1])
            DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0], CURRENT_BOSS_POSITIONS[boss][1] - 1])
            DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0] + 1, CURRENT_BOSS_POSITIONS[boss][1] - 1])
        }

        if (boss.includes("nashor") || boss.includes("herald")) {
            DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0] - 1, CURRENT_BOSS_POSITIONS[boss][1] + 1])
            DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0], CURRENT_BOSS_POSITIONS[boss][1] + 1])
            DangerZonePositions.push([CURRENT_BOSS_POSITIONS[boss][0] + 1, CURRENT_BOSS_POSITIONS[boss][1] + 1])
        }
        

        bossDangerZonePositions[boss] = [...DangerZonePositions]
        DangerZonePositions.length = 0
    }
    
    return bossDangerZonePositions

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

const determineBackgroundColor = (row, col, positionInPlay, possibleCaptures, isDragonActive, isHeraldActive, isBaronActive, swordInTheStonePosition) => {
    const offset = row % 2
    const currentPosition = [row, col]
    let green = GREEN_SQUARE_COLOR
    let white = WHITE_SQUARE_COLOR

    const dangerZonePositions = getBossDangerZonePositions(isDragonActive, isHeraldActive, isBaronActive)
    
    if (row === 3 && col === 6) {
        console.log("possibleCaptures", possibleCaptures)
        console.log("currentPosition", currentPosition)
    }
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

    if ([[3, 3], [4, 3], [3, 4], [4, 4]].toString().includes([row, col].toString())) {
        green = DARK_GREEN_SQUARE_COLOR
        white = DARK_WHITE_SQUARE_COLOR
    }

    if (
        positionInPlay.toString() !== [null, null].toString() &&
        positionInPlay[0] === row &&
        positionInPlay[1] === col
    ) {
        green = GREEN_SELECTED_SQUARE_COLOR
        white = WHITE_SELECTED_SQUARE_COLOR
    }
    
    return (col + offset) % 2 === 0 ? white : green
}

const determineColor = (row, col, isDragonActive, isHeraldActive, isBaronActive) => {
    const offset = row % 2
    const currentPosition = [row, col]

    const dangerZonePositions = getBossDangerZonePositions(isDragonActive, isHeraldActive, isBaronActive)
    
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
    DRAGON_POSITION,
    BOARD_HERALD_POSITION,
    BARON_NASHOR_POSITION,
    MAX_BOSS_HEALTH,
    LIGHT_BLUE_SQUARE_COLOR,
    pickSide, 
    snakeToCamel, 
    determineBackgroundColor,
    determineColor, 
    capitalizeFirstLetter
};