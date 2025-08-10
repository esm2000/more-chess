import traceback

from src.log import logger
import src.moves as moves
from .check_checkmate import trim_king_moves
from .monsters import MONSTER_INFO
from .board_analysis import get_piece_value


INVALID_GAME_STATE_ERROR_MESSAGE = "New game state is invalid"

# if more than one pieces for one side has moved and its not a castle, invalidate
def check_to_see_if_more_than_one_piece_has_moved(
        old_game_state, 
        new_game_state, 
        moved_pieces,
        capture_positions,
        is_valid_game_state
):
    for side in old_game_state["captured_pieces"]:
        count_of_pieces_on_new_state = 0
        has_king_moved = False
        has_rook_moved = False
        
        for moved_piece in moved_pieces:
            if side != moved_piece["side"]:
                continue
            
            if moved_piece["current_position"][0] is not None:
                count_of_pieces_on_new_state += 1
            if moved_piece["current_position"][0] is None and "pawn" in moved_piece["piece"]["type"]:
                previous_position = moved_piece['previous_position']
                square_on_current_game_state = new_game_state["board_state"][previous_position[0]][previous_position[1]]
                if square_on_current_game_state and all(side == piece["type"].split("_")[0] for piece in square_on_current_game_state):
                    new_game_state["turn_count"] = old_game_state["turn_count"]
            if moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
                moves_info = {"possible_moves": [], "possible_captures": []}
                try:
                    moves_info = moves.get_moves(old_game_state.get("previous_state"), old_game_state, moved_piece["previous_position"], moved_piece["piece"])
                    if "king" in moved_piece["piece"].get("type"):
                        moves_info = trim_king_moves(moves_info, old_game_state.get("previous_state"), old_game_state, moved_piece["side"])   
                    for possible_capture_info in moves_info["possible_captures"]:
                        capture_positions.append(possible_capture_info) 
                except Exception as e:
                    logger.error(f"Unable to determine move for {moved_piece['piece']['type']} due to: {traceback.format_exc()}")
                    is_valid_game_state = False
        # if move(s) are invalid, invalidate
                if moved_piece["current_position"] not in moves_info["possible_moves"] + moves_info["castle_moves"]:
                    logger.error(f"Square {moved_piece['previous_position']} to square {moved_piece['current_position']} invalid for {moved_piece['piece']['type']}")
                    is_valid_game_state = False
        # if a piece has spawned without being exchanged for a pawn
        # take note of gold count that is supposed to be spent to obtain it
            if moved_piece["current_position"][0] is not None \
            and moved_piece["previous_position"][0] is None \
            and not any(p['previous_position'] == moved_piece["current_position"] for p in moved_pieces if p["previous_position"][0] is not None):          
                if "queen" in moved_piece["piece"]["type"] or "king" in moved_piece["piece"]["type"]:
                    logger.error(f"A {'queen' if 'queen' in moved_piece['piece']['type'] else 'king'} has been bought")
                    is_valid_game_state = False
        # if more one piece moves and it's not a castle, invalidate 
        if count_of_pieces_on_new_state > 2:
            logger.error("3 or more pieces of the same side have moved in one turn")
            is_valid_game_state = False
        elif count_of_pieces_on_new_state == 2:
            # participating pieces must be unmoved according to the log to be a castle
            # (left) black rook [0, 0] + king [0, 4] -> black rook [0, 3] + king [0, 2]
            # (right) black rook [0, 7] + king [0, 4] -> black rook [0, 5] + king [0, 6]
            # (left) white rook [7, 0] + king [7, 4] -> white rook [7, 3] + king [7, 2]
            # (right) white rook [7, 7] + king [7, 4] -> white rook [7, 5] + king [7, 6]

            king_position = {"previous": [None, None], "current": [None, None]}
            rook_position = {"previous": [None, None], "current": [None, None]}

            for moved_piece in moved_pieces:
                if side != moved_piece["side"]:
                    continue
                
                if moved_piece["current_position"][0] is not None:
                    moved_piece_info = moved_piece.get("piece", {})
                    if "king" in moved_piece_info.get("type", ""):
                        has_king_moved = True
                        king_position["previous"], king_position["current"] = moved_piece["previous_position"], moved_piece["current_position"]
                    if "rook" in moved_piece_info.get("type", ""):
                        has_rook_moved = True
                        rook_position["previous"], rook_position["current"] = moved_piece["previous_position"], moved_piece["current_position"]

            valid_castling_moves = {
                "white": [
                    {
                        "king_from": [7, 4], "king_to": [7, 2],
                        "rook_from": [7, 0], "rook_to": [7, 3],
                        "king_moved": "has_king_moved",
                        "rook_moved": "has_left_rook_moved"
                    },
                    {
                        "king_from": [7, 4], "king_to": [7, 6],
                        "rook_from": [7, 7], "rook_to": [7, 5],
                        "king_moved": "has_king_moved",
                        "rook_moved": "has_right_rook_moved"
                    }
                ],
                "black": [
                    {
                        "king_from": [0, 4], "king_to": [0, 2],
                        "rook_from": [0, 0], "rook_to": [0, 3],
                        "king_moved": "has_king_moved",
                        "rook_moved": "has_left_rook_moved"
                    },
                    {
                        "king_from": [0, 4], "king_to": [0, 6],
                        "rook_from": [0, 7], "rook_to": [0, 5],
                        "king_moved": "has_king_moved",
                        "rook_moved": "has_right_rook_moved"
                    }
                ]
            }

            # Check if both pieces haven't moved
            if not (has_king_moved and has_rook_moved):
                logger.error("A castle was not detected and more than one piece of the same side has moved")
                is_valid_game_state = False
            else:
                # Check for valid castling move
                for move in valid_castling_moves.get(side, []):
                    if (
                        king_position["previous"] == move["king_from"]
                        and king_position["current"] == move["king_to"]
                        and rook_position["previous"] == move["rook_from"]
                        and rook_position["current"] == move["rook_to"]
                        and not new_game_state["castle_log"][side][move["king_moved"]]
                        and not new_game_state["castle_log"][side][move["rook_moved"]]
                        and not new_game_state["check"][side]
                    ):  
                        break  # Valid castling move
                else:
                    logger.error("Invalid castle was attempted")
                    is_valid_game_state = False

    return is_valid_game_state


