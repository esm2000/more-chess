"""King move generation."""

from __future__ import annotations

from src.types import GameState, MoveResult, Position
from src.utils.board_analysis import evaluate_current_position
from src.moves._helpers import (
    process_possible_moves_dict,
    _add_marked_for_death_threats,
)


# must be called with get_unsafe_positions() where unsafe positions are filtered out
# (unable to do that within this function without circular importing in can_king_move())
def get_moves_for_king(curr_game_state: GameState, prev_game_state: GameState | None, curr_position: Position) -> MoveResult:
    """Generate all legal moves for a king at curr_position."""
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "king" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No king found at position {curr_position}")

    possible_moves = []
    possible_captures = []
    castle_moves = []

    dragon_buff = piece_in_play.get("dragon_buff", 0)

    directions = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, 1], [1, -1], [-1, -1]]
    for direction in directions:
        possible_position = [curr_position[0] + direction[0], curr_position[1] + direction[1]]
        if not (possible_position[0] >= 0 and possible_position[0] <= 7 and possible_position[1] >= 0 and possible_position[1] <= 7):
            continue

        if not curr_game_state["board_state"][possible_position[0]][possible_position[1]]:
            possible_moves.append(possible_position.copy())
        # check for a piece from the opposing side, add piece's position to the possible_moves and possible_captures
        # (UNLESS IT'S A KING)
        elif any(opposing_side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
            if all(f"{opposing_side}_king" != piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                possible_moves.append(possible_position.copy())
                possible_captures.append([possible_position.copy(), possible_position.copy()])
        # the king shouldn't be allowed to be on the same square as a neutral monster and can only move to a neutral monster's square to slay it
        # check for a neutral monster, only add monster's position to possible_moves and possible_captures if it has a health of 1.
        elif any(("neutral" in piece["type"] and piece.get("health", 0) == 1) for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
            possible_moves.append(possible_position.copy())
            possible_captures.append([possible_position.copy(), possible_position.copy()])

    start_row = 7 if side == "white" else 0
    king_start = [start_row, 4]

    # Only allow castling if king is in its starting position and hasn't moved
    if curr_position == king_start and not curr_game_state["castle_log"][side]["has_king_moved"]:
        def rook_present(row, col):
            return any(
                piece.get("type", "") == f"{side}_rook"
                for piece in curr_game_state["board_state"][row][col] or []
            )

        def rook_dragon_buff(row, col):
            dragon_buff = 0
            for piece in curr_game_state["board_state"][row][col] or []:
                if piece.get("type", "") == f"{side}_rook":
                    dragon_buff = piece.get("dragon_buff", 0)
            return dragon_buff

        def is_path_clear(start_col, end_col):
            min_col = min(start_col, end_col)
            max_col = max(start_col, end_col)
            for col in range(min_col + 1, max_col):
                if curr_game_state["board_state"][start_row][col]:
                    return False
            return True

        if (rook_present(start_row, 0) and
            not curr_game_state["castle_log"][side]["has_left_rook_moved"] and
            ((rook_dragon_buff(start_row, 0)  >= 4 and dragon_buff >= 4) or is_path_clear(4, 0))):
            castle_moves.append([start_row, 2])

        if (rook_present(start_row, 7) and
            not curr_game_state["castle_log"][side]["has_right_rook_moved"] and
            ((rook_dragon_buff(start_row, 7) >= 4 and dragon_buff >= 4) or is_path_clear(4, 7))):
            castle_moves.append([start_row, 6])

    threatening_move = []
    if dragon_buff >= 5:
        _add_marked_for_death_threats(possible_moves, threatening_move, opposing_side, curr_game_state["board_state"])

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move, "castle_moves": castle_moves}, is_king=True)
