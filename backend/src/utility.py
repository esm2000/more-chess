from bson.objectid import ObjectId
import copy 
import datetime
from fastapi import HTTPException, Response
from mocks.empty_game import empty_game
from src.logging import logger
import src.api as api
import src.moves as moves

INVALID_GAME_STATE_ERROR_MESSAGE = "New game state is invalid"

MONSTER_INFO = {
    "neutral_dragon": {
        "position": [4, 7],
        "max_health": 5
    },
    "neutral_board_herald": {
        "position": [3, 0],
        "max_health": 5
    },
    "neutral_baron_nashor": {
        "position": [3, 0],
        "max_health": 10
    }
}

def determine_pieces_that_have_moved(curr_board_state, prev_board_state):
    moved_pieces_dict = {
        "missing": {},
        "spawned": {}
    }
    output = []
    
    for row in range(8):
        for col in range(8):
            curr_square = curr_board_state[row][col] if curr_board_state[row][col] else []
            prev_square = prev_board_state[row][col] if prev_board_state[row][col] else []
            
            # use list comprehension to get list of piece types on current and previous board on square of interest 
            pieces_on_curr_square = [piece.get("type") for piece in curr_square]
            pieces_on_prev_square = [piece.get("type") for piece in prev_square]

            # check for any missing pieces from current board by getting diff
            pieces_missing_from_curr_board = list(set(pieces_on_prev_square) - set(pieces_on_curr_square))
            
            # check for any additonal pieces by getting opposite diff
            pieces_added_to_curr_board = list(set(pieces_on_curr_square) - set(pieces_on_prev_square))

            # iterate through both results and record results in output array 
            curr_square_dict = {}
            prev_square_dict = {}
            
            for piece in curr_square:
                curr_square_dict[piece.get("type")] = piece
            for piece in prev_square:
                prev_square_dict[piece.get("type")] = piece

            for piece_type in pieces_missing_from_curr_board:
                if piece_type not in moved_pieces_dict["missing"]:
                    moved_pieces_dict["missing"][piece_type] = []
                moved_pieces_dict["missing"][piece_type].append({
                    "position": [row, col],
                    "piece": prev_square_dict[piece_type],
                    "side": piece_type.split("_")[0]
                })
                
            for piece_type in pieces_added_to_curr_board:
                if piece_type not in moved_pieces_dict["spawned"]:
                    moved_pieces_dict["spawned"][piece_type] = []
                moved_pieces_dict["spawned"][piece_type].append({
                    "position": [row, col],
                    "piece": curr_square_dict[piece_type],
                    "side": piece_type.split("_")[0]
                })

    # if piece if missing from current board square
    # check to see if it in previous board
    for piece_type in moved_pieces_dict["missing"]:
        # more than one piece of the same type moves, invalid game state
        for side in ["white", "black"]:
            if len([piece for piece in moved_pieces_dict["missing"][piece_type] if piece["side"] == side]) > 1 and \
            len([piece for piece in moved_pieces_dict["spawned"][piece_type] if piece["side"] == side]) > 1:
                error_message = f"More than one {piece_type} has moved"
                logger.error(error_message)
                raise Exception(error_message)
        for piece in moved_pieces_dict["missing"][piece_type]:
            current_position = [None, None]
            if piece_type in moved_pieces_dict["spawned"]:
                for i, p in enumerate(moved_pieces_dict["spawned"][piece_type].copy()):
                    if p["side"] == piece["side"]:
                        current_position = p["position"]
                    del moved_pieces_dict["spawned"][piece_type][i]
                if not moved_pieces_dict["spawned"][piece_type]:
                    del moved_pieces_dict["spawned"][piece_type]
        
            output.append({
                "piece": piece["piece"],
                "side": piece["side"],
                "previous_position": piece["position"],
                "current_position": current_position
            })
    
    for piece_type in moved_pieces_dict["spawned"]:
        for piece in moved_pieces_dict["spawned"][piece_type]:
            output.append({
                "piece": piece["piece"],
                "side": piece["side"],
                "previous_position": [None, None],
                "current_position": piece["position"] 
            })

    return output