# old game's turn count is representative of what side should be moving (even is white, odd is black)
def invalidate_game_if_wrong_side_moves(moved_pieces, is_valid_game_state, old_game_turn_count):
    side_that_should_be_moving = "white" if not old_game_turn_count % 2 else "black"
    for side in [piece_info["side"] for piece_info in moved_pieces if piece_info["current_position"][0] is not None]:
        if side != side_that_should_be_moving and side != "neutral":
            logger.error(f"{side} moved instead of {side_that_should_be_moving}")
            is_valid_game_state = False
    return is_valid_game_state


def invalidate_game_if_more_than_one_side_moved(move_count_for_white, move_count_for_black, is_valid_game_state):
    # if more than one side has pieces that's moved, invalidate 
    if move_count_for_white > 0 and move_count_for_black > 0: 
        logger.error("More than one side have pieces that have moved")
        is_valid_game_state = False
    return is_valid_game_state


def invalidate_game_if_stunned_piece_moves(moved_pieces, is_valid_game_state):
    for moved_piece in moved_pieces:
        # if piece has a origin and a destination (not spawned or captured) and is stunned, invalidate 
        if moved_piece["current_position"][0] is not None \
        and moved_piece["previous_position"][0] is not None \
        and moved_piece["piece"].get("is_stunned", False):
            logger.error(f"Stunned piece, {moved_piece['piece']['type']}, has moved")
            is_valid_game_state = False
    return is_valid_game_state


def invalidate_game_if_monster_has_moved(is_valid_game_state, moved_pieces):
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
            logger.error("A neutral monster has moved")
            is_valid_game_state = False
    return is_valid_game_state


def invalidate_game_if_too_much_gold_is_spent(old_game_state, gold_spent, is_valid_game_state):
    for side in old_game_state["gold_count"]:
        if gold_spent[side] > old_game_state["gold_count"][side]:
            logger.error(f"More gold has been spent for {side} than {side} currently has ({gold_spent[side]} gold vs. {old_game_state['gold_count'][side]} gold)")
            is_valid_game_state = False
    return is_valid_game_state


# if any new pieces in the captured pieces array have not been captured this turn, invalidate
# (it's imperative that this code section is placed after we've updated captured_pieces)
def invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array(old_game_state, new_game_state, moved_pieces, is_valid_game_state, is_pawn_exchange_possibly_being_carried_out):
    captured_pieces_array = new_game_state["captured_pieces"]["white"].copy() + new_game_state["captured_pieces"]["black"].copy() + new_game_state["graveyard"]
    for captured_piece in old_game_state["captured_pieces"]["white"] + old_game_state["captured_pieces"]["black"] + old_game_state["graveyard"]:
        captured_pieces_array.remove(captured_piece)

    for moved_piece in moved_pieces:
        if moved_piece["current_position"][0] is None:
            try:
                captured_pieces_array.remove(moved_piece["piece"]['type'])
            except ValueError as e:
                if not ("pawn" in moved_piece["piece"]["type"] and is_pawn_exchange_possibly_being_carried_out[moved_piece["side"]]):
                    logger.error(f"Captured piece {moved_piece['piece']['type']} has not been recorded as a captured piece")
                    is_valid_game_state = False
    
    if len(captured_pieces_array) > 0:
        logger.error(f"There are extra captured pieces not accounted for: {captured_pieces_array}")
        is_valid_game_state = False
    
    return is_valid_game_state


