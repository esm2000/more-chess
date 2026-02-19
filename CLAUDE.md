# League of Chess - Developer Documentation

Last Updated: 2026-02-19

> **Keep this file current.** Update the relevant sections whenever you change game mechanics, add/rename modules, restructure directories, change dependencies, or shift development priorities. See [Maintaining This Document](#maintaining-this-document) for the update checklist.

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

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Primary backend language |
| FastAPI | 0.89.1 | Web framework for REST API |
| MongoDB | 4.3.3 | NoSQL database (via PyMongo) |
| Uvicorn | 0.20.0 | ASGI server |
| Pytest | 7.2.1 | Testing framework |
| python-dotenv | 0.21.1 | Environment variable management |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | ^18.2.0 | UI framework |
| React DOM | ^18.2.0 | React rendering |
| React Scripts | 5.0.1 | Build tooling (CRA) |
| Testing Library | ^13.4.0 | Component testing |

### Deployment

| Technology | Purpose |
|------------|---------|
| Docker | Multi-stage build (node:current-alpine → nginx:alpine + Python venv) |
| Nginx | Static file server for frontend |

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
- A player's piece and a neutral monster can occupy the same square simultaneously (player pieces cannot otherwise share squares)
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
- Bishop debuff (`bishop_debuff`): piece threatened by a bishop at turn end gains 1 stack; at 3 stacks the bishop can instantly capture it regardless of position

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

Universal mechanics: moving adjacent/onto a monster deals 1 damage; pieces staying adjacent >1 turn are destroyed; regenerates to full HP if no damage taken for 3 turns.

#### Dragon
- Spawns every 10 turns on h4; permanent stacking buffs:
  1. Pawns +1 movement range
  2. All pieces deal 2 damage to monsters
  3. Ignore collision with ally pawns
  4. Ignore collision with all allies
  5. (Elder Dragon, 3 turns) Marked-for-death: pieces can be captured by occupying an adjacent square; opponent chooses which threatened piece dies

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

**Backend** (port 8080, CORS accepts localhost:3000/8080 and 0.0.0.0 variants):
```bash
cd backend
python server.py
```

**Frontend** (port 3000, connects to backend at localhost:8080/api):
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
- `GET /` - Health check (returns "OK")

Request/response: JSON with `snake_case` keys (backend) ↔ `camelCase` (frontend, converted by `GameStateContext.js`).

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

`run.sh` entrypoint: starts Nginx, then Python backend. Build arg `LOCAL=true` (default) for dev, `LOCAL=false` for prod.

---

## Testing Strategy

212 test functions across 19 files. Unit tests use `mocks/empty_game.py` (isolated, no DB); integration tests use `mocks/starting_game.py` + FastAPI test client. `test_utils.py` provides `select_and_move_white/black_piece()` helpers.

### Test Coverage

| Test File | What It Covers |
|-----------|---------------|
| `unit/test_moves_pawn.py` | Pawn movement, +2/+3 advantage mechanics, immunity |
| `unit/test_moves_knight.py` | L-shape movement, unit collision (no jumping) |
| `unit/test_moves_bishop.py` | Energize stacks, marked-for-death, vulnerability |
| `unit/test_moves_rook.py` | Scaling range by turn count |
| `unit/test_moves_queen.py` | Stun ability, turn reset on kill/assist |
| `unit/test_moves_king.py` | Movement, castle detection, Divine Right, gold |
| `integration/test_database.py` | MongoDB CRUD operations |
| `integration/test_api_game_states.py` | Game creation, state persistence |
| `integration/test_api_basic_gameplay.py` | Standard movement, captures, turn order |
| `integration/test_api_pawn_mechanics.py` | Pawn advantage (+2/+3) via API |
| `integration/test_api_bishop_mechanics.py` | Energize stacks, marked-for-death, adjacency |
| `integration/test_api_queen_mechanics.py` | Stun and turn reset via API |
| `integration/test_api_castling.py` | Kingside/queenside castle, prevention cases |
| `integration/test_api_check_and_checkmate.py` | Check, checkmate, stalemate, Divine Right |
| `integration/test_api_neutral_monsters.py` | Dragon/Herald/Baron spawn, damage, buffs |
| `integration/test_api_piece_buying.py` | Gold economy, purchase validation |
| `integration/test_api_special_items.py` | Sword in the Stone, Divine Right buff |
| `integration/conftest.py` | Pytest fixtures for game setup/teardown |

### Running Tests

```bash
pytest                              # all tests
pytest backend/tests/unit/          # unit only
pytest backend/tests/integration/   # integration only
pytest -v -s -x -k "dragon"         # verbose, print, stop-on-fail, filter
```

### Test Quality Metrics

- **Total Tests:** 212 test functions (some tests are stubs awaiting implementation)
- **Test Files:** 18 files (6 unit, 12 integration/support)
- **Coverage Focus:** Backend game logic (100% of core mechanics tested)
- **Test Execution Time:** ~5-10 seconds for full suite (fast feedback loop)
- **Test Isolation:** Each test uses fresh game state from mocks (no shared state)
- **Continuous Validation:** Pytest runs in Docker build (stage 5) to prevent broken deployments

---

## Current Development Focus

### Active Development Area

Current focus: neutral monster buff implementation, marked-for-death mechanics validation, and stalemate detection edge cases. Check `git branch` for the current working branch.

### Recent Development Work

- Stalemate detection fix (side-to-move logic)
- Marked-for-death mechanic validation (bishop 3-stack, 5-dragon-stack)
- 5-dragon-stack marked-for-death adjacent capture implemented for all piece types
- Knight dragon buff path collision bug fix (or → and)
- Baron Nashor buff + check validation
- Pawn advantage calculation fix (average piece value)
- Turn skip edge cases (all pieces stunned)

### Current Roadmap Status

**Frontend ~75%:** ✅ Board, pieces, monsters, status effects, win/loss, rules, shop | 🔄 Monster buff UI | 📋 Shop rework, pawn exchange, visual cues

**Backend ~80%:** ✅ Core logic, move gen, check/checkmate, monsters, buffs, API | 🔄 Monster buff validation, edge cases | 📋 Shop/pawn exchange, refactoring, AI

**Production ~30%:** ✅ Docker, multi-stage build | 📋 DB docs, linting, Kubernetes

### Current Priorities

1. Finalize Neutral Monster Buff Implementation
2. Improve Code Maintainability
3. Complete Frontend Buff Visualization
4. Shop and Pawn Exchange Finalization
5. Develop CPU Opponent
6. Production Readiness

---

## Common Patterns and Conventions

### Game State Structure

```python
game_state = {
    "turn_count": 0,
    "position_in_play": [None, None],   # [row, col]
    "board_state": [[[{"type": "white_pawn"}], [], ...]],  # 8x8 array of piece arrays
    "possible_moves": [[row, col], ...],
    "possible_captures": [[[r1,c1], [r2,c2]], ...],  # [move_to, capture_at]
    "captured_pieces": {"white": [], "black": []},
    "gold_count": {"white": 0, "black": 0},
    "check": {"white": False, "black": False},
    "black_defeat": False, "white_defeat": False,
    "sword_in_the_stone_position": None,
    "capture_point_advantage": None,
    "bishop_special_captures": [],
    "queen_reset": False,
    "neutral_attack_log": {},
    "castle_log": {
        "white": {"has_king_moved": False, "has_left_rook_moved": False, "has_right_rook_moved": False},
        "black": {"has_king_moved": False, "has_left_rook_moved": False, "has_right_rook_moved": False}
    }
}
```

**Key Conventions:**
- `board_state[row][col]`: row 0 = black's back rank, row 7 = white's back rank
- Each cell is an **array** of piece objects (supports monster co-occupancy)
- Piece objects have mandatory `type` (e.g., `"white_pawn"`) and optional buff fields
- Positions always `[row, col]`; colors always lowercase (`"white"`, `"black"`, `"neutral"`)

### MongoDB Document Format

**Key Conventions:**
- Collection: `"games"` in `"game_db"`; `_id` converted to string `id` for API responses
- Use `replace_one()` not `update_one()`; always use `ObjectId(id)` for queries

### API Request/Response Cycle

**Key Conventions:**
- Frontend always sends **full game state**; backend validates entire pipeline before persisting
- `convertKeysToSnakeCase()` sending, `convertKeysToCamelCase()` receiving
- Game state ID in browser `sessionStorage`

### Error Handling and Logging

**Key Conventions:**
- `logger.error()` for failures; validation functions pass `is_valid_game_state` bool flag
- All validation errors: `HTTPException(status_code=400, ...)`
- Error message constants in `utils/__init__.py`; never silently fail

### Frontend-Backend Communication

**Key Conventions:**
- Backend: `snake_case`; Frontend: `camelCase`; conversion in `GameStateContext.js`
- Piece types: `"white_pawn"` in state, `whitePawn` in image map
- CORS: `localhost:3000`, `localhost:8080`, `0.0.0.0` variants

### Move Generation Pattern

```python
# All get_moves_for_*() return:
{
    "possible_moves": [[row, col], ...],
    "possible_captures": [[[r1,c1], [r2,c2]], ...],   # [move_to, capture_at]
    "threatening_move": [[row, col]],                 # squares this piece attacks (used for check detection, not shown to player)
    "castle_moves": [[row, col]]                      # valid castle destination squares for the King (empty for all other pieces)
}
```

**Key Conventions:**
- Functions take `curr_game_state`, `prev_game_state`, `curr_position`
- Unused keys return `[]`; file boundary (c3-c6-f6-f3) checked in each generator

### Testing Patterns

**Key Conventions:**
- Unit: `mocks/empty_game.py`, direct `moves.get_moves()` calls, no DB
- Integration: `mocks/starting_game.py`, FastAPI test client, `select_and_move_*()` helpers
- Always `copy.deepcopy()` mock states; fixtures in `conftest.py`

### Code Organization Principles

**Key Conventions:**
- Single responsibility per module; all validation in `validation.py`
- Pipeline orchestration in `game_update_pipeline.py`
- Component hierarchy: Board.js → Piece.js → Buff.js; global state via Context
- Backend: absolute imports from `src/`; Frontend: relative imports
- Constants in ALL_CAPS: `BASE_API_URL`, `PLAYERS`, `IMAGE_MAP`

---

## Maintaining This Document

Update this file whenever you change architecture, game mechanics, modules, workflow, tests, or priorities.

### Update Triggers Checklist

- [ ] New game mechanic → Section 4
- [ ] New/changed utility module → Section 5
- [ ] Changed directory structure → Section 3
- [ ] New dependency → Section 2
- [ ] Modified build/test process → Section 6
- [ ] New test suite → Section 7
- [ ] Completed major feature → Section 8
- [ ] Changed common pattern → Section 9
- [ ] Any update → bump "Last Updated" timestamp
