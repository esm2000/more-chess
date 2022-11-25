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
    setTurnCount: () => {},
    setPositionInPlay: () => {},
    setBoardState: () => {},
    setPossibleCaptures: () => {}
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

    const initGameState = {
        turnCount: 0,
        // positionInPlay: [null, null],
        positionInPlay: [5, 2],
        boardState: [
            ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_king", "black_rook"],
            Array(8).fill("black_pawn"),
            Array(8).fill(null),
            [null, null, null, "black_pawn", null, null, null, "neutral_dragon"],
            Array(8).fill(null),
            [null, null, "white_knight", null, null, null, null, null],
            Array(8).fill("white_pawn"),
            ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_king", "white_rook"],
        ],
        // possibleMoves: [],
        possibleMoves: [[4, 2], [3, 2], [3, 3]],
        possibleCaptures: [],
        setTurnCount: setTurnCount,
        setPositionInPlay: setPositionInPlay,
        setBoardState: setBoardState,
        setPossibleCaptures: setPossibleCaptures
    }
    const [gameState, setGameState] = useState(initGameState);

    const [refreshInterval, setRefreshInterval] = useState(3000);
    
    const fetchGameState = () => {
        console.log("refresh")
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