def get_piece_value(piece_type):
        if "pawn" in piece_type:
            return 1
        elif "knight" in piece_type or "bishop" in piece_type:
            return 3
        elif "rook" in piece_type:
            return 5
        elif "queen" in piece_type:
            return 9
        elif "dragon" in piece_type or "herald" in piece_type:
            return 5
        elif "baron" in piece_type:
            return 10
        return 0


def spawn_neutral_monsters(game_state):
    turn_count = game_state["turn_count"]
    monster_info = copy.deepcopy(MONSTER_INFO)

    monsters = []
    if turn_count % 10 == 0 and turn_count > 0:
        monsters.append("neutral_dragon")
    if turn_count in [10, 20]:
        monsters.append("neutral_board_herald")
    if (turn_count - 20) % 15 == 0 and turn_count > 20:
        monsters.append("neutral_baron_nashor")

    for monster in monsters:
        monster_piece = [{"type": monster, "health": monster_info[monster]["max_health"], "turn_spawned": turn_count}]
        if game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]] is None:
            game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]] = monster_piece
        elif all(piece.get('type') != monster for piece in game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]]):
            game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]] = monster_piece + game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]]
            
            if monster == "neutral_baron_nashor":
                for i in range(len(game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]])):
                    if game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]][i].get("type") == "neutral_board_herald":
                        game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]].pop(i)


def carry_out_neutral_monster_attacks(game_state):
    monster_info = copy.deepcopy(MONSTER_INFO)
    sides = list(game_state["captured_pieces"].keys())

    for monster in monster_info:
        potential_monster_position = game_state["board_state"][monster_info[monster]["position"][0]][monster_info[monster]["position"][1]]
        if not potential_monster_position or not any(piece["type"] == monster for piece in potential_monster_position):
            continue
        
        for i in range(monster_info[monster]["position"][0] - 1, monster_info[monster]["position"][0] + 2):
            for j in range(monster_info[monster]["position"][1] - 1, monster_info[monster]["position"][1] + 2):
                if i >= 0 and i <= 7 and j >= 0 and j <= 7:
                    if game_state["board_state"][i][j]:
                        for k, piece in enumerate(game_state["board_state"][i][j].copy()):
                            side = piece["type"].split("_")[0]
                            if side in sides:
                                neutral_kill_mark = piece.get("neutral_kill_mark", -1)
                                
                                if neutral_kill_mark == game_state["turn_count"]:
                                    # if a king gets captured that's game over
                                    if "king" in piece["type"]:
                                        game_state["player_victory"] = side == "black"
                                        game_state["player_defeat"] = side == "white"
                                    else:
                                        game_state["board_state"][i][j].remove(piece)
                                        game_state["graveyard"].append(piece.get("type"))
                                elif game_state["turn_count"] - neutral_kill_mark > 2:
                                    game_state["board_state"][i][j][k]["neutral_kill_mark"] = game_state["turn_count"] + 2


def is_neutral_monster_spawned(neutral_monster_type, board_state):
    neutral_monster_position = MONSTER_INFO[neutral_monster_type]["position"]
    square = board_state[neutral_monster_position[0]][neutral_monster_position[1]]
    if not square:
        return False
    return any([piece.get("type") == neutral_monster_type for piece in square])


def evaluate_current_position(curr_position, curr_game_state):
    if curr_position[0] is None or curr_position[1] is None:
        raise Exception(f"Invalid position, {curr_position}, cannot have None value as a position")
    if curr_position[0] < -1 or curr_position[0] > 7 or curr_position[1] < -1 or curr_position[1] > 7:
        raise Exception(f"Invalid position, {curr_position}, out of bounds")
    if not curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        raise Exception(f"No piece at position {curr_position}")


def enable_adjacent_bishop_captures(curr_game_state, side, possible_moves_dict):
    adjacent_squares = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
    opposing_side = "white" if side == "black" else "black"
    # iterate through possible moves
    for possible_move in possible_moves_dict["possible_moves"]:
        # iterate through every adjacent square
        for adjacent_square in adjacent_squares:
            potential_bishop_square = [possible_move[0] + adjacent_square[0], possible_move[1] + adjacent_square[1]]
            # continue if square is out of bounds 
            if potential_bishop_square[0] < 0 or potential_bishop_square[0] > 7 or potential_bishop_square[1] < 0 or potential_bishop_square[1] > 7:
                continue
            # if there's a bishop from the opposing side present in an adjacent square,
            # add it to the capture_moves
            if curr_game_state["board_state"][potential_bishop_square[0]][potential_bishop_square[1]] and \
            any(piece.get("type") == f"{opposing_side}_bishop" for piece in curr_game_state["board_state"][potential_bishop_square[0]][potential_bishop_square[1]]):
                possible_moves_dict["possible_captures"].append([possible_move, potential_bishop_square])
    return possible_moves_dict

