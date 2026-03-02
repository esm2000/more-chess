"""Castling log tracking -- records when kings and rooks first move."""

from src.types import GameState, MovedPiece


def update_castle_log(new_game_state: GameState, moved_pieces: list[MovedPiece]) -> None:
    """Mark kings/rooks as moved in castle_log when they leave starting squares."""
    moved_rooks_and_kings = [piece_info for piece_info in moved_pieces if 'rook' in piece_info['piece']['type'] or 'king' in piece_info['piece']['type']]

    for moved_piece_info in moved_rooks_and_kings:
        if moved_piece_info['piece']['type'] == 'white_king' and moved_piece_info['previous_position'] == [7, 4]:
            new_game_state['castle_log']['white']["has_king_moved"] = True
        elif moved_piece_info['piece']['type'] == 'black_king' and moved_piece_info['previous_position'] == [0, 4]:
            new_game_state['castle_log']['black']["has_king_moved"] = True
        elif moved_piece_info['piece']['type'] == 'white_rook' and moved_piece_info['previous_position'] == [7, 0]:
            new_game_state['castle_log']['white']["has_left_rook_moved"] = True
        elif moved_piece_info['piece']['type'] == 'white_rook' and moved_piece_info['previous_position'] == [7, 7]:
            new_game_state['castle_log']['white']["has_right_rook_moved"] = True
        elif moved_piece_info['piece']['type'] == 'black_rook' and moved_piece_info['previous_position'] == [0, 0]:
            new_game_state['castle_log']['black']["has_left_rook_moved"] = True
        elif moved_piece_info['piece']['type'] == 'black_rook' and moved_piece_info['previous_position'] == [0, 7]:
            new_game_state['castle_log']['black']["has_right_rook_moved"] = True
