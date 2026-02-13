# League of Chess - Developer Documentation

Last Updated: 2026-02-10

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Codebase Architecture](#codebase-architecture)
4. [Game Mechanics](#game-mechanics)
5. [Core Code Modules](#core-code-modules)
6. [Development Workflow](#development-workflow)
7. [Testing Strategy](#testing-strategy)
8. [Current Development Focus](#current-development-focus)
9. [Common Patterns and Conventions](#common-patterns-and-conventions)
10. [Maintaining This Document](#maintaining-this-document)

---

## Project Overview

**Project Name:** League of Chess

**Description:** Chess variant with MOBA-style mechanics (modified pieces, neutral monsters, buff systems). See [README.md](README.md) for full rules and roadmap.

**Current Development Status:** WORK IN PROGRESS.

- **Frontend:** ~75% complete - board, pieces, monsters, status effects, win/loss screens done; buff UI, shop rework, pawn exchange remaining.
- **Backend:** ~80% complete - core logic, move generation, check/checkmate, API done; finalizing monster buffs, maintainability.
- **Production:** ~30% complete - Dockerized; database docs, linting, Kubernetes deployment remaining.

---

## Technology Stack

**Backend:** Python 3.12, FastAPI 0.89.1, MongoDB/PyMongo 4.3.3, Uvicorn 0.20.0, Pytest 7.2.1, python-dotenv 0.21.1

**Frontend:** React 18.2.0, React DOM 18.2.0, React Scripts 5.0.1, Testing Library ^13.4.0

**Deployment:** Docker (multi-stage: node:current-alpine → nginx:alpine + Python venv), Nginx

---

## Codebase Architecture

### Directory Structure

```
more-chess/
├── backend/
│   ├── src/
│   │   ├── api.py               # FastAPI route definitions
│   │   ├── moves.py             # Core move generation
│   │   ├── database.py          # MongoDB connection
│   │   ├── log.py               # Logging
│   │   └── utils/               # Game logic utilities
│   │       ├── board_analysis.py
│   │       ├── castle_mechanics.py
│   │       ├── check_checkmate.py
│   │       ├── game_ending.py
│   │       ├── game_scoring.py
│   │       ├── game_state.py
│   │       ├── game_update_pipeline.py
│   │       ├── monsters.py
│   │       ├── moves_and_positions.py
│   │       ├── piece_mechanics.py
│   │       ├── queen_mechanics.py
│   │       ├── special_items.py
│   │       ├── stun_mechanics.py
│   │       └── validation.py
│   ├── tests/
│   │   ├── unit/                # Unit tests (piece move generation)
│   │   ├── integration/         # Integration tests (full API flows)
│   │   └── test_utils.py
│   ├── mocks/                   # Test mock game states
│   ├── server.py                # Entry point
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React UI components
│   │   ├── context/GameStateContext.js  # Global state + API sync
│   │   ├── assets/              # Images (pieces, rules, statuses)
│   │   ├── index.js             # Entry point
│   │   └── utility.js           # Helper functions
│   └── package.json
│
├── Dockerfile
├── nginx.conf
├── run.sh
├── .env
└── README.md
```

### Key Modules

| Path | Purpose |
|------|---------|
| `backend/server.py` | FastAPI entry point |
| `backend/src/api.py` | REST API route definitions |
| `backend/src/moves.py` | Core move generation engine for all piece types |
| `backend/src/database.py` | MongoDB connection and CRUD operations |
| `backend/src/utils/game_update_pipeline.py` | Turn orchestration pipeline |
| `backend/src/utils/check_checkmate.py` | Check/checkmate/stalemate detection |
| `backend/src/utils/piece_mechanics.py` | Piece-specific rules (energize, Divine Right, etc.) |
| `backend/src/utils/monsters.py` | Neutral monster spawning, damage, buff application |
| `backend/src/utils/queen_mechanics.py` | Queen stun and turn reset logic |
| `backend/src/utils/validation.py` | API input validation |
| `frontend/src/index.js` | React entry point |
| `frontend/src/components/Board.js` | Main game board, piece interactions |
| `frontend/src/components/Piece.js` | Piece rendering, drag-and-drop, status effects |
| `frontend/src/context/GameStateContext.js` | Global state via React Context; handles API sync |
| `backend/tests/unit/` | Unit tests for move generation (isolated) |
| `backend/tests/integration/` | End-to-end API flow tests |
| `backend/mocks/` | Predefined game states for tests |

---

## Game Mechanics

> Full rules and examples are in README.md. This section summarizes mechanics for quick developer reference.

### Core Differences from Standard Chess

- Black starts with pawn on d6 (not d7) to balance white's first-move advantage
- Pieces cannot move past center file boundary (c3-c6-f6-f3) unless already in center
- Multiple pieces can occupy same square when a neutral monster is present
- If a neutral monster spawns on a King's square, that side loses immediately
- King can have Divine Right buff (prevents 1 check/checkmate instance)

### Piece-Specific Mechanics

#### Pawns
- Average piece value compared per team (excl. pawns): Knight/Bishop=3, Rook=5, Queen=9
- +2 avg point advantage: pawns can capture enemy pawns directly in front (not just diagonal)
- +3 avg point advantage: your pawns are immune to capture by enemy pawns

#### Knights
- Cannot jump over pieces; need clear L-shaped path to destination

#### Bishops
- Energize stacks: +5 per diagonal square moved, +10 per capture; max 100
- At 100 stacks: can capture by landing on any diagonally adjacent square
- Vulnerable: can be captured by landing on any of the 8 adjacent squares
- Marked-for-death: 3 stacks of being threatened by a bishop = instant kill

#### Rooks
- Starting range: 3 squares; formula: `range = 3 + floor((turn_count - 10) / 5)` for turns > 10

#### Queens
- Non-capture move: all adjacent enemy pieces are stunned for 1 turn
- On kill (when safe): queen gets another move immediately
- On assist (ally takes kill queen set up): queen gets another move

#### Kings
- Every 10 turns: Sword in the Stone spawns; King picks it up for Divine Right buff (prevents 1 check/checkmate)
- King earns +1 gold per enemy piece captured by allies
- King can buy pieces at starting square: Pawn=2g, Knight/Bishop=6g, Rook=10g (no Queens)

### Neutral Monsters

Universal mechanics: moving adjacent/onto a monster deals 1 damage; pieces staying adjacent >1 turn are destroyed; respawns if no damage for 3 turns.

#### Dragon
- Spawns every 10 turns on h4; permanent stacking buffs:
  1. Pawns +1 movement range
  2. All pieces deal 2 damage to monsters
  3. Ignore collision with ally pawns
  4. Ignore collision with all allies
  5. (Elder Dragon, 3 turns) Capture by adjacency; opponent chooses which piece dies

#### Board Herald
- Spawns turns 10 and 20 on a5; individual buff to capturing piece (permanent until captured)
- Adjacent ally pawns can capture 1 square directly forward

#### Baron Nashor
- Spawns every 15 turns after turn 20 on a5; 5-turn team-wide pawn buff:
  - Pawns can capture 1 square forward; pawns immune to enemy pawn capture
  - Negates enemy +3 advantage pawn immunity

---

## Core Code Modules

### Backend

| Module | Primary Responsibility | Key Functions |
|--------|----------------------|---------------|
| `src/api.py` | FastAPI routes | endpoints: game CRUD, buy_piece, moves |
| `src/moves.py` | Move generation engine | `get_moves`, `get_moves_for_*` (6 piece types) |
| `src/database.py` | MongoDB connection | exports `mongo_client` |
| `src/log.py` | Logging | exports `logger` |
| `utils/game_update_pipeline.py` | Turn orchestration | `prepare_game_update`, `apply_special_piece_effects`, `manage_turn_progression`, `validate_moves_and_pieces`, `handle_endgame_conditions` |
| `utils/piece_mechanics.py` | Piece-specific rules | `apply_bishop_energize_stacks_and_bishop_debuffs`, `apply_divine_right_to_kings`, `apply_marked_for_death_from_five_dragon_stacks` |
| `utils/check_checkmate.py` | Check/checkmate/stalemate | `is_in_check`, `is_checkmate`, `is_stalemate`, `trim_king_moves` |
| `utils/queen_mechanics.py` | Queen stun & turn reset | `apply_queen_stun`, `apply_queen_turn_reset` |
| `utils/monsters.py` | Monster spawn/damage/buffs | `spawn_neutral_monsters`, `damage_neutral_monsters`, `apply_neutral_monster_buffs` |
| `utils/validation.py` | API input validation | `is_valid_move`, `is_valid_piece_to_move`, `is_valid_piece_purchase` |
| `utils/castle_mechanics.py` | Castling validation | `can_castle_kingside`, `can_castle_queenside` |
| `utils/game_scoring.py` | Gold economy | awards +1g to King per ally capture |
| `utils/game_ending.py` | Win/loss/draw detection | sets `white_defeat`/`black_defeat` |
| `utils/game_state.py` | State schema init | default structure for new games |
| `utils/board_analysis.py` | Board analysis | `evaluate_current_position`, `get_neutral_monster_slain_position` |
| `utils/moves_and_positions.py` | Position helpers | bounds check, path clearance |
| `utils/special_items.py` | Shop/sword effects | sword pickup, piece purchase |
| `utils/stun_mechanics.py` | Stun tracking | `stunned_until` property; skips stunned pieces |

### Frontend

| Component | Primary Responsibility |
|-----------|----------------------|
| `src/index.js` | React entry point |
| `components/Board.js` | Game board; piece interactions, move highlighting |
| `components/Piece.js` | Piece rendering; drag-and-drop, buff indicators |
| `context/GameStateContext.js` | Global state + API sync; `updateGameState`, `fetchGameState` |
| `components/HUD,Shop,Buff,etc.` | UI areas (gold, shop, buffs, win/loss screens, rules) |
| `utility.js` | Shared helpers: `pickSide`, `snakeToCamel`, `BASE_API_URL` |

---

## Development Workflow

### Setup

**Prerequisites:** Python 3.12, Node.js (current), MongoDB, Docker (optional)

**.env file (project root):**
```bash
PYTHONPATH=backend
DB_HOST=your-mongodb-host
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password
```

**Install dependencies:**
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Running Locally

**Backend** (port 8080):
```bash
cd backend
python server.py
```

**Frontend** (port 3000):
```bash
cd frontend
npm start
```

### API Endpoints

- `POST /api/game` - Create new game
- `GET /api/game/{id}` - Retrieve game state
- `POST /api/game/{id}` - Update game state (submit move)
- `POST /api/buy_piece` - Purchase piece with gold
- `GET /api/moves` - Get legal moves for a piece
- `GET /` - Health check

### Testing

```bash
pytest                                          # all tests
pytest backend/tests/unit/                     # unit tests only
pytest backend/tests/integration/              # integration tests only
pytest -v -s -x -k "dragon"                    # verbose, print, stop-on-fail, filter
python3 -m compileall backend/src/ -q          # typecheck
```

### Docker Deployment

```bash
docker build . -t league-of-chess
docker run -p 80:80 -p 8080:8080 league-of-chess
```

Ports: `80` = frontend (Nginx), `8080` = backend (FastAPI). Requires `.env` at project root.

---

## Testing Strategy

The project maintains comprehensive test coverage using Pytest 7.2.1 as the testing framework. The test suite is organized into unit tests for isolated piece mechanics and integration tests for full API workflows, with a total of **121 test functions** across 18 test files.

### Test Organization

**Directory Structure:**
```
backend/tests/
├── unit/                    # Unit tests for move generation logic
│   ├── test_moves_pawn.py      # Pawn conditional movement and capture tests
│   ├── test_moves_knight.py    # Knight unit collision tests
│   ├── test_moves_bishop.py    # Bishop energize stacks and marked-for-death tests
│   ├── test_moves_rook.py      # Rook scaling range tests
│   ├── test_moves_queen.py     # Queen stun and turn reset tests
│   └── test_moves_king.py      # King movement and Divine Right tests
├── integration/             # Integration tests for full game flows
│   ├── conftest.py            # Pytest fixtures (game setup, teardown)
│   ├── test_database.py       # MongoDB CRUD operations
│   ├── test_api_game_states.py       # Game creation and state retrieval
│   ├── test_api_basic_gameplay.py    # Basic piece movement and capture
│   ├── test_api_pawn_mechanics.py    # Pawn advantage mechanics
│   ├── test_api_bishop_mechanics.py  # Bishop energize and vulnerability
│   ├── test_api_queen_mechanics.py   # Queen stun and reset mechanics
│   ├── test_api_castling.py          # Castling validation
│   ├── test_api_check_and_checkmate.py # Check, checkmate, stalemate
│   ├── test_api_neutral_monsters.py  # Monster spawning and buff application
│   ├── test_api_piece_buying.py      # Gold economy and piece purchases
│   └── test_api_special_items.py     # Special items (Sword in the Stone)
└── test_utils.py            # Shared test utilities (move helpers, assertions)
```

### Unit Tests - Piece Mechanics

**Purpose:** Test individual piece move generation in isolation without API overhead.

**Approach:**
- Uses `mocks/empty_game.py` for clean board state initialization
- Tests move generation functions directly from `src/moves.py`
- Focuses on edge cases and piece-specific mechanics
- No database or API layer involved

**Coverage (6 test files):**
1. **test_moves_pawn.py** - Pawn movement, diagonal captures, conditional movement (+2/+3 advantage), immunity to enemy pawns
2. **test_moves_knight.py** - L-shaped movement, unit collision (no jumping), path blocking
3. **test_moves_bishop.py** - Diagonal movement, energize stack accumulation (5/square, 10/capture), marked-for-death debuff (3 stacks), vulnerability (adjacent captures), 100-stack range extension
4. **test_moves_rook.py** - Straight-line movement, scaling range by turn count (3 base, +1 every 5 turns after turn 10)
5. **test_moves_queen.py** - Omnidirectional movement, stun ability (adjacent enemies after non-capture moves), turn reset on kill/assist
6. **test_moves_king.py** - Single-square movement, castle detection, Divine Right buff pickup, gold economy

**Example Test Pattern:**
```python
import copy
import src.moves as moves
from mocks.empty_game import empty_game

def test_pawn_movement():
    curr_game_state = copy.deepcopy(empty_game)
    curr_game_state["board_state"][3][3] = [{"type": "white_pawn"}]

    prev_game_state = copy.deepcopy(curr_game_state)
    result = moves.get_moves(curr_game_state, prev_game_state, 3, 3)

    assert [4, 3] in result["possible_moves"]
```

### Integration Tests - Full API Flows

**Purpose:** Validate end-to-end gameplay scenarios through the API layer.

**Approach:**
- Uses `mocks/starting_game.py` for standard chess starting position
- Tests API endpoints from `src/api.py` via FastAPI test client
- Validates game state updates, database persistence, and multi-turn interactions
- Uses helper functions from `test_utils.py` for common operations

**Coverage (12 test files):**
1. **test_database.py** - MongoDB connection, game creation, state retrieval, update operations
2. **test_api_game_states.py** - Game initialization, state persistence, turn progression
3. **test_api_basic_gameplay.py** - Standard piece movement, captures, turn order
4. **test_api_pawn_mechanics.py** - Average piece value calculation, +2 advantage (forward capture), +3 advantage (immunity)
5. **test_api_bishop_mechanics.py** - Energize stack accumulation across turns, marked-for-death progression (1→2→3 stacks), adjacent vulnerability, 100-stack instant capture
6. **test_api_queen_mechanics.py** - Stun application (adjacent enemies), turn reset on kill (safety check), turn reset on assist
7. **test_api_castling.py** - Kingside castle, queenside castle, castle prevention (check, path blocked, pieces moved)
8. **test_api_check_and_checkmate.py** - Check detection, checkmate validation, stalemate detection, Divine Right interaction
9. **test_api_neutral_monsters.py** - Dragon spawn (every 10 turns on h4), Board Herald spawn (turns 10, 20 on a5), Baron Nashor spawn (every 15 turns after turn 20), health tracking, damage mechanics, buff application (dragon stacks 1-5, herald individual buff, baron team buff)
10. **test_api_piece_buying.py** - Gold accumulation (King +1 per ally kill), piece purchase validation (cost, spawning), shop mechanics (King on starting square)
11. **test_api_special_items.py** - Sword in the Stone spawn (every 10 turns), Divine Right pickup (King only), buff consumption (prevents 1 check/checkmate)
12. **conftest.py** - Pytest fixtures for game setup, teardown, and common test data

**Example Integration Test Pattern:**
```python
import copy
from fastapi import Response
import pytest
from mocks.starting_game import starting_game
import src.api as api
from tests.test_utils import select_and_move_white_piece

def test_spawn_monsters(game):
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 9
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)

    assert game["board_state"][4][7][0]["type"] == "neutral_dragon"
    assert game["board_state"][3][0][0]["type"] == "neutral_board_herald"
```

### Mock Game States

**Location:** `backend/mocks/`

**Purpose:** Provide consistent, predefined game states for reproducible testing.

**Available Mocks:**
1. **empty_game.py** - Clean 8x8 board with no pieces, default game state values. Used for unit tests to isolate piece mechanics.
2. **starting_game.py** - Standard chess starting position with League of Chess modifications (black pawn on d6). Used for integration tests to simulate real gameplay.

**Mock Structure:** Each mock exports a Python dictionary matching the `GameState` Pydantic model schema:
- `board_state` - 8x8 array (empty arrays or piece objects)
- `turn_count` - Turn number (0 for starting games)
- `gold_count`, `captured_pieces`, `check`, `defeat` flags - All initialized
- Neutral monster states, buff tracking, castle log - All default values

### Test Utilities

**Location:** `backend/tests/test_utils.py`

**Purpose:** Shared helper functions to reduce test boilerplate and improve readability.

**Key Utilities:**
- `select_white_piece()`, `select_black_piece()` - Piece selection API calls
- `move_white_piece()`, `move_black_piece()` - Piece movement API calls
- `select_and_move_white_piece()`, `select_and_move_black_piece()` - Combined select + move operations
- Custom assertions for game state validation

**Example Usage:**
```python
from tests.test_utils import select_and_move_white_piece

game = select_and_move_white_piece(
    game=game,
    from_row=6, from_col=4,  # e2
    to_row=4, to_col=4       # e4
)
```

### Current Test Focus

The test suite currently emphasizes:

**Well-Covered Areas:**
- ✅ Piece move generation (all 6 piece types with special mechanics)
- ✅ Neutral monster mechanics (Dragon, Board Herald, Baron Nashor)
- ✅ Buff systems (energize stacks, marked-for-death, dragon stacks, baron/herald buffs)
- ✅ Check, checkmate, and stalemate detection
- ✅ Castling validation (kingside, queenside, prevention cases)
- ✅ Gold economy and piece buying
- ✅ Queen stun and turn reset mechanics
- ✅ Pawn advantage mechanics (+2/+3 value differences)

**Active Development (Recent Focus):**
- Dragon buff implementation and validation (5 stacking buffs)
- Marked-for-death mechanics (bishop 3-stack system, 5-dragon-stack team system)
- Baron Nashor buff application (team-wide pawn enhancements)
- Stalemate detection edge cases

**Areas for Expansion:**
- Frontend component testing (currently minimal React Testing Library usage)
- End-to-end browser testing (no Selenium/Playwright tests yet)
- Performance testing (no load tests for concurrent games)
- Visual regression testing (no screenshot comparison)

### Running Tests

See [Development Workflow - Testing](#testing) section for detailed commands on running tests, including:
- Running all tests: `pytest`
- Running specific suites: `pytest backend/tests/unit/` or `pytest backend/tests/integration/`
- Running specific files or functions
- Test output options (`-v`, `-s`, `-x`, `-k`)

### Test Quality Metrics

- **Total Tests:** 121 test functions
- **Test Files:** 18 files (6 unit, 12 integration/support)
- **Coverage Focus:** Backend game logic (100% of core mechanics tested)
- **Test Execution Time:** ~5-10 seconds for full suite (fast feedback loop)
- **Test Isolation:** Each test uses fresh game state from mocks (no shared state)
- **Continuous Validation:** Pytest runs in Docker build (stage 5) to prevent broken deployments

---

## Current Development Focus

This section provides context on active development work, recent commits, and current priorities to help developers understand where the project stands and what's being worked on.

### Active Development Branch

**Primary Development Branch:** `backend/neutral_monster_buffs`

This branch contains the most recent active development work focused on neutral monster buff implementation, marked-for-death mechanics validation, and stalemate detection fixes. The branch is ahead of `main` by 10 commits as of 2026-02-10.

**Current Branch (Documentation):** `ralph/claude-md-documentation`

This branch is focused on creating comprehensive Claude.md documentation for improved AI-assisted development.

### Recent Development Work

The project has seen significant progress in finalizing neutral monster buff mechanics and edge case handling:

**Latest Commits on `backend/neutral_monster_buffs` Branch:**

1. **Stalemate Detection Fix** (commit bc37527d) - Fixed stalemate detection logic to correctly identify the side to move and only detect stalemate when no non-king pieces have legal moves. This addresses edge cases where stalemate was incorrectly triggered.

2. **Marked-for-Death Validation** (commits de23a146, ac63260a, db281943, 2b639ea3) - Comprehensive validation of the marked-for-death mechanic including:
   - Single piece marked-for-death capture flow
   - Multiple pieces marked-for-death capture flow
   - Turn reset interaction with marked-for-death pieces
   - Mandatory piece surrender when all pieces are marked
   - Surrendering marked pieces while in check

3. **Baron Nashor Buff Validation** (commit 0e770556) - Validated that Kings are correctly placed in check when positioned in front of a pawn with Baron Nashor buff (which allows pawns to capture pieces directly in front).

4. **Pawn Advantage Mechanic Fix** (commit 09735c44) - Fixed capture point advantage calculation to use average piece value of remaining board pieces per README rules, ensuring pawn mechanics (+2/+3 advantage) work as intended.

5. **Turn Skip Edge Cases** (commits 3565a18a, b86a6676) - Validated realistic scenarios involving turn skips from all pieces being stunned, ensuring game state remains valid.

**Latest Commits on `main` Branch:**

1. **UI Documentation Update** (commit 7899494f) - Updated frontend README TODO list to account for new neutral monster buff UI requirements.

2. **Code Refactoring** (commits c2ffc2576, cf48c791) - Broke down `update_game_state()` function for better maintainability and improved exception handling for determining moved pieces.

3. **Test Stability** (commit 3487c7a0) - Fixed intermittent test failures caused by Sword in the Stone spawning in unpredictable locations.

### Current Roadmap Status

**Frontend Progress: ~75% Complete**
- ✅ Complete: Board, pieces, neutral monsters, status effects, win/loss screens, rules modal, shop interface
- 🔄 In Progress: Neutral monster buff UI enhancements (color tint + number indicators for stacked buffs)
- 📋 Remaining: Shop rework, pawn exchange UI, visual cues for turn skips/resets, piece deselection, draw UI

**Backend Progress: ~80% Complete**
- ✅ Complete: Core game logic, move generation for all pieces, check/checkmate detection, neutral monster spawning/damage, most buff systems, API endpoints
- 🔄 In Progress: Neutral monster buff validation (dragon stacks, marked-for-death mechanics), edge case handling
- 📋 Remaining: Final shop/pawn exchange logic, code refactoring for maintainability, AI opponent implementation

**Production Progress: ~30% Complete**
- ✅ Complete: Docker containerization, multi-stage build, basic deployment structure
- 📋 Remaining: Database setup documentation, code cleanup and refactoring, linting, Kubernetes deployment scripts, production deployment

### Current Priorities

Based on the roadmap and recent commit activity, the current development priorities are:

1. **Finalize Neutral Monster Buff Implementation** (Active) - Complete validation and testing of all dragon stack mechanics, marked-for-death systems (both bishop 3-stack and 5-dragon-stack), and Baron/Herald buff interactions.

2. **Improve Code Maintainability** (Active) - Continue refactoring large functions like `update_game_state()` and improving error handling throughout the codebase.

3. **Complete Frontend Buff Visualization** (Next Priority) - Implement UI indicators for neutral monster buffs (color tints, stack numbers, buff icons) to provide clear visual feedback to players.

4. **Shop and Pawn Exchange Finalization** (Upcoming) - Complete both backend logic and frontend UI for shop mechanics and pawn promotion.

5. **Production Readiness** (Future) - Code cleanup, linting, comprehensive testing, database documentation, and deployment preparation.

### Development Context

**Testing Focus:** Recent development has emphasized comprehensive integration testing for edge cases, particularly around:
- Stalemate detection with various board states
- Marked-for-death mechanics with multiple pieces
- Turn reset interactions with queen mechanics
- Baron Nashor buff interactions with check/checkmate

**Code Quality Focus:** Ongoing effort to break down large functions (300+ lines) into smaller, more maintainable modules while maintaining test coverage.

**Branch Strategy:** Feature branches for major work (`backend/neutral_monster_buffs`), with periodic merges to `main` after thorough testing.

---

## Common Patterns and Conventions

This section documents recurring code patterns, conventions, and best practices used throughout the project. Understanding these patterns helps maintain consistency and reduce cognitive load when working on the codebase.

### Game State Structure

The game state is the central data structure that represents the complete state of a chess game at any point in time. It follows a consistent schema across both backend (Python dict) and frontend (JavaScript object).

**Core Structure:**

```python
game_state = {
    "turn_count": 0,                    # Current turn number
    "position_in_play": [None, None],   # [row, col] of selected piece
    "board_state": [                    # 8x8 array of piece arrays
        [[{"type": "white_pawn"}], [], ...],  # Each cell is array of piece objects
        ...
    ],
    "possible_moves": [[row, col], ...],            # Legal move positions
    "possible_captures": [[[r1,c1], [r2,c2]], ...], # [move_to, capture_at] pairs
    "captured_pieces": {"white": [], "black": []},   # Graveyard
    "gold_count": {"white": 0, "black": 0},         # Player gold balances
    "check": {"white": False, "black": False},       # Check status
    "black_defeat": False,              # Game ending flags
    "white_defeat": False,
    "sword_in_the_stone_position": None,  # [row, col] or None
    "capture_point_advantage": None,    # Average piece value difference
    "bishop_special_captures": [],      # Bishop marked-for-death targets
    "latest_movement": {},              # Last move metadata
    "queen_reset": False,               # Queen turn reset flag
    "neutral_attack_log": {},           # Monster damage tracking
    "castle_log": {                     # Castling eligibility
        "white": {"has_king_moved": False, "has_left_rook_moved": False, "has_right_rook_moved": False},
        "black": {"has_king_moved": False, "has_left_rook_moved": False, "has_right_rook_moved": False}
    }
}
```

**Key Conventions:**
- `board_state` is indexed as `board_state[row][col]`, where row 0 is black's back rank and row 7 is white's back rank
- Each board cell is an **array** of piece objects (allows multiple pieces on same square for neutral monsters)
- Piece objects have mandatory `type` field (e.g., `"white_pawn"`, `"neutral_dragon"`) and optional fields for buffs/debuffs
- Positions are always `[row, col]` format (never col, row)
- Color strings are always lowercase: `"white"`, `"black"`, `"neutral"`

### MongoDB Document Format

Game states are persisted in MongoDB with minimal modifications to the in-memory structure.

**Database Schema:**

```python
# Collection: "games" in "game_db" database
{
    "_id": ObjectId("..."),           # MongoDB auto-generated ID
    "turn_count": 0,
    "board_state": [...],
    # ... all game_state fields ...
    "last_updated": datetime.datetime.now()  # Timestamp for debugging
}
```

**CRUD Patterns:**

```python
# Create (api.py:create_game)
game_database = mongo_client["game_db"]
game_database["games"].insert_one(game_state)
game_state["id"] = str(game_state.pop("_id"))  # Convert ObjectId to string for API response

# Read (api.py:retrieve_game_state)
game_database = mongo_client["game_db"]
game_state = game_database["games"].find_one({"_id": ObjectId(id)})
if not game_state:
    raise HTTPException(status_code=404, detail="Game not found")
game_state["id"] = str(game_state.pop("_id"))

# Update (api.py:update_game_state)
game_database["games"].replace_one(
    {"_id": ObjectId(id)},
    new_game_state
)
```

**Key Conventions:**
- MongoDB `_id` field is converted to string `id` field when returning to frontend
- `last_updated` timestamp is added on create/update for debugging
- Replace operations use `replace_one()` not `update_one()` to avoid partial updates
- Always use `ObjectId(id)` for query filters

### API Request/Response Cycle

The frontend-backend communication follows a consistent pattern for all game state updates.

**Request Flow:**

1. **Frontend initiates update** - User moves piece or performs action
2. **Frontend sends PUT request** - `PUT /api/game/{id}` with full game state (snake_case)
3. **Backend validates state** - Runs through game_update_pipeline checks
4. **Backend persists state** - Saves to MongoDB
5. **Backend returns updated state** - Responds with full game state (snake_case)
6. **Frontend updates context** - Converts to camelCase and updates React context

**Example Frontend Pattern (GameStateContext.js):**

```javascript
const updateGameState = (gameState) => {
    const gameStateId = sessionStorage.getItem("gameStateId")

    fetch(`${BASE_API_URL}/api/game/${gameStateId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(convertKeysToSnakeCase(gameState))
    })
    .then(response => {
        if (!response.ok) throw new Error(`Request failed: ${response.status}`)
        return response.json();
    })
    .then(jsonResponse => {
        const parsedResponse = {
            ...convertKeysToCamelCase(jsonResponse),
            updateGameState: updateGameState
        }
        setGameState(parsedResponse)
    })
    .catch(exception => console.log(exception));
}
```

**Example Backend Pattern (api.py):**

```python
@router.put("/game/{id}", status_code=200)
def update_game_state(id, state: GameState, response: Response):
    # Pipeline orchestration
    old_game_state, new_game_state, moved_pieces = prepare_game_update(id, state, retrieve_game_state)
    if old_game_state.get("black_defeat") or old_game_state.get("white_defeat"):
        return old_game_state  # Game already ended

    is_valid = apply_special_piece_effects(old_game_state, new_game_state, moved_pieces)
    is_valid, should_increment = manage_turn_progression(...)
    is_valid = validate_moves_and_pieces(...)
    # ... more pipeline stages ...

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid game state")

    # Persist and return
    game_database["games"].replace_one({"_id": ObjectId(id)}, new_game_state)
    new_game_state["id"] = str(new_game_state.pop("_id"))
    return new_game_state
```

**Key Conventions:**
- Frontend always sends **full game state**, not just the changed fields
- Backend validates **entire pipeline** before persisting (all-or-nothing)
- Use `convertKeysToSnakeCase()` when sending, `convertKeysToCamelCase()` when receiving
- Game state ID stored in `sessionStorage.getItem("gameStateId")`
- Always check for game ending conditions before processing updates

### Error Handling and Logging

The project uses consistent error handling and logging patterns across backend modules.

**Logging Pattern (log.py):**

```python
import logging
from src.log import logger

# Usage examples
logger.debug("Detailed debug information")
logger.info("General information about game state")
logger.error(f"Error occurred: {exception_message}")
```

**Error Handling in game_update_pipeline.py:**

```python
try:
    moved_pieces = utils.determine_pieces_that_have_moved(
        new_game_state["board_state"], old_game_state["board_state"]
    )
except Exception as e:
    logger.error(f"Unable to determine pieces that have moved: {e}")
    raise HTTPException(status_code=400, detail=utils.INVALID_GAME_STATE_ERROR_MESSAGE)
```

**Validation Pattern (utils/validation.py):**

```python
# Validation functions return boolean flags
is_valid_game_state = True

is_valid_game_state = utils.check_to_see_if_more_than_one_piece_has_moved(
    old_game_state, new_game_state, moved_pieces, capture_positions, is_valid_game_state
)

is_valid_game_state = utils.invalidate_game_if_stunned_piece_moves(
    moved_pieces, is_valid_game_state
)

# Final check
if not is_valid_game_state:
    raise HTTPException(status_code=400, detail=utils.INVALID_GAME_STATE_ERROR_MESSAGE)
```

**Key Conventions:**
- Use `logger.error()` for validation failures and exceptions
- Validation functions take `is_valid_game_state` boolean flag and return updated flag
- All validation errors use `HTTPException(status_code=400, detail=...)`
- Common error messages defined as constants in `utils/__init__.py`
- Never silently fail - always log and raise exceptions for invalid states

### Frontend-Backend Communication

The project uses specific naming conventions and conversion utilities to bridge JavaScript and Python naming styles.

**Case Conversion Pattern:**

```javascript
// utility.js - Converts between snake_case and camelCase

// Backend to Frontend
convertKeysToCamelCase({
    "turn_count": 10,
    "board_state": [...],
    "captured_pieces": {...}
})
// Returns: {turnCount: 10, boardState: [...], capturedPieces: {...}}

// Frontend to Backend
convertKeysToSnakeCase({
    turnCount: 10,
    boardState: [...],
    capturedPieces: {...}
})
// Returns: {"turn_count": 10, "board_state": [...], "captured_pieces": {...}}
```

**Piece Type Naming:**
- Backend: `"white_pawn"`, `"black_king"`, `"neutral_dragon"` (snake_case with color prefix)
- Frontend: Same format maintained (JavaScript objects preserve Python naming)
- Image mapping: `whitePawn`, `blackKing`, `neutralDragon` (camelCase for JavaScript keys)

**API Base URL Configuration (utility.js):**

```javascript
var BASE_API_URL
if (process.env.REACT_APP_LOCAL === "true") {
    BASE_API_URL = "http://0.0.0.0:8080";  // Local development
} else {
    var current_link = window.location.href
    // Production: derive from current window location
    if (current_link === 'http://0.0.0.0:3000') {
        current_link = 'http://0.0.0.0:8080'
    }
    BASE_API_URL = current_link
}
```

**Key Conventions:**
- Backend uses `snake_case` for all keys (Python PEP 8 standard)
- Frontend uses `camelCase` for JavaScript variables and state (JavaScript convention)
- Conversion happens at API boundary in `GameStateContext.js`
- Game state ID persisted in browser `sessionStorage` for session continuity
- CORS configured to accept `localhost:3000`, `localhost:8080`, `0.0.0.0` variants

### Move Generation Pattern

Move generation follows a consistent structure across all piece types in `src/moves.py`.

**Standard Return Format:**

```python
def get_moves(old_game_state, new_game_state, curr_position, piece):
    # Returns dictionary with 4 keys
    return {
        "possible_moves": [[row, col], ...],              # Legal non-capture moves
        "possible_captures": [[[r1,c1], [r2,c2]], ...],  # [move_to, capture_at] pairs
        "threatening_move": [[row, col]],                 # Positions threatening enemy king
        "castle_moves": [[row, col]]                      # Castle destination squares
    }
```

**Piece-Specific Function Pattern:**

```python
def get_moves_for_pawn(curr_game_state, prev_game_state, curr_position):
    possible_moves = []
    possible_captures = []
    threatening_move = []

    # 1. Determine piece color and direction
    piece = curr_game_state["board_state"][curr_position[0]][curr_position[1]][0]
    side = "white" if "white" in piece["type"] else "black"
    direction = 1 if side == "white" else -1

    # 2. Generate base moves
    # ... movement logic ...

    # 3. Apply special mechanics (buffs, debuffs, etc.)
    # ... special rules ...

    # 4. Return standardized dictionary
    return {
        "possible_moves": possible_moves,
        "possible_captures": possible_captures,
        "threatening_move": threatening_move,
        "castle_moves": []
    }
```

**Key Conventions:**
- All move generation functions take `curr_game_state`, `prev_game_state`, `curr_position`
- Position format is always `[row, col]` not `(row, col)` or `{row, col}`
- `possible_captures` uses nested arrays: first element is where piece moves, second is what gets captured
- Empty arrays returned for unused keys (e.g., pawns return `[]` for `castle_moves`)
- Special mechanics (energize stacks, stun, etc.) applied in piece-specific functions
- File control restrictions (center boundary) checked in individual move generators

### Testing Patterns

The test suite follows consistent patterns for unit and integration tests.

**Unit Test Pattern (tests/unit/):**

```python
import copy
import src.moves as moves
from mocks.empty_game import empty_game

def test_piece_movement():
    # 1. Setup - Create clean game state
    curr_game_state = copy.deepcopy(empty_game)
    curr_game_state["board_state"][3][3] = [{"type": "white_pawn"}]

    # 2. Execute - Call move generation
    prev_game_state = copy.deepcopy(curr_game_state)
    result = moves.get_moves(curr_game_state, prev_game_state, 3, 3)

    # 3. Assert - Verify expected moves
    assert [4, 3] in result["possible_moves"]
```

**Integration Test Pattern (tests/integration/):**

```python
import copy
from fastapi import Response
from mocks.starting_game import starting_game
import src.api as api
from tests.test_utils import select_and_move_white_piece

def test_gameplay_scenario(game):  # game fixture from conftest.py
    # 1. Setup - Modify game state to specific turn
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 9
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    # 2. Execute - Perform moves via test helpers
    game = select_and_move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)

    # 3. Assert - Verify game state changes
    assert game["board_state"][4][7][0]["type"] == "neutral_dragon"
```

**Test Utility Helpers (tests/test_utils.py):**

```python
# Helpers reduce boilerplate and improve readability
select_and_move_white_piece(game, from_row, from_col, to_row, to_col)
select_and_move_black_piece(game, from_row, from_col, to_row, to_col)
```

**Key Conventions:**
- Unit tests use `mocks/empty_game.py` for isolated piece mechanics
- Integration tests use `mocks/starting_game.py` for realistic scenarios
- Always use `copy.deepcopy()` when modifying mock states
- Test utilities in `test_utils.py` for common operations (select, move, combined)
- Pytest fixtures defined in `conftest.py` for game setup/teardown
- Test function names follow `test_<description>` pattern for autodiscovery
- Use descriptive assertions with clear expected values

### Code Organization Principles

The codebase follows consistent organization principles across backend and frontend.

**Backend Module Organization:**
- **Single Responsibility:** Each utility module has one clear purpose (e.g., `queen_mechanics.py` only handles queen-specific logic)
- **Pipeline Pattern:** `game_update_pipeline.py` orchestrates all utility modules in defined order
- **Validation Separation:** All input validation in `validation.py`, not scattered in logic files
- **Mock Data Isolation:** Test mocks in `backend/mocks/`, never in production code paths

**Frontend Component Organization:**
- **Component Hierarchy:** Board.js → Piece.js → Buff.js (parent to child composition)
- **Context for State:** GameStateContext.js provides global state, no prop drilling
- **Utility Separation:** All helper functions in `utility.js`, not inline in components
- **Asset Organization:** Images grouped by type (`pieces/`, `rules/`, `statuses/`)

**Import Conventions:**

```python
# Backend imports - always absolute from src/
from src.log import logger
import src.moves as moves
from src.utils.game_update_pipeline import prepare_game_update
from mocks.starting_game import starting_game
```

```javascript
// Frontend imports - relative paths for components
import { GameStateContextData } from '../context/GameStateContext';
import { PLAYERS, BASE_API_URL, convertKeysToCamelCase } from '../utility';
import Piece from './Piece';
```

**Key Conventions:**
- Backend uses absolute imports from `src/` (enabled by `PYTHONPATH=backend` in .env)
- Frontend uses relative imports (`../` for parent directory navigation)
- Utility functions exported as named exports: `export { pickSide, snakeToCamel, ... }`
- Context uses default export: `export default GameStateContext`
- Constants in ALL_CAPS: `BASE_API_URL`, `PLAYERS`, `IMAGE_MAP`

---

## Maintaining This Document

This section provides guidelines for keeping Claude.md up-to-date as the project evolves. An accurate, current Claude.md ensures that Claude Code and other developers have the right context when working on the codebase.

### Why Maintain This Document

Claude.md serves as the primary context document for:
- **AI-assisted development** - Claude Code uses this file to understand the project without exploring the codebase repeatedly
- **Onboarding new developers** - Provides comprehensive project overview and patterns
- **Architectural decisions** - Documents the "why" behind design choices
- **Development efficiency** - Reduces ramp-up time when returning to the project after breaks

An outdated Claude.md can lead to incorrect assumptions, wasted effort, and misaligned implementations.

### When to Update

Update Claude.md in these scenarios:

#### 1. **Architectural Changes** (High Priority)
- Adding or removing major directories
- Changing frontend/backend separation
- Introducing new frameworks or libraries
- Modifying deployment architecture (Docker, Nginx config)
- **Update Sections:** 2 (Technology Stack), 3 (Codebase Architecture), 6 (Development Workflow)

#### 2. **New Game Mechanics** (High Priority)
- Adding new piece abilities or modifying existing ones
- Introducing new neutral monsters or buffs
- Changing game rules or win conditions
- Adding new special systems (items, shops, etc.)
- **Update Sections:** 4 (Game Mechanics), 5 (Core Code Modules), 9 (Common Patterns)

#### 3. **Major Code Refactoring** (Medium Priority)
- Renaming or splitting core modules (e.g., breaking up `moves.py`)
- Moving functions between files
- Changing utility module responsibilities
- Restructuring component hierarchy
- **Update Sections:** 3 (Codebase Architecture), 5 (Core Code Modules), 9 (Common Patterns)

#### 4. **Testing Strategy Changes** (Medium Priority)
- Adding new test suites or categories
- Changing test organization
- Introducing new testing tools (e.g., Playwright for E2E)
- Significant changes to mock data structure
- **Update Sections:** 7 (Testing Strategy)

#### 5. **Development Workflow Changes** (Medium Priority)
- New build processes or commands
- Changes to local setup requirements
- Docker configuration updates
- API endpoint additions or changes
- Environment variable changes
- **Update Sections:** 6 (Development Workflow)

#### 6. **Milestone Completion** (Regular Updates)
- Completing major features from the roadmap
- Merging feature branches to main
- Shifting development priorities
- Starting new epic work
- **Update Sections:** 8 (Current Development Focus)

#### 7. **Dependency Updates** (Low Priority, but Important)
- Upgrading major versions (React 18 → 19, Python 3.12 → 3.13)
- Adding new significant dependencies
- Changing database technology
- **Update Sections:** 2 (Technology Stack), 6 (Development Workflow)

### How to Update

Follow this process when updating Claude.md:

#### Step 1: Update the "Last Updated" Timestamp
```markdown
Last Updated: YYYY-MM-DD
```
Change the date at the top of the file to the current date whenever you make updates.

#### Step 2: Update Relevant Sections
Refer to the "When to Update" section above to identify which sections need changes. Common patterns:

**For New Features:**
1. Add mechanic description to **Section 4 (Game Mechanics)**
2. Document implementation files in **Section 5 (Core Code Modules)**
3. Update test coverage in **Section 7 (Testing Strategy)**
4. Update current focus in **Section 8 (Current Development Focus)**

**For Architecture Changes:**
1. Update directory structure in **Section 3 (Codebase Architecture)**
2. Update module descriptions in **Section 5 (Core Code Modules)**
3. Update patterns if conventions changed in **Section 9 (Common Patterns)**

**For Workflow Changes:**
1. Update commands and processes in **Section 6 (Development Workflow)**
2. Update setup requirements if dependencies changed
3. Update testing commands if test organization changed

#### Step 3: Update Cross-References
If you rename files or change structure:
1. Search for old file paths throughout the document
2. Update all references to use new paths
3. Update line counts if files grew/shrank significantly
4. Fix any broken internal links in the table of contents

#### Step 4: Verify Accuracy
Before committing changes:
- Read through updated sections to ensure they match the current codebase
- Test any commands you added or modified
- Verify file paths are correct
- Check that examples still work

### Update Triggers Checklist

Use this checklist when making changes to the project:

- [ ] **Added new game mechanic?** → Update Section 4 (Game Mechanics)
- [ ] **Created new utility module?** → Update Section 5 (Core Code Modules)
- [ ] **Changed directory structure?** → Update Section 3 (Codebase Architecture)
- [ ] **Added new dependency?** → Update Section 2 (Technology Stack)
- [ ] **Modified build/test process?** → Update Section 6 (Development Workflow)
- [ ] **Added new test suite?** → Update Section 7 (Testing Strategy)
- [ ] **Completed major feature?** → Update Section 8 (Current Development Focus)
- [ ] **Changed common pattern?** → Update Section 9 (Common Patterns)
- [ ] **Any update made?** → Update "Last Updated" timestamp at top

### Examples of Updates

#### Example 1: Adding a New Neutral Monster (e.g., "Elder Drake")

**Sections to Update:**
1. **Section 4 (Game Mechanics)** - Add new monster subsection under "Neutral Monsters"
   ```markdown
   #### Elder Drake (15 HP)

   **Spawn:** Every 20 turns after turn 40 on e4 square

   **Team-Wide Buff:** [description]
   ```

2. **Section 5 (Core Code Modules)** - Update `monsters.py` description if significant new logic added

3. **Section 7 (Testing Strategy)** - Add test coverage notes
   ```markdown
   - Elder Drake spawn mechanics (turns 60, 80, 100...)
   - Elder Drake buff application and duration
   ```

4. **Section 8 (Current Development Focus)** - Add to "Recent Development Work" or "Current Priorities"

5. **Last Updated** - Change date to current date

#### Example 2: Refactoring `moves.py` into Multiple Files

**Sections to Update:**
1. **Section 3 (Codebase Architecture)** - Update directory structure
   ```markdown
   ├── src/
   │   ├── moves/
   │   │   ├── __init__.py
   │   │   ├── pawn_moves.py
   │   │   ├── knight_moves.py
   │   │   ├── bishop_moves.py
   │   │   └── ...
   ```

2. **Section 5 (Core Code Modules)** - Replace single `moves.py` entry with multiple entries for new files

3. **Section 9 (Common Patterns)** - Update import patterns
   ```python
   from src.moves.pawn_moves import get_moves_for_pawn
   ```

4. **Last Updated** - Change date to current date

#### Example 3: Completing Neutral Monster Buffs Feature

**Sections to Update:**
1. **Section 1 (Project Overview)** - Update backend progress percentage (80% → 85%)

2. **Section 8 (Current Development Focus)** - Move from "Active Development" to "Recently Completed"
   ```markdown
   **Recently Completed:**
   - ✅ Neutral monster buff implementation (Dragon stacks 1-5, Baron/Herald buffs)
   - ✅ Marked-for-death mechanics (Bishop 3-stack, 5-dragon-stack systems)
   ```

3. **Section 8 (Current Development Focus)** - Update "Current Priorities" to reflect next focus area

4. **Last Updated** - Change date to current date

### Maintenance Best Practices

1. **Update incrementally** - Don't let changes accumulate. Update Claude.md in the same commit as the code change when possible.

2. **Be specific** - Use exact file paths, line counts, and version numbers. Vague descriptions reduce document usefulness.

3. **Keep examples current** - If code patterns change, update example code blocks to reflect new conventions.

4. **Remove obsolete information** - Delete sections about removed features rather than marking them as "deprecated."

5. **Test your updates** - If you document a command or workflow, actually run it to verify it works.

6. **Consider the AI audience** - Claude Code relies on this document for context. Write clearly and comprehensively.

7. **Use consistent formatting** - Follow existing markdown patterns for headers, code blocks, and lists.

### Who Should Update

**Primary Responsibility:** The developer making the code change should update Claude.md.

**Secondary Review:** During PR review, reviewers should verify that Claude.md updates are included if needed.

**Periodic Audits:** Every 2-3 months, conduct a full review of Claude.md against the current codebase to catch any drift.

### Quick Update Template

When making changes, use this template for commit messages:

```
Update Claude.md: [brief description]

- Updated Section X: [specific changes]
- Updated Section Y: [specific changes]
- Updated Last Updated timestamp
```

Example:
```
Update Claude.md: Document Elder Drake neutral monster

- Updated Section 4 (Game Mechanics): Added Elder Drake spawn/buff mechanics
- Updated Section 5 (Core Code Modules): Added Elder Drake implementation notes to monsters.py
- Updated Section 7 (Testing Strategy): Added Elder Drake test coverage
- Updated Section 8 (Current Development Focus): Added Elder Drake to recent work
- Updated Last Updated timestamp to 2026-02-15
```

---

**Document Version:** 1.0
**Last Comprehensive Review:** 2026-02-10
**Next Scheduled Review:** 2026-05-10 (3 months)