# used to reset game state during integration testing
def clear_game(game):
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 0
    game_on_next_turn["board_state"] = copy.deepcopy(empty_game["board_state"])

    game_on_next_turn["graveyard"] = []
    game_on_next_turn["gold_count"] = {
        "white": 0,
        "black": 0
    }
    game_on_next_turn["captured_pieces"] = {"white": [], "black": []}
    game_on_next_turn["previous_state"] = game_on_next_turn["board_state"]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    return game

# facilitate adjacent capture
# some pieces are able to capture pieces by being adjacent to them
# mutates new_game_state object and moved_pieces array
def facilitate_adjacent_capture(old_game_state, new_game_state, moved_pieces):
     # (while loop and manual pointer used since moved_pieces might be mutated)
    moved_pieces_pointer = 0
    # 1. iterate through moved pieces to check for pieces that have moved
    while moved_pieces_pointer < len(moved_pieces):
        moved_piece = moved_pieces[moved_pieces_pointer]
        if moved_piece["previous_position"][0] is None or \
        moved_piece["current_position"][1] is None or \
        moved_piece["side"] == "neutral":
            moved_pieces_pointer += 1
            continue
    # 2. get the moves and captures possible for the piece in its previous position
        # moves_info = {
        #   "possible_moves": [[row, col], ...] - positions where piece can move
        #   "possible_captures": [[[row, col], [row, col]], ...] - first position is where piece has to move to capture piece in second position
        # }
        try:
            # TODO: incorporate other piece types here
            if "pawn" in moved_piece["piece"]["type"]:
                moves_info = moves.get_moves_for_pawn(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=moved_piece["previous_position"]
                )
            if "knight" in moved_piece["piece"]["type"]:
                moves_info = moves.get_moves_for_knight(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=moved_piece["previous_position"]
                )
            if "bishop" in moved_piece["piece"]["type"]:
                moves_info = moves.get_moves_for_bishop(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=moved_piece["previous_position"]
                )
            if "rook" in moved_piece["piece"]["type"]:
                moves_info = moves.get_moves_for_rook(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=moved_piece["previous_position"]
                )
            if "queen" in moved_piece["piece"]["type"]:
                moves_info = moves.get_moves_for_queen(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=moved_piece["previous_position"]
                )
            if "king" in moved_piece["piece"]["type"]:
                moves_info = moves.get_moves_for_king(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=moved_piece["previous_position"]
                )
        except Exception as e:
            logger.error(f"Unable to determine move for {moved_piece['piece']} due to: {e}")
            moved_pieces_pointer += 1
            continue
    # 3. iterate through possible captures, looking for the ones that match the current position

        possible_captures = moves_info["possible_captures"]
        for possible_capture in possible_captures:
            if possible_capture[0] != moved_piece["current_position"]:
                continue
    # 4. check to see that there are captured pieces with previous positions that match each of the possible captures
            adajacent_pieces_to_capture_found = True
            for mp in moved_pieces:
                if mp["current_position"][0] is None and mp["previous_position"] == possible_capture[1]:
                    adajacent_pieces_to_capture_found = False
    # 5. for the possible captures that aren't accounted for in moved pieces, add to moved pieces and remove from new game state
    # and append to captured pieces
            if adajacent_pieces_to_capture_found:
                square = new_game_state["board_state"][possible_capture[1][0]][possible_capture[1][1]]
                piece_pointer = 0
                while piece_pointer < len(square):
                    piece = square[piece_pointer]
                    # if on opposing side add to moved pieces and remove from new game state
                    if (moved_piece["side"] == "white" and "black" in piece["type"]) or \
                    (moved_piece["side"] == "black" and "white" in piece["type"]) or \
                    "neutral" in piece["type"] and piece["health"] == 1:
                        if "health" in piece:
                            piece["health"] = 0
                        square.pop(piece_pointer)
                        if not square:
                            new_game_state["board_state"][possible_capture[1][0]][possible_capture[1][1]] = None
                        moved_pieces.append({
                            "piece": piece,
                            "side": piece["type"].split("_")[0],
                            "previous_position": possible_capture[1],
                            "current_position": [None, None]
                        })
                        new_game_state["captured_pieces"][moved_piece["side"]].append(piece["type"])
                    piece_pointer += 1
        moved_pieces_pointer += 1


