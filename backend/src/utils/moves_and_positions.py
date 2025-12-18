import traceback

from fastapi import HTTPException

from src.log import logger
import src.moves as moves
from .check_checkmate import trim_king_moves


# determine possibleMoves if a position_in_play is not [null, null]
def determine_possible_moves(old_game_state, new_game_state, moved_pieces, player, reset_position_in_play, is_pawn_exchange_required_this_turn):
    has_non_neutral_piece_moved = False
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral":
            continue
        has_non_neutral_piece_moved = True
    if has_non_neutral_piece_moved and reset_position_in_play: 
        new_game_state["position_in_play"] = [None, None]
    if new_game_state["position_in_play"][0] is not None: 
        square = new_game_state["board_state"][new_game_state["position_in_play"][0]][new_game_state["position_in_play"][1]]
        piece_in_play = None
        for piece in square:
            if (player and "white" in piece.get('type')) \
                or (not player and "black" in piece.get('type')) \
                or ("king" in piece.get('type')):
                piece_in_play = piece

        if not piece_in_play:
            error_msg = f"Invalid position_in_play in potential new game state, no piece present ({new_game_state['position_in_play']})"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        try:
            moves_info = moves.get_moves(old_game_state, new_game_state, new_game_state["position_in_play"], piece)
            if "king" in piece.get("type", ""):
                side = piece["type"].split("_")[0]
                moves_info = trim_king_moves(moves_info, old_game_state, new_game_state, side)
        except Exception as e:
            logger.error(f"Unable to determine move for {piece} due to: {traceback.format_exc()}")

        new_game_state["possible_moves"] = moves_info["possible_moves"]
        new_game_state["possible_captures"] = moves_info["possible_captures"]
    if is_pawn_exchange_required_this_turn:
        new_game_state["possible_moves"] = []
        new_game_state["possible_captures"] = []


def was_a_new_position_in_play_selected(moved_pieces, old_game_state, new_game_state):
    return not len([mp for mp in moved_pieces if mp["previous_position"][0] is not None and mp["current_position"][0] is not None]) and \
    old_game_state["position_in_play"] != new_game_state["position_in_play"]


# assumption is that there is a valid position_in_play in the new_game_state before using this function
def does_position_in_play_match_turn(old_game_state, new_game_state):
    side_that_should_be_moving = "white" if not old_game_state["turn_count"] % 2 else "black"
    position = new_game_state["position_in_play"]
    square = old_game_state["board_state"][position[0]][position[1]] or []

    if not square:
        logger.error(f"Position in play validation failed: No piece at position {position}")
        return False

    for piece in square:
        if side_that_should_be_moving in piece.get("type", ""):
            return True
    
    piece_types = [piece.get("type", "unknown") for piece in square]
    logger.error(f"Position in play validation failed: {side_that_should_be_moving} cannot move pieces at {position}. Found pieces: {piece_types}")
    return False