# PRD: Comprehensive Claude.md Documentation

## Overview
Create a detailed Claude.md file that serves as the primary context document for Claude Code when working on the League of Chess project. This documentation will enable Claude to understand the project architecture, game mechanics, tech stack, and development workflows without needing to explore the codebase repeatedly.

## Purpose
- Provide instant context for Claude Code sessions
- Document the unique chess variant mechanics (inspired by League of Legends)
- Map codebase structure and key files
- Explain development workflows (build, test, deploy)
- Serve as single source of truth for project architecture

## Requirements

### 1. Project Overview Section
- Project name and description (League of Chess variant)
- Inspiration source (Reddit post by /u/Zaaptastic)
- High-level purpose and goals
- Current development status and maturity level
- Link to main README for detailed patch notes

### 2. Technology Stack Section
- Backend: Python 3.12, FastAPI, MongoDB, Uvicorn, Pytest
- Frontend: React 18.2.0, Create React App
- Deployment: Docker, Nginx
- Environment management (.env configuration)
- Key dependencies and versions

### 3. Codebase Architecture Section
- Directory structure with descriptions
- Frontend organization (components, context, assets)
- Backend organization (api, moves, utils modules)
- Test organization (unit vs integration tests)
- Entry points for both frontend and backend
- Key files and their responsibilities

### 4. Game Mechanics Documentation
- Standard chess deviations
- Piece-specific mechanics:
  - Pawns: Conditional movement, material advantage
  - Knights: Jump removal
  - Bishops: Energize system, stacks, debuffs
  - Rooks: Scaling movement range
  - Queens: Stun mechanics, turn reset on kill
  - Kings: Divine Right, gold system
- Neutral monsters:
  - Dragon buffs (5 stacks)
  - Board Herald mechanics
  - Baron Nashor team buffs
- Special systems:
  - File control restrictions
  - Check/checkmate detection
  - Stalemate handling
  - Castling mechanics

### 5. Core Code Modules Section
- Detailed description of key backend files:
  - `src/moves.py`: Move generation (~2000 lines)
  - `src/utils/game_update_pipeline.py`: Turn orchestration
  - `src/utils/piece_mechanics.py`: Individual piece logic
  - `src/utils/monsters.py`: Neutral monster system
  - `src/utils/validation.py`: Move/state validation
  - `src/utils/check_checkmate.py`: Position analysis
  - `src/utils/queen_mechanics.py`: Queen turn reset
- Frontend component highlights:
  - `Board.js`: Main game board
  - `GameStateContext.js`: State management
  - Piece components and HUD

### 6. Development Workflow Section
- Local development setup
- Running frontend (npm start)
- Running backend (uvicorn server:app)
- Running tests (pytest with specific test files)
- Environment variable configuration
- Docker build and deployment
- API endpoint structure

### 7. Testing Strategy Section
- Unit test coverage (piece-specific mechanics)
- Integration test approach (full gameplay scenarios)
- Mock game states for testing
- Current test focus areas (neutral monster buffs)
- How to run specific test suites

### 8. Current Development Focus Section
- Active branch: backend/neutral_monster_buffs
- Recent work on dragon buff mechanics
- Piece marked-for-death validation
- Stalemate detection fixes
- Roadmap status (Frontend 75%, Backend 80%, Production 30%)

### 9. Common Patterns and Conventions
- Game state structure
- MongoDB document format
- API request/response cycle
- Error handling and logging
- Frontend-backend communication patterns

## Success Criteria
- Claude.md exists at project root
- All 9 sections are comprehensive and accurate
- File is well-formatted with clear markdown structure
- Cross-references to actual file paths (with line numbers where relevant)
- Easy to scan with headers and subheaders
- Includes code examples where helpful
- Total length: ~500-800 lines for comprehensive coverage

## Non-Goals
- Not a replacement for README.md (which has patch notes and setup)
- Not API documentation (endpoints are in api.py)
- Not a tutorial for playing the game
- Not a complete game rules manual (README has that)

## Technical Notes
- Use markdown tables for structured data
- Include file path references in code blocks
- Use consistent heading hierarchy
- Add table of contents at top
- Include last updated timestamp
