import { createContext, useContext, useEffect, useState } from "react"

const GameStateContext = createContext({
    turnCount: 0,
    positionInPlay: [null, null],
    setTurnCount: () => {},
    setPositionInPlay: () => {}
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
        setGameState({...gameState, positionInPlay: positionInPlay})
    }

    const initGameState = {
        turnCount: 0,
        positionInPlay: [null, null],
        boardState: [
            ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_king", "black_rook"],
            Array(8).fill("black_pawn"),
            Array(8).fill(null),
            Array(8).fill(null),
            Array(8).fill(null),
            Array(8).fill(null),
            Array(8).fill("white_pawn"),
            ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_king", "white_rook"],
        ],
        setTurnCount: setTurnCount,
        setPositionInPlay: setPositionInPlay
    }
    const [gameState, setGameState] = useState(initGameState);

    const [refreshInterval, setRefreshInterval] = useState(3000);
    
    const fetchGameState = () => {
        console.log("refresh")
        // retrieve and then setGameState()
        setGameState(initGameState)
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