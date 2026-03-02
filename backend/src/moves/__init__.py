__all__ = ['get_moves']

from src.moves.pawn import get_moves_for_pawn
from src.moves.knight import get_moves_for_knight
from src.moves.bishop import get_moves_for_bishop
from src.moves.rook import get_moves_for_rook
from src.moves.queen import get_moves_for_queen
from src.moves.king import get_moves_for_king

# get_moves() returns possible_moves_dict
# {
#   "possible_moves": [[row, col], ...] - positions where piece can move
#   "possible_captures": [[[row, col], [row, col]], ...] - first position is where piece has to move to capture piece in second position
#   "threatening_move": [[row, col]] - position where king of opposite side is threatened by the piece in its current position
#   "castle_moves": [[row, col]] - positions where piece can move to facilitate a castle
# }
def get_moves(old_game_state, new_game_state, curr_position, piece):
    piece_type = piece["type"]
    if "pawn" in piece_type:
        moves_info = get_moves_for_pawn(
            curr_game_state=new_game_state,
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    elif "knight" in piece_type:
        moves_info = get_moves_for_knight(
            curr_game_state=new_game_state,
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    elif "bishop" in piece_type:
        moves_info = get_moves_for_bishop(
            curr_game_state=new_game_state,
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    elif "rook" in piece_type:
        moves_info = get_moves_for_rook(
            curr_game_state=new_game_state,
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    elif "queen" in piece_type:
        moves_info = get_moves_for_queen(
            curr_game_state=new_game_state,
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    elif "king" in piece_type:
        moves_info = get_moves_for_king(
            curr_game_state=new_game_state,
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    else:
        raise ValueError(f"Unknown piece type: {piece_type}")
    return moves_info
