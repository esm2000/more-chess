import collections

import src.moves as moves
from src.log import logger
from .check_checkmate import can_king_move


# conditionally mutates new_game_state
def handle_draw_conditions(old_game_state, new_game_state):
    # condition: only kings are left on board
    piece_log = collections.Counter()
        
    for row in new_game_state["board_state"]:
        for col_index in range(len(row)):
            square = row[col_index] or []
            for piece in square:
                piece_type = piece.get("type", "")
                if "white" in piece_type or "black" in piece_type:
                    piece_log[piece_type] += 1

    if "white_king" in piece_log and "black_king" in piece_log and len(piece_log) == 2:
        logger.info("BOTH DEFEATS set to True: Only kings remaining on board")
        new_game_state["white_defeat"] = True
        new_game_state["black_defeat"] = True

    # condition: where only moves available will place current player in check
    side_that_should_be_moving_next_turn = "white" if not new_game_state["turn_count"] % 2 else "black"
    only_king_can_move = True
    is_king_immobile = False
    for row_index in range(len(new_game_state["board_state"])):
        row = new_game_state["board_state"][row_index]
        if not only_king_can_move:
            break
        for col_index in range(len(row)):
            if not only_king_can_move:
                break
            square = row[col_index] or []
            for piece in square:
                piece_type = piece.get("type", "")
                if side_that_should_be_moving_next_turn in piece_type:
                    moves_info = moves.get_moves(old_game_state, new_game_state, [row_index, col_index], piece)
                    if moves_info["possible_moves"] and "king" not in piece_type:
                        only_king_can_move = False
                        break
                    elif not moves_info["possible_moves"] and "king" in piece_type:
                        is_king_immobile = True
    
    if only_king_can_move and is_king_immobile:
        logger.info("BOTH DEFEATS set to True: Only king can move and king is immobile")
        new_game_state["white_defeat"] = True
        new_game_state["black_defeat"] = True

    # condition: no moves are available
    tie_game_if_no_moves_are_possible_next_turn(old_game_state, new_game_state)



# conditionally mutates new_game_state
# it's assumed that this function is used after the turn is incremented
def tie_game_if_no_moves_are_possible_next_turn(old_game_state, new_game_state):
    # if one or both sides have already lost no reason to continue
    if new_game_state["white_defeat"] or new_game_state["black_defeat"]:
        return 
    
    old_game_turn_count = old_game_state["turn_count"]
    new_game_turn_count = new_game_state["turn_count"]
    side_that_should_be_moving_next_turn = "white" if old_game_turn_count % 2 else "black"

    if can_king_move(old_game_state, new_game_state, turn_incremented=old_game_turn_count != new_game_turn_count):
        return
    
    tie_game = True
    for i in range(len(new_game_state["board_state"])):
        for j in range(len(new_game_state["board_state"][0])):
            square = new_game_state["board_state"][i][j]

            if square:
                for piece in square:
                    if side_that_should_be_moving_next_turn in piece.get("type", "") and \
                        "king" not in piece.get("type", ""):
                        tie_game = len(
                                moves.get_moves(
                                    old_game_state,
                                    new_game_state,
                                    [i, j],
                                    piece
                                )["possible_moves"]
                        ) == 0
            if not tie_game:
                break
    
    if tie_game:
        logger.info("BOTH DEFEATS set to True: No moves possible for next turn (tie game)")
        new_game_state["white_defeat"] = True
        new_game_state["black_defeat"] = True    
        

# new game's turn count is representative of what side should be moving next turn (even is white, odd is black)
def are_all_non_king_pieces_stunned(new_game_state, reverse=False):
    new_game_turn_count = new_game_state["turn_count"]
    side_that_should_be_moving_next_turn = "white" if not new_game_turn_count % 2 else "black"
    if reverse:
        side_that_should_be_moving_next_turn = "white" if side_that_should_be_moving_next_turn == "black" else "black"
    output = True
    for i in range(len(new_game_state["board_state"])):
        for j in range(len(new_game_state["board_state"][0])):
            square = new_game_state["board_state"][i][j]
            if square:
                for piece in square:
                    if piece.get("type", "").split("_")[0] == side_that_should_be_moving_next_turn and \
                    "king" not in piece.get("type", "") and \
                    not piece.get("is_stunned", False):
                        output = False
    return output