// PawnExchangeModal.js
// ====================
// Pawn promotion UI — shown when a pawn reaches the back rank.
//
// HOW TO DETECT WHEN TO SHOW:
//   The backend does NOT send an explicit "exchange required" flag.
//   Instead, it signals implicitly:
//     1. A pawn of the current side exists on the promotion rank
//        (row 0 for white, row 7 for black)
//     2. possible_moves and possible_captures are BOTH empty arrays
//     3. The turn count has been reset (same side still moving)
//   Check for: pawn on back rank + no legal moves = show this modal.
//
// WHAT IT DOES:
//   1. Display 4 promotion options: Knight, Bishop, Rook, Queen
//      (King exchange is rejected by the backend — validation.py:289-293)
//   2. Each option shows the piece sprite (use IMAGE_MAP from utility.js)
//   3. On selection:
//      a. Replace the pawn in boardState with the chosen piece at same position
//      b. Call updateGameState() to send to backend
//      c. Backend validates via check_if_pawn_exchange_is_possibly_being_carried_out()
//      d. Turn count increments, game continues
//
// STYLING:
//   - Pixel art retro aesthetic — brown/earth tones matching Shop.js palette
//     (rgb(125, 59, 2) background, rgb(71, 33, 1) border)
//   - Use the pixel font already in the project
//   - Modal overlay centered on the board, semi-transparent backdrop
//   - Piece sprites should be large enough to tap on mobile (use determineIsMobile())
//   - Header like "~ Promote Pawn ~" matching Shop.js "~ Shop ~" style
//
// PROPS (suggested):
//   - pawnPosition: [row, col] — position of the pawn being promoted
//   - side: "white" — determines piece type prefix (currently only white plays)
//   - onExchange: callback after exchange completes (to clear modal state)
//
// WHERE TO RENDER:
//   Board.js — add detection logic and render this modal when conditions are met.
//   It should block all other board interaction while visible.
//
// RELEVANT BACKEND FILES:
//   - validation.py:315-332 — check_if_pawn_exchange_is_required()
//   - validation.py:335-349 — check_if_pawn_exchange_is_possibly_being_carried_out()
//   - game_update_pipeline.py:148-167 — handle_pawn_exchanges()
//   - moves_and_positions.py:46-48 — clears moves when exchange required
//
// RELEVANT FRONTEND FILES:
//   - utility.js — IMAGE_MAP, camelToSnake, determineIsMobile
//   - context/GameStateContext.js — updateGameState, boardState, possibleMoves
//   - components/Board.js — parent component, detection logic goes here
