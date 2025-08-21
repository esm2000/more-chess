import { createContext, useContext, useEffect, useState } from "react"
import { PLAYERS, BASE_API_URL, convertKeysToCamelCase, convertKeysToSnakeCase } from '../utility';

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
    SwordInTheStonePosition: null,
    capturePointAdvantage: null,
    blackDefeat: false,
    whiteDefeat: false,
    goldCount: null,
    bishopSpecialCaptures: [],
    latestMovement: null,
    queenReset: false,
    check: {white: false, black: false},
    // TODO: for consistency add recursion to convertKeysToSnakeCase()
    castleLog: {
        white: {hasKingMoved: false, hasLeftRookMoved: false, hasRightRookMoved: false},
        black: {hasKingMoved: false, hasLeftRookMoved: false, hasRightRookMoved: false}
    },
    neutralBuffLog: {
        white: {dragon: {stacks:0, turn: 0}, boardHerald: false, baronNashor: false},
        black: {dragon: {stacks:0, turn: 0}, boardHerald: false, baronNashor: false}
    }
})

export function GameStateContextData() {
    return useContext(GameStateContext)
}

// https://medium.com/@isaac.hookom/auto-refresh-data-for-react-functional-components-5eda19f912d1
// https://mtm.dev/react-child-update-context
// state refreshes every 5 second

export function GameStateProvider({children}) {
    const updateGameState = (gameState) => {
        const gameStateId = sessionStorage.getItem("gameStateId")
        
        fetch(`${BASE_API_URL}/api/game/${gameStateId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(convertKeysToSnakeCase(gameState))
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Request failed with status code ${response.status}: ${response.statusText}`)
            }
            return response.json();
        })
        .then(jsonResponse => {
            const parsedJsonResponse = {
                ...convertKeysToCamelCase(jsonResponse), 
                updateGameState: updateGameState
            }
            setGameState(parsedJsonResponse)
        })
        .catch(exception => {
            console.log(exception);
        });
    }

    const initGameState = {
        initialState: true,
        turnCount: 0,
        positionInPlay: [null, null],
        boardState: [
            [[{"type":"black_pawn"}], [{"type":"black_knight"}], [{"type":"black_bishop", "energize_stacks": 0}], [{"type":"black_queen"}], [{"type":"black_king"}], [{"type":"black_bishop", "energize_stacks": 0}], [{"type":"black_knight"}], [{"type":"black_rook"}]],
            Array(8).fill([{"type":"black_pawn"}]),
            Array(8).fill(null),
            Array(8).fill(null),
            Array(8).fill(null),
            Array(8).fill(null),
            Array(8).fill([{"type":"white_pawn"}]),
            [[{"type":"white_rook"}], [{"type":"white_knight"}], [{"type":"white_bishop", "energize_stacks": 0}], [{"type":"white_queen"}], [{"type":"white_king"}], [{"type":"white_bishop", "energize_stacks": 0}], [{"type":"white_knight"}], [{"type":"white_rook"}]],
        ],
        possibleMoves: [],
        possibleCaptures: [],
        capturedPieces: {
            [PLAYERS[0]]: [],
            [PLAYERS[1]]: []
        }, 
        graveyard: [],
        swordInTheStonePosition: null,
        capturePointAdvantage: null,
        blackDefeat: false,
        whiteDefeat: false,
        goldCount: {
            [PLAYERS[0]]: 0,
            [PLAYERS[1]]: 0
        },
        bishopSpecialCaptures: [],
        latestMovement: {},
        queenReset: false,
        neutralAttackLog: {},
        check: {
            [PLAYERS[0]]: false,
            [PLAYERS[1]]: false
        },
        // for consistency add recursion to convertKeysToSnakeCase()
        castleLog: {
            white: {hasKingMoved: false, hasLeftRookMoved: false, hasRightRookMoved: false},
            black: {hasKingMoved: false, hasLeftRookMoved: false, hasRightRookMoved: false}
        },
        neutralBuffLog: {
        white: {dragon: {stacks:0, turn: 0}, boardHerald: false, baronNashor: false},
        black: {dragon: {stacks:0, turn: 0}, boardHerald: false, baronNashor: false}
    }
    }
    const [gameState, setGameState] = useState(initGameState);

    const [intervalTime, setIntervalTime] = useState(3000);
    
    const fetchGameState = () => {
        var url
        var method
        const gameStateId = sessionStorage.getItem("gameStateId")
        const lastUpdated = sessionStorage.getItem("lastUpdated")

        if (gameStateId == null) {
            url = `${BASE_API_URL}/api/game`
            method = "POST"
        } else {
            url = `${BASE_API_URL}/api/game/${gameStateId}`
            method = "GET"
        }
        
        const sixSecondsAgo = Date.now() - 6000;
        if (Date.parse(lastUpdated) < sixSecondsAgo) {
            return
        }

        fetch(url, {"method": method})
        .then(response => response.json())
        .then(result => {
            if (method === "POST") {
                console.log(`POST Game ID - ${result["id"]}`)
            } else {
                console.log(`GET Game ${result["id"]}`)
            }
            const parsedResult = {
                ...convertKeysToCamelCase(result), 
                updateGameState: updateGameState
            }
            setGameState(parsedResult)
            sessionStorage.setItem("gameStateId", parsedResult["id"])
            sessionStorage.setItem("lastUpdated", parsedResult["lastUpdated"])
        })
        .catch(exception => {
            console.log(exception);
        });
    }

    useEffect(() => {
        fetchGameState()
        
        const interval = setInterval(() => fetchGameState(), 3000)
        // when component is not being rendered stop refresh
        return () => {
            clearInterval(interval)
            sessionStorage.clear();
        }
    }, [])

    return(
        <GameStateContext.Provider value={gameState}>
            {children}
        </GameStateContext.Provider>
    )
}

export default GameStateContext;