def apply_bishop_energize_stacks_and_bishop_debuffs(old_game_state, new_game_state, moved_pieces):
    # iterate through moved pieces to check to see if a bishop has moved from its previous position and hasn't been bought/captured 
    # and add energize stacks based on its movement (5 energize stacks for each square moved, 10 energize stacks for each piece captured)
    for i, moved_piece in enumerate(moved_pieces):
        if "bishop" in moved_piece["piece"]["type"] and moved_piece["previous_position"][0] and moved_piece["current_position"][0]:
            # should be a good measure of how many diagonal squares the bishop has traveled
            distance_moved = abs(moved_piece["previous_position"][0] - moved_piece["current_position"][0])
            energize_stacks_to_add = 5 * distance_moved
            moves_info = moves.get_moves_for_bishop(
                curr_game_state=old_game_state, 
                prev_game_state=old_game_state.get("previous_state"), 
                curr_position=moved_piece["previous_position"]
            )

            for j, piece in enumerate(moved_pieces):
                if i == j or piece["current_position"][0] is not None:
                    continue
                if any(capture_positions[0] == moved_piece["current_position"] and capture_positions[1] == piece["previous_position"] for capture_positions in moves_info["possible_captures"]):
                    energize_stacks_to_add += 10
            
            for piece in new_game_state["board_state"][moved_piece["current_position"][0]][moved_piece["current_position"][1]]:
                if "bishop" in piece["type"]:
                    piece["energize_stacks"] += energize_stacks_to_add

                    if piece["energize_stacks"] > 100:
                        piece["energize_stacks"] = 100
    # iterate through moved pieces to check to see if bishop is threatening to capture a piece and apply debuff

            future_moves_info = moves.get_moves_for_bishop(
                curr_game_state=new_game_state, 
                prev_game_state=old_game_state, 
                curr_position=moved_piece["current_position"]
            )
            opposing_side = "white" if moved_piece["side"] == "black" else "black"
            if future_moves_info["possible_captures"]:
                for possible_capture_info in future_moves_info["possible_captures"]:
                    position_of_piece_in_danger = possible_capture_info[1]
                    if not new_game_state["board_state"][position_of_piece_in_danger[0]][position_of_piece_in_danger[1]]:
                        continue
                    for piece in new_game_state["board_state"][position_of_piece_in_danger[0]][position_of_piece_in_danger[1]]:
                        if opposing_side not in piece.get('type'):
                            continue
                        if "bishop_debuff" not in piece:
                            piece["bishop_debuff"] = 1
                        elif piece["bishop_debuff"] < 3:
                            piece["bishop_debuff"] += 1

# iterate through moved pieces to check to see if a queen has moved from its previous position and hasn't been bought/captured,
# also check to see if it's captured any pieces. If it hasn't captured any pieces, stun all adjacent pieces
def apply_queen_stun(old_game_state, new_game_state, moved_pieces):
    for i, moved_piece in enumerate(moved_pieces):
        if "queen" in moved_piece["piece"]["type"] and moved_piece["previous_position"][0] is not None and moved_piece["current_position"][0] is not None:
            queen_side = moved_piece["side"]
            moves_info = moves.get_moves_for_queen(
                curr_game_state=old_game_state, 
                prev_game_state=old_game_state.get("previous_state"), 
                curr_position=moved_piece["previous_position"]
            )
            canStun = True
            for j, piece in enumerate(moved_pieces):
                if i == j or piece["current_position"][0] is not None:
                    continue
                if any(capture_positions[0] == moved_piece["current_position"] and capture_positions[1] == piece["previous_position"] for capture_positions in moves_info["possible_captures"]):
                    canStun = False
                    break
            if canStun:
                directions = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, 1], [1, -1], [-1, -1]]
                for direction in directions:
                    row, col = moved_piece["current_position"][0] + direction[0], moved_piece["current_position"][1] + direction[1]
                    if row < 0 or col < 0 or row > 7 or col > 7:
                        continue
                    square = new_game_state["board_state"][row][col]
                    if square:
                        for piece in square:
                            side = piece["type"].split("_")[0]
                            if queen_side != side:
                                piece["is_stunned"] = True


