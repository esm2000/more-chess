import { createContext, useContext, useEffect, useState } from "react"
import { PLAYERS, getPossibleCaptures } from '../utility';

const GameStateContext = createContext({
    turnCount: 0,
    positionInPlay: [null, null],
    boardState: [
        Array(8).fill(null),
        Array(8).fill(null),
        Array(8).fill(null),
        Array(8).fill(null),
        Array(8).fill(null),
        Array(8).fill(null),
        Array(8).fill(null),
        Array(8).fill(null)
    ],
    possibleMoves: [],
    possibleCaptures: [],
    capturedPieces: [],
    setTurnCount: () => {},
    setPositionInPlay: () => {},
    setBoardState: () => {},
    setPossibleCaptures: () => {},
    setCapturedPieces: () => {}
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
        setGameState({
            ...gameState, 
            positionInPlay: positionInPlay,
            possibleCaptures: getPossibleCaptures(gameState.boardState, gameState.possibleMoves)
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

    const initGameState = {
        turnCount: 0,
        // positionInPlay: [null, null],
        positionInPlay: [5, 2],
        boardState: [
            [{"type":"black_rook"}, {"type":"black_knight"}, {"type":"black_bishop", "energize_stacks": 0}, {"type":"black_queen"}, {"type":"black_king"}, {"type":"black_bishop", "energize_stacks": 100}, {"type":"black_king"}, {"type":"black_rook"}],
            [{"type":"black_pawn", "pawn_buff": 1}, {"type":"black_pawn", "pawn_buff": 1}, {"type":"black_pawn", "pawn_buff": 1}, null, {"type":"black_pawn", "pawn_buff": 1}, {"type":"black_pawn", "pawn_buff": 1}, {"type":"black_pawn", "pawn_buff": 1}, {"type":"black_pawn", "pawn_buff": 1}],
            [null, null, null, {"type":"black_pawn", "pawn_buff": 1}, null, null, null, null],
            [null, null, null, {"type":"black_pawn", "pawn_buff": 1}, null, null, null, {"type":"neutral_dragon"}],
            [{"type":"neutral_baron_nashor"}, null, null, null, null, null, null, null],
            [null, null, {"type":"white_knight"}, null, null, null, null, null],
            Array(8).fill({"type":"white_pawn", "pawn_buff": 2}),
            [{"type":"white_rook", "is_stunned": true}, {"type":"white_knight", "is_stunned": true}, {"type":"white_bishop", "energize_stacks": 50}, {"type":"white_queen"}, {"type":"white_king"}, {"type":"white_bishop", "energize_stacks": 15}, {"type":"white_king"}, {"type":"white_rook"}],
        ],
        // possibleMoves: [],
        possibleMoves: [[4, 2], [3, 2], [3, 3]],
        possibleCaptures: [],
        capturedPieces: {
            [PLAYERS[0]]: ["black_pawn", "black_rook", "neutral_board_herald"],
            [PLAYERS[1]]: ["white_bishop", "neutral_dragon", "neutral_baron_nashor"]
        }, 
        setTurnCount: setTurnCount,
        setPositionInPlay: setPositionInPlay,
        setBoardState: setBoardState,
        setPossibleCaptures: setPossibleCaptures,
        setCapturedPieces: setCapturedPieces
    }
    const [gameState, setGameState] = useState(initGameState);

    const [refreshInterval, setRefreshInterval] = useState(3000);
    
    const fetchGameState = () => {
        // retrieve gameState
        
        // and then setGameState()
        setGameState(initGameState)

        // update any fields not obtained from backend
        if (gameState.possibleMoves.length > 0) {
            gameState.setPossibleCaptures(getPossibleCaptures(gameState.boardState, gameState.possibleMoves))
        }
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
    }, [initGameState.turnCount])

    return(
        <GameStateContext.Provider value={gameState}>
            {children}
        </GameStateContext.Provider>
    )
}

export default GameStateContext;