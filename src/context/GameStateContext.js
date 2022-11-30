import { createContext, useContext, useEffect, useState } from "react"
import { PLAYERS } from '../utility';

const GameStateContext = createContext({
    turnCount: 0,
    positionInPlay: [null, null],
    boardState: [
        Array(8).fill([null]),
        Array(8).fill([null]),
        Array(8).fill([null]),
        Array(8).fill([null]),
        Array(8).fill([null]),
        Array(8).fill([null]),
        Array(8).fill([null]),
        Array(8).fill([null])
    ],
    possibleMoves: [],
    possibleCaptures: [],
    capturedPieces: [],
    SwordInTheStonePosition: null,
    isMobile: false,
    capturePointAdvantage: null,
    setTurnCount: () => {},
    setPositionInPlay: () => {},
    setBoardState: () => {},
    setPossibleCaptures: () => {},
    setCapturedPieces: () => {},
    setSwordInTheStonePosition: () => {},
    setIsMobile: () => {},
    setCapturePointAdvantage: () => {}
})

export function GameStateContextData() {
    return useContext(GameStateContext)
}

// https://medium.com/@isaac.hookom/auto-refresh-data-for-react-functional-components-5eda19f912d1
// https://mtm.dev/react-child-update-context
// state refreshes every 5 second

export function GameStateProvider({children}) {

    const setTurnCount = (turnCount) => {
        setGameState({...gameState, turnCount: turnCount})
    }

    const setPositionInPlay = (positionInPlay) => {
        // TODO API Call where you update the game via API and get the response to update possibleCaptures
        setGameState({
            ...gameState, 
            positionInPlay: positionInPlay,
            // possibleCaptures: getPossibleCaptures(gameState.boardState, gameState.possibleMoves)
        })
    }

    const setBoardState = (boardState) => {
        setGameState({...gameState, boardState: boardState})
    }

    const setPossibleCaptures = (possibleCaptures) => {
        setGameState({...gameState, possibleCaptures: possibleCaptures})
    }

    const setCapturedPieces = (capturedPieces) => {
        setGameState({...gameState, capturedPieces: capturedPieces})
    }

    const setSwordInTheStonePosition = (swordInTheStonePosition) => {
        setGameState({...gameState, swordInTheStonePosition: swordInTheStonePosition})
    }

    const setIsMobile = (isMobile) => {
        setGameState({...gameState, isMobile: isMobile})
    }

    const setCapturePointAdvantage = (capturePointAdvantage) => {
        setGameState({...gameState, capturePointAdvantage: capturePointAdvantage})
    }

    const initGameState = {
        turnCount: 0,
        // positionInPlay: [null, null],
        positionInPlay: [5, 2],
        boardState: [
            [[{"type":"black_rook"}], [{"type":"black_knight"}], [{"type":"black_bishop", "energize_stacks": 0}], [{"type":"black_queen"}], [{"type":"black_king"}], [{"type":"black_bishop", "energize_stacks": 100}], [{"type":"black_king"}], [{"type":"black_rook"}]],
            [[{"type":"black_pawn", "pawn_buff": 1}], [{"type":"black_pawn", "pawn_buff": 1}], [{"type":"black_pawn", "pawn_buff": 1}], null, [{"type":"black_pawn", "pawn_buff": 1}], [{"type":"black_pawn", "pawn_buff": 1}], [{"type":"black_pawn", "pawn_buff": 1}], [{"type":"black_pawn", "pawn_buff": 1}]],
            [null, null, null, [{"type":"black_pawn", "pawn_buff": 1}], null, null, null, null],
            [null, null, null, [{"type":"black_pawn", "pawn_buff": 1}], null, null, null, [{"type":"neutral_dragon", "health": 4}]],
            [[{"type":"neutral_baron_nashor", "health": 10}], null, null, null, null, null, null, null],
            [null, null, [{"type":"white_knight"}], null, null, null, null, null],
            Array(8).fill([{"type":"white_pawn", "pawn_buff": 2}]),
            [[{"type":"white_rook", "is_stunned": true}], [{"type":"white_knight", "is_stunned": true}], [{"type":"white_bishop", "energize_stacks": 50}], [{"type":"white_queen"}], [{"type":"white_king"}], [{"type":"white_bishop", "energize_stacks": 15}], [{"type":"white_knight", "bishop_debuff": 1}], [{"type":"white_rook", "bishop_debuff": 2}]],
        ],
        // possibleMoves: [],
        possibleMoves: [[4, 2], [3, 2], [3, 3]],
        possibleCaptures: [[3, 3]],
        capturedPieces: {
            [PLAYERS[0]]: ["black_pawn", "black_rook", "neutral_board_herald"],
            [PLAYERS[1]]: ["white_bishop", "neutral_dragon", "neutral_baron_nashor"]
        }, 
        swordInTheStonePosition: [4, 5],
        isMobile: window.matchMedia("(max-width: 1024px)").matches && window.matchMedia("(orientation: portrait)").matches,
        capturePointAdvantage: ["black", 4],
        setTurnCount: setTurnCount,
        setPositionInPlay: setPositionInPlay,
        setBoardState: setBoardState,
        setPossibleCaptures: setPossibleCaptures,
        setCapturedPieces: setCapturedPieces,
        setSwordInTheStonePosition: setSwordInTheStonePosition,
        setIsMobile: setIsMobile,
        setCapturePointAdvantage: setCapturePointAdvantage
    }
    const [gameState, setGameState] = useState(initGameState);

    const [refreshInterval, setRefreshInterval] = useState(3000);
    
    const fetchGameState = () => {
        // retrieve gameState
        
        // and then setGameState()
        setGameState(initGameState)

    }

    const updateIsMobile = () => {
        setIsMobile(window.matchMedia("(max-width: 1024px)").matches && window.matchMedia("(orientation: portrait)").matches)
    }

    useEffect(() => {
        // uncomment when backend is finished and remove uncommented fetchGameState() call
        // // setting refreshInterval to null can be used in a pause
        // if (refreshInterval) {
        //     const interval = setInterval(fetchGameState, refreshInterval)
        //     // when component is not being rendered stop refresh
        //     return () => clearInterval(interval)
        // }
        fetchGameState()
        window.addEventListener('resize', updateIsMobile)
    }, [initGameState.turnCount])

    return(
        <GameStateContext.Provider value={gameState}>
            {children}
        </GameStateContext.Provider>
    )
}

export default GameStateContext;