# clean game possible moves and possible captures from last game state
# remove possible moves from last turn if any 
def clean_possible_moves_and_possible_captures(new_game_state):
    new_game_state["possible_moves"] = []
    new_game_state["possible_captures"] = []


def append_to_turn_count(old_game_state, new_game_state, moved_pieces):
    if len(moved_pieces) > 0:
        new_game_state["turn_count"] = old_game_state["turn_count"] + 1

# do not allow for updates to graveyard
def prevent_client_side_updates_to_graveyard(old_game_state, new_game_state):
    new_game_state["graveyard"] = old_game_state["graveyard"]

# if more than one pieces for one side has moved and its not a castle, invalidate
def check_to_see_if_more_than_one_piece_has_moved(
        old_game_state, 
        new_game_state, 
        moved_pieces, 
        is_valid_game_state, 
        is_pawn_exchange_possible,
        capture_positions,
        gold_spent
):
    move_count_for_white, move_count_for_black = 0, 0
    for side in old_game_state["captured_pieces"]:
        count_of_pieces_on_new_state = 0
        has_king_moved = False
        has_rook_moved = False
        is_pawn_exchange_possible[side] = False
        
        for moved_piece in moved_pieces:
            if side != moved_piece["side"]:
                continue
            
            if moved_piece["current_position"][0] is not None:
                count_of_pieces_on_new_state += 1
            if moved_piece["current_position"][0] is None and "pawn" in moved_piece["piece"]["type"]:
                previous_position = moved_piece['previous_position']
                # opposite_side = "white" if side == "black" else "black"
                square_on_current_game_state = new_game_state["board_state"][previous_position[0]][previous_position[1]]
                if square_on_current_game_state and all(side == piece["type"].split("_")[0] for piece in square_on_current_game_state):
                    is_pawn_exchange_possible[side] = True
                    new_game_state["turn_count"] = old_game_state["turn_count"]
            if moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
                if side == "white":
                    move_count_for_white += 1
                else:
                    move_count_for_black += 1

                moves_info = {"possible_moves": [], "possible_captures": []}
                try:
                    # TODO: incorporate other piece types here
                    if "pawn" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_pawn(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    if "knight" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_knight(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    if "bishop" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_bishop(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    if "rook" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_rook(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    if "queen" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_queen(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    if "king" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_king(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    for possible_capture_info in moves_info["possible_captures"]:
                        capture_positions.append(possible_capture_info)
                        
                except Exception as e:
                    logger.error(f"Unable to determine move for {moved_piece['piece']['type']} due to: {e}")
                    is_valid_game_state = False
        # if move(s) are invalid, invalidate
                if moved_piece["current_position"] not in moves_info["possible_moves"]:
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
                
                gold_spent[side] += get_piece_value(moved_piece["piece"]["type"])

                if gold_spent[side] > old_game_state["gold_count"][side]:
                    logger.error(f"More gold has been spent for {side} than {side} currently has ({gold_spent[side]} gold vs. {old_game_state['gold_count'][side]} gold)")
                    is_valid_game_state = False
        if count_of_pieces_on_new_state > 1:
            for moved_piece in moved_pieces:
                if "king" in moved_piece.get("piece"):
                    has_king_moved = True
                if "rook" in moved_piece.get("piece"):
                    has_rook_moved = True

            if not (has_king_moved and has_rook_moved):
                logger.error("A castle was not detected and more than one piece has moved")
                is_valid_game_state = False

    # if more than one side has pieces that's moved, invalidate 
    if move_count_for_white > 0 and move_count_for_black > 0: 
        logger.error("More than one side have pieces that have moved")
        is_valid_game_state = False
    return is_valid_game_state, move_count_for_white, move_count_for_black


def get_neutral_monster_slain_position(moved_pieces):
    neutral_monster_slain_position = None
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is None and moved_piece["previous_position"][0] is not None:
            neutral_monster_slain_position = moved_piece["previous_position"]
    return neutral_monster_slain_position


def is_invalid_king_capture(moved_pieces):
    for moved_piece in moved_pieces:
        if moved_piece["current_position"][0] is None and "king" in moved_piece["piece"]["type"]:
            return True
    return False
    

def invalidate_game_if_stunned_piece_moves(moved_pieces, is_valid_game_state):
    for moved_piece in moved_pieces:
        # if piece has a origin and a destination (not spawned or captured) and is stunned, invalidate 
        if moved_piece["current_position"][0] is not None \
        and moved_piece["previous_position"][0] is not None \
        and moved_piece["piece"].get("is_stunned", False):
            logger.error(f"Stunned piece, {moved_piece['piece']['type']}, has moved")
            is_valid_game_state = False
    return is_valid_game_state


# the side being cleansed is the moving side
def cleanse_stunned_pieces(new_game_state, move_count_for_white):
    side_being_cleansed = "white" if move_count_for_white else "black"
    
    # iterate through the entire board
    for row in new_game_state["board_state"]:
        for square in row:
            # if the square is present iterate through it
            if square:
                for piece in square:
                    # if piece is on moving side and is stunned, cleanse
                    if side_being_cleansed in piece['type'] and piece.get("is_stunned", False):
                        del piece['is_stunned']


def invalidate_game_if_monster_has_moved(is_valid_game_state, moved_pieces):
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
            logger.error("A neutral monster has moved")
            is_valid_game_state = False
    return is_valid_game_state


def is_neutral_monster_killed(moved_pieces):
    neutral_monster_slain_position = get_neutral_monster_slain_position(moved_pieces)
    was_neutral_monster_killed = False
    for moved_piece in moved_pieces:
        if neutral_monster_slain_position:
            if moved_piece["side"] != "neutral" and \
            abs(moved_piece["current_position"][0] - neutral_monster_slain_position[0]) in [0, 1] and \
            abs(moved_piece["current_position"][1] - neutral_monster_slain_position[1]) in [0, 1]:
                was_neutral_monster_killed = True
    return was_neutral_monster_killed


def check_for_disappearing_pieces(old_game_state, moved_pieces, is_valid_game_state, capture_positions, is_pawn_exchange_possible):
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
                if "pawn" in moved_piece["piece"]["type"] and is_pawn_exchange_possible[moved_piece["side"]]:
                    captured_piece_accounted_for = True
                      
            if not captured_piece_accounted_for:
                logger.error(f"Piece {moved_piece['piece']['type']} on {moved_piece['previous_position']} has disappeared from board without being captured")
                is_valid_game_state = False
    return is_valid_game_state


def damage_neutral_monsters(new_game_state, moved_pieces):
    for moved_piece in moved_pieces:
        # if a piece is on the same square or adjacent to neutral monsters, they should damage or kill them
        if moved_piece["previous_position"][0] is not None and moved_piece["current_position"][0] is not None:
            for neutral_monster in MONSTER_INFO:
                if is_neutral_monster_spawned(neutral_monster,new_game_state["board_state"]):
                    row_diff = abs(moved_piece["current_position"][0] - MONSTER_INFO[neutral_monster]["position"][0])
                    col_diff = abs(moved_piece["current_position"][1] - MONSTER_INFO[neutral_monster]["position"][1])
                    if row_diff in [-1, 0, 1] and col_diff in [-1, 0, 1]:
                        for i, piece in enumerate(new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]]):
                            if piece.get("type") == neutral_monster:
                                new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]][i]["health"] = piece["health"] - 1
                    
                                if new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]][i]["health"] < 1:
                                    new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]].pop(i)
                                    new_game_state["captured_pieces"][moved_piece["side"]].append(neutral_monster)