def check_for_disappearing_pieces(
    old_game_state, 
    new_game_state, 
    moved_pieces, 
    is_valid_game_state, 
    capture_positions, 
    is_pawn_exchange_possibly_being_carried_out
):
    for moved_piece in moved_pieces:
        # if any piece captured this turn doesn't have a captor, invalidate (keep in mind that adjacent 
        # capturing is possible so positions in moved_pieces shouldn't be relied on as crutch)
        if moved_piece["side"] != "neutral" and moved_piece["current_position"][0] is None:
            captured_piece_accounted_for = False
            for capture_position in capture_positions:
                if capture_position[1] == moved_piece["previous_position"]:
                    captured_piece_accounted_for = True
                    capture_positions.remove(capture_position)           
            
            if not captured_piece_accounted_for:
                # check to see if captured piece was next to a neutral monster 
                for monster in MONSTER_INFO:
                    potential_monster_position = old_game_state["board_state"][MONSTER_INFO[monster]["position"][0]][MONSTER_INFO[monster]["position"][1]]
                    if abs(moved_piece["previous_position"][0] - MONSTER_INFO[monster]["position"][0]) in [0, 1] and \
                    abs(moved_piece["previous_position"][1] - MONSTER_INFO[monster]["position"][1]) in [0, 1] and \
                    any(piece["type"] == monster for piece in potential_monster_position):
                    # check to see if neutral monster is also present in previous game
                        turn_count_for_previous_game = old_game_state["turn_count"]
                        turn_count_when_monster_spawned = list(filter(lambda piece: piece["type"] == monster, potential_monster_position))[0]["turn_spawned"]
                        if turn_count_for_previous_game > turn_count_when_monster_spawned:
                            captured_piece_accounted_for = True

                # check to see if a pawn exchange has occurred
                if "pawn" in moved_piece["piece"]["type"] and is_pawn_exchange_possibly_being_carried_out[moved_piece["side"]]:
                    captured_piece_accounted_for = True

                    row = moved_piece["previous_position"][0]
                    col = moved_piece["previous_position"][1]
                    if any("king" in piece.get("type") for piece in (new_game_state["board_state"][row][col] or [])):
                        logger.error(f"A king cannot be exchanged for a pawn")
                        is_valid_game_state = False
            
            if not captured_piece_accounted_for and new_game_state["bishop_special_captures"]:
                # check to see if piece was captured via full bishop debuff stacked
                if moved_piece["piece"]["type"] == new_game_state["bishop_special_captures"][0]["type"]:
                    captured_piece_accounted_for = True
                      
            if not captured_piece_accounted_for:
                logger.error(f"Piece {moved_piece['piece']['type']} on {moved_piece['previous_position']} has disappeared from board without being captured")
                is_valid_game_state = False
    return is_valid_game_state


def check_if_pawn_exchange_is_required(old_game_state, new_game_state, moved_pieces, is_valid_game_state):
    side_that_should_be_moving = "white" if not old_game_state["turn_count"] % 2 else "black"
    side_that_should_not_be_moving = "black" if side_that_should_be_moving == "white" else "white"

    row = 0 if side_that_should_be_moving == "white" else 7
    is_pawn_exchange_required_this_turn = False

    for col in range(8):
        if any([piece.get("type") == f"{side_that_should_be_moving}_pawn" for piece in (new_game_state["board_state"][row][col] or [])]):
            is_pawn_exchange_required_this_turn = True

    if is_pawn_exchange_required_this_turn:
        for moved_piece in moved_pieces:
            if moved_piece["side"] == side_that_should_not_be_moving and moved_piece["current_position"][0] is not None:
                is_valid_game_state = False
    return is_pawn_exchange_required_this_turn, is_valid_game_state


def check_if_pawn_exhange_is_possibly_being_carried_out(old_game_state, new_game_state, moved_pieces):
    is_pawn_exchange_possibly_being_carried_out = {"white": False, "black": False}

    for side in old_game_state["captured_pieces"]:
        for moved_piece in moved_pieces:
            if side != moved_piece["side"]:
                continue
                
            if moved_piece["current_position"][0] is None and "pawn" in moved_piece["piece"]["type"]:
                previous_position = moved_piece['previous_position']
                square_on_current_game_state = new_game_state["board_state"][previous_position[0]][previous_position[1]]
                if square_on_current_game_state and all(side == piece["type"].split("_")[0] for piece in square_on_current_game_state):
                    is_pawn_exchange_possibly_being_carried_out[side] = True
    return is_pawn_exchange_possibly_being_carried_out


def should_turn_count_be_incremented_for_pawn_exchange(old_game_state, is_pawn_exchange_possibly_being_carried_out):
    side_that_should_be_moving = "white" if not old_game_state["turn_count"] % 2 else "black"
    return  is_pawn_exchange_possibly_being_carried_out[side_that_should_be_moving]


def get_gold_spent(moved_pieces):
    gold_spent = {"white": 0, "black": 0}
    for moved_piece in moved_pieces:
    # if a piece has spawned without being exchanged for a pawn
    # take note of gold count that is supposed to be spent to obtain it
        if moved_piece["current_position"][0] is not None \
        and moved_piece["previous_position"][0] is None \
        and not any(p['previous_position'] == moved_piece["current_position"] for p in moved_pieces if p["previous_position"][0] is not None):          
            gold_spent[moved_piece["side"]] += get_piece_value(moved_piece["piece"]["type"])
    return gold_spent


def is_invalid_king_capture(moved_pieces):
    for moved_piece in moved_pieces:
        if moved_piece["current_position"][0] is None and "king" in moved_piece["piece"]["type"]:
            return True
    return False