# if any new pieces in the captured pieces array have not been captured this turn, invalidate
# (it's imperative that this code section is placed after we've updated captured_pieces)
def invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array(old_game_state, new_game_state, moved_pieces, is_valid_game_state, is_pawn_exchange_possible):
    captured_pieces_array = new_game_state["captured_pieces"]["white"].copy() + new_game_state["captured_pieces"]["black"].copy() + new_game_state["graveyard"]
    for captured_piece in old_game_state["captured_pieces"]["white"] + old_game_state["captured_pieces"]["black"] + old_game_state["graveyard"]:
        captured_pieces_array.remove(captured_piece)

    for moved_piece in moved_pieces:
        if moved_piece["current_position"][0] is None:
            try:
                captured_pieces_array.remove(moved_piece["piece"]['type'])
            except ValueError as e:
                if not ("pawn" in moved_piece["piece"]["type"] and is_pawn_exchange_possible[moved_piece["side"]]):
                    logger.error(f"Captured piece {moved_piece['piece']['type']} has not been recorded as a captured piece")
                    is_valid_game_state = False
    
    if len(captured_pieces_array) > 0:
        logger.error(f"There are extra captured pieces not accounted for: {captured_pieces_array}")
        is_valid_game_state = False
    
    return is_valid_game_state

# determine possibleMoves if a position_in_play is not [null, null]
def determine_possible_moves(old_game_state, new_game_state, moved_pieces, player):
    has_non_neutral_piece_moved = False
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral":
            continue
        has_non_neutral_piece_moved = True

    if len(moved_pieces) > 0: 
        new_game_state["position_in_play"] = [None, None]
    if new_game_state["position_in_play"][0] is not None: 
        square = new_game_state["board_state"][new_game_state["position_in_play"][0]][new_game_state["position_in_play"][1]]
        piece_in_play = None
        for piece in square:
            if (player and "white" in piece.get('type')) or (not player and "black" in piece.get('type')):
                piece_in_play = piece

        if not piece_in_play:
            error_msg = f"Invalid position_in_play in potential new game state, no piece present ({new_game_state['position_in_play']})"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        if has_non_neutral_piece_moved:
            error_msg = f"Piece in play but pieces have been moved"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        try:
            # TODO: incorporate other piece types here
            if "pawn" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_pawn(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
            if "knight" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_knight(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
            if "bishop" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_bishop(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
            if "rook" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_rook(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
            if "queen" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_queen(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
            if "king" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_king(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
        except Exception as e:
            logger.error(f"Unable to determine move for {moved_piece['piece']} due to: {e}")
        
        new_game_state["possible_moves"] = moves_info["possible_moves"]
        new_game_state["possible_captures"] = moves_info["possible_captures"]


# gets the cumulative values of each side's pieces
def get_piece_value_for_each_side(new_game_state):
    piece_values = {"white": 0, "black": 0}
    
    for side in new_game_state["captured_pieces"]:
        for piece in new_game_state["captured_pieces"][side]:
            piece_values[side] += get_piece_value(piece)
    return piece_values


# updates the gold count for the new game state
def update_gold_count(old_game_state, new_game_state, gold_spent):
    for side in new_game_state["captured_pieces"]:

        for piece in list(set(new_game_state["captured_pieces"]) - set(old_game_state["captured_pieces"])):
            new_game_state["gold_count"][side] += get_piece_value(piece) * 2

        new_game_state["gold_count"][side] -= gold_spent[side]


# updates the capture point advantage
def update_capture_point_advantage(new_game_state):
    piece_values = get_piece_value_for_each_side(new_game_state)
    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]

    if capture_point_advantage == 0: 
        new_game_state["capture_point_advantage"] = None
    else:
        new_game_state["capture_point_advantage"] = [winning_side, capture_point_advantage]


def reassign_pawn_buffs(new_game_state):
    piece_values = get_piece_value_for_each_side(new_game_state)
    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]
    pawn_buff = capture_point_advantage if capture_point_advantage < 4 else 3 # capped at 3
    for row in range(8):
        for col in range(8):
            square = new_game_state["board_state"][row][col]
            if square:
                for i, piece in enumerate(square):
                    if "pawn" in piece.get("type"):
                        if piece.get("side") == winning_side:
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = pawn_buff
                        elif piece.get("side") == losing_side:
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = 0

# erase cached previous state in previous game state to manage space efficiency
# save old game state under new game state's previous state
def manage_game_state(old_game_state, new_game_state):
    previous_state_of_old_game = old_game_state.get("previous_state")
    if previous_state_of_old_game:
        old_game_state.pop("previous_state")
    new_game_state["previous_state"] = old_game_state


def perform_game_state_update(new_game_state, mongo_client, game_id):
    new_game_state["last_updated"] = datetime.datetime.now()
    query = {"_id": ObjectId(game_id)}
    new_values = {"$set": new_game_state}
    game_database = mongo_client["game_db"]
    game_database["games"].update_one(query, new_values)