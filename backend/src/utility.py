from bson.objectid import ObjectId
import copy 
import datetime
from fastapi import HTTPException, Response
from mocks.empty_game import empty_game
import random
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
        monster_position_row = monster_info[monster]["position"][0]
        monster_position_col = monster_info[monster]["position"][1]
        if game_state["board_state"][monster_position_row][monster_position_col] is None:
            game_state["board_state"][monster_position_row][monster_position_col] = monster_piece
        elif all(piece.get('type') != monster for piece in game_state["board_state"][monster_position_row][monster_position_col]):            
            i = 0
            while i < len(game_state["board_state"][monster_position_row][monster_position_col]):
                piece = game_state["board_state"][monster_position_row][monster_position_col][i]
                if "king" in piece.get("type"):
                    if "white" in piece["type"]:
                        game_state["player_defeat"] = True
                    else:
                        game_state["player_victory"] = True
                    i += 1
                else:
                    game_state["graveyard"].append(piece.get("type"))
                    game_state["board_state"][monster_position_row][monster_position_col].pop(i)

            game_state["board_state"][monster_position_row][monster_position_col] = monster_piece

            if monster == "neutral_baron_nashor":
                for i in range(len(game_state["board_state"][monster_position_row][monster_position_col])):
                    if game_state["board_state"][monster_position_row][monster_position_col][i].get("type") == "neutral_board_herald":
                        game_state["board_state"][monster_position_row][monster_position_col].pop(i)


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
    game_on_next_turn["previous_state"] = copy.deepcopy(game_on_next_turn)
    
    game_on_next_turn["player_victory"] = False
    game_on_next_turn["player_defeat"] = False

    game_on_next_turn["sword_in_the_stone_position"] = None

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
            moves_info = moves.get_moves(old_game_state.get("previous_state"), old_game_state, moved_piece["previous_position"], moved_piece["piece"])
            if "king" in moved_piece["piece"].get("type"):
                moves_info = trim_king_moves(moves_info, old_game_state.get("previous_state"), old_game_state, moved_piece["side"])
        except Exception as e:
            import traceback
            logger.error(f"Unable to determine move for {moved_piece['piece']} due to: {traceback.format_exc(e)}")
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
    positions_with_bishop_debuffs_applied = []
    # iterate through moved pieces to check to see if a bishop has moved from its previous position and hasn't been bought/captured 
    # and add energize stacks based on its movement (5 energize stacks for each square moved, 10 energize stacks for each piece captured)
    for i, moved_piece in enumerate(moved_pieces):
        if "bishop" in moved_piece["piece"]["type"] and moved_piece["previous_position"][0] is not None and moved_piece["current_position"][0] is not None:
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
                    if position_of_piece_in_danger in positions_with_bishop_debuffs_applied:
                        continue
                    positions_with_bishop_debuffs_applied.append(position_of_piece_in_danger)
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
                            if queen_side != side and "king" not in piece["type"]:
                                piece["is_stunned"] = True
                                piece["turn_stunned_for"] = old_game_state["turn_count"] + 1


# clean game possible moves and possible captures from last game state
# remove possible moves from last turn if any 
def clean_possible_moves_and_possible_captures(new_game_state):
    new_game_state["possible_moves"] = []
    new_game_state["possible_captures"] = []


def increment_turn_count(old_game_state, new_game_state, moved_pieces, number_of_turns):
    if len(moved_pieces) > 0:
        new_game_state["turn_count"] = old_game_state["turn_count"] + number_of_turns

# do not allow for updates to graveyard
def prevent_client_side_updates_to_graveyard(old_game_state, new_game_state):
    new_game_state["graveyard"] = old_game_state["graveyard"]

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
                    import traceback
                    logger.error(f"Unable to determine move for {moved_piece['piece']['type']} due to: {traceback.format_exc(e)}")
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
        if count_of_pieces_on_new_state > 1:
            for moved_piece in moved_pieces:
                if "king" in moved_piece.get("piece"):
                    has_king_moved = True
                if "rook" in moved_piece.get("piece"):
                    has_rook_moved = True

            if not (has_king_moved and has_rook_moved):
                logger.error("A castle was not detected and more than one piece has moved")
                is_valid_game_state = False

    return is_valid_game_state


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
def cleanse_stunned_pieces(new_game_state):
    # iterate through the entire board
    for row in new_game_state["board_state"]:
        for square in row:
            # if the square is present iterate through it
            if square:
                for piece in square:
                    # if piece is on moving side and is stunned, cleanse
                    if piece.get("is_stunned", False) and piece.get("turn_stunned_for", 0) < new_game_state["turn_count"]:
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


def check_for_disappearing_pieces(
    old_game_state, 
    new_game_state, 
    moved_pieces, 
    is_valid_game_state, 
    capture_positions, 
    is_pawn_exchange_possible
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
                if "pawn" in moved_piece["piece"]["type"] and is_pawn_exchange_possible[moved_piece["side"]]:
                    captured_piece_accounted_for = True
            
            if not captured_piece_accounted_for and new_game_state["bishop_special_captures"]:
                # check to see if piece was captured via full bishop debuff stacked
                if moved_piece["piece"]["type"] == new_game_state["bishop_special_captures"][0]["type"]:
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
            moves_info = moves.get_moves(old_game_state, new_game_state, new_game_state["position_in_play"], piece)
            if "king" in piece.get("type"):
                moves_info = trim_king_moves(moves_info, old_game_state, new_game_state, moved_piece["side"])
        except Exception as e:
            import traceback
            logger.error(f"Unable to determine move for {piece} due to: {traceback.format_exc(e)}")
        
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
    def list_difference(list1, list2):
        result = list1[:]  # Make a copy of list1
        for item in list2:
            if item in result:
                result.remove(item)
        return result
    
    for side in new_game_state["captured_pieces"]:
        for piece in list_difference(new_game_state["captured_pieces"][side], old_game_state["captured_pieces"][side]):
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


def get_move_counts(moved_pieces):
    move_count_for_white, move_count_for_black = 0, 0
    for moved_piece in moved_pieces:        
        if moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
            if moved_piece["side"] == "white":
                move_count_for_white += 1
            else:
                move_count_for_black += 1
    return move_count_for_white, move_count_for_black


def invalidate_game_if_more_than_one_side_moved(move_count_for_white, move_count_for_black, is_valid_game_state):
    # if more than one side has pieces that's moved, invalidate 
    if move_count_for_white > 0 and move_count_for_black > 0: 
        logger.error("More than one side have pieces that have moved")
        is_valid_game_state = False
    return is_valid_game_state


def check_is_pawn_exhange_is_possible(old_game_state, new_game_state, moved_pieces):
    is_pawn_exchange_possible = {"white": False, "black": False}

    for side in old_game_state["captured_pieces"]:
        for moved_piece in moved_pieces:
            if side != moved_piece["side"]:
                continue
                
            if moved_piece["current_position"][0] is None and "pawn" in moved_piece["piece"]["type"]:
                previous_position = moved_piece['previous_position']
                square_on_current_game_state = new_game_state["board_state"][previous_position[0]][previous_position[1]]
                if square_on_current_game_state and all(side == piece["type"].split("_")[0] for piece in square_on_current_game_state):
                    is_pawn_exchange_possible[side] = True
    return is_pawn_exchange_possible


def get_gold_spent(old_game_state, moved_pieces):
    gold_spent = {"white": 0, "black": 0}
    for moved_piece in moved_pieces:
    # if a piece has spawned without being exchanged for a pawn
    # take note of gold count that is supposed to be spent to obtain it
        if moved_piece["current_position"][0] is not None \
        and moved_piece["previous_position"][0] is None \
        and not any(p['previous_position'] == moved_piece["current_position"] for p in moved_pieces if p["previous_position"][0] is not None):          
            gold_spent[moved_piece["side"]] += get_piece_value(moved_piece["piece"]["type"])
    return gold_spent


def invalidate_game_if_too_much_gold_is_spent(old_game_state, gold_spent, is_valid_game_state):
    for side in old_game_state["gold_count"]:
        if gold_spent[side] > old_game_state["gold_count"][side]:
            logger.error(f"More gold has been spent for {side} than {side} currently has ({gold_spent[side]} gold vs. {old_game_state['gold_count'][side]} gold)")
            is_valid_game_state = False
    return is_valid_game_state


def clean_bishop_special_captures(new_game_state):
    new_game_state["bishop_special_captures"] = []


def handle_pieces_with_full_bishop_debuff_stacks(
    old_game_state,
    new_game_state,
    moved_pieces,
    is_valid_game_state,
    capture_positions
):

    def get_pieces_with_three_bishop_stacks_from_state(game_state):
        output = []
        # [
        #   {
        #       "piece": <piece dictionary>,
        #       "position": [i, j]
        #   }
        # ]
        for i, row in enumerate(game_state["board_state"]):
            for j, square in enumerate(row):
                if square:
                    for piece in square:
                        if piece.get("bishop_debuff", 0) == 3:
                            output.append({
                                "piece": piece.copy(), "position": [i, j]
                            })
        return output
    
    
    def did_piece_get_full_bishop_debuffs_this_turn(old_game_state, new_piece_info):
        row = new_piece_info["position"][0]
        col = new_piece_info["position"][1]
        square = old_game_state["board_state"][row][col]
        if not square:
            return False
        for piece in square:
            if piece["type"] == new_piece_info["piece"]["type"] and \
            new_piece_info["piece"].get("bishop_debuff", 0) == 3 and \
            piece.get("bishop_debuff", 0) == 2:
                return True
        return False
    
    def did_piece_get_spared_this_turn_from_special_bishop_capture(new_game_state, old_piece_info):
        row = old_piece_info["position"][0]
        col = old_piece_info["position"][1]
        square = new_game_state["board_state"][row][col]
        if not square:
            return False
        
        for piece in square:
            if piece["type"] == old_piece_info["piece"]["type"] and piece.get("bishop_debuff", 0) == 0:
                return True
        return False

    def more_than_one_side_has_pieces_captured(old_game_state, new_game_state):
        return len(old_game_state["captured_pieces"]["white"]) != len(new_game_state["captured_pieces"]["white"]) and \
        len(old_game_state["captured_pieces"]["black"]) != len(new_game_state["captured_pieces"]["black"])
        
    def have_pieces_have_been_captured(old_game_state, new_game_state):
        return len(old_game_state["captured_pieces"]["white"]) != len(new_game_state["captured_pieces"]["white"]) or \
        len(old_game_state["captured_pieces"]["black"]) != len(new_game_state["captured_pieces"]["black"])

    should_increment_turn_count = True
    pieces_with_three_bishop_stacks_this_turn = get_pieces_with_three_bishop_stacks_from_state(new_game_state)
    sides_from_with_three_bishop_stacks_this_turn = [piece_info["piece"]["type"].split("_")[0] for piece_info in pieces_with_three_bishop_stacks_this_turn]
    pieces_with_three_bishop_stacks_last_turn = get_pieces_with_three_bishop_stacks_from_state(old_game_state)

    if pieces_with_three_bishop_stacks_this_turn:
        new_game_state["position_in_play"] = [None, None]
    # [
    #   {
    #       "piece": <piece dictionary>,
    #       "position": [i, j]
    #   }
    # ]
        # scenario 0 - catch all - more than one side has 3 bishop debuffs 
        #            - invalidate game
    if "white" in sides_from_with_three_bishop_stacks_this_turn and \
        "black" in sides_from_with_three_bishop_stacks_this_turn:
        logger.error("More than one side has full bishop debuff stacks")
        is_valid_game_state = False
        should_increment_turn_count = False
        # scenario 1 - (can be any) pieces on the board have third bishop debuff and did not have all three last turn 
        #            - or they had all three last turn but another piece with a third bishop debuff was dealt with instead
        #            - turn count is not being incremented
    elif any([did_piece_get_full_bishop_debuffs_this_turn(old_game_state, piece_info) for piece_info in pieces_with_three_bishop_stacks_this_turn]):
        should_increment_turn_count = False
        # scenario 2 - illegal move is attempted instead of dealing with bishop debuffs
        #            - search through moved pieces and invalidate game state if any pieces moved (valid old position and new position) if there's any third bishop buff active in old_game_state
    elif pieces_with_three_bishop_stacks_last_turn and \
    len([moved_piece for moved_piece in moved_pieces if moved_piece["previous_position"][0] is not None and moved_piece["current_position"][0] is not None]) > 0:
        logger.error("Illegal move was attempted instead of dealing with full bishop debuff stacks")
        is_valid_game_state = False
        should_increment_turn_count = False
        # scenario 3 - a piece that had third bishop debuff in the previous game state has no debuffs present in the current game state
        #            - player spared piece
        #            - turn count is being incremented
        #            - (technically allow sparing of multiple pieces since this isn't game breaking behavior)
    elif all([did_piece_get_spared_this_turn_from_special_bishop_capture(new_game_state, piece_info) for piece_info in pieces_with_three_bishop_stacks_last_turn]):
        should_increment_turn_count = True
        # scenario 4 - more than one piece has been captured
    elif (pieces_with_three_bishop_stacks_this_turn or pieces_with_three_bishop_stacks_last_turn) and \
    more_than_one_side_has_pieces_captured(old_game_state, new_game_state):
        logger.error("More than one side has pieces captured after dealing with full bishop debuff stacks")
        is_valid_game_state = False
        should_increment_turn_count = False
        # scenario 5 - there is a piece in the moved_pieces array that shows that a piece was captured (via bishop debuffs)
        #            - player captured piece and game has to ensure that state is not invalidated later on 
        #              by appending captured piece's position to capture_positions
        #            - turn count is being incremented only if there are no other pieces to spare or capture
    elif pieces_with_three_bishop_stacks_last_turn and \
    have_pieces_have_been_captured(old_game_state, new_game_state):
        if not new_game_state["bishop_special_captures"]:
            logger.error("Bishop special capture positions not properly marked even though piece has been captured")
            is_valid_game_state = False
            should_increment_turn_count = False
        else:
            captured_side = new_game_state["bishop_special_captures"][0]["type"].split("_")[0]
            opposite_side = "white" if captured_side == "black" else "black"
            is_found = False
            for row in range(0, len(new_game_state["board_state"])):
                for col in range(0, len(new_game_state["board_state"])):
                    if is_found:
                        break
                    new_square = new_game_state["board_state"][row][col]

                    if not new_square:
                        continue

                    for piece in new_square:
                        if piece.get("type") == f"{opposite_side}_bishop":
                            moves_info = moves.get_moves_for_bishop(old_game_state, old_game_state.get("previous_state"), [row, col])
                            if new_game_state["bishop_special_captures"][0]["position"] in moves_info["possible_moves"] or \
                            new_game_state["bishop_special_captures"][0]["position"] in [possible_capture[1] for possible_capture in moves_info["possible_captures"]]:
                                # "possible_captures": [[[row, col], [row, col]], ...] - first position is where piece has to move to capture piece in second position
                                new_capture_position = [[row, col], new_game_state["bishop_special_captures"][0]["position"]]
                                is_found = True
            should_increment_turn_count = len(pieces_with_three_bishop_stacks_this_turn) == 1
            if not is_found:
                is_valid_game_state = False
                logger.error(f'Unable to find a {opposite_side} bishop that could capture {new_game_state["bishop_special_captures"][0]["type"]}')        
            else:
                capture_positions.append(new_capture_position)
                # find bishop responsible and apply energize stacks in this scenario
                # HEAVY ASSUMPTION: only one piece in latest_movement field at a time (except for castling)
                for entry in new_game_state["latest_movement"]["record"]:
                    if entry["piece"]["type"] == f"{opposite_side}_bishop":
                        # an additional check to see if bishop's current position can apply bishop debuff to captured piece
                        try:
                            moves_info = moves.get_moves_for_bishop(
                                curr_game_state=old_game_state, 
                                prev_game_state=old_game_state.get("previous_state"), 
                                curr_position=entry["current_position"]
                            )
                            
                            if new_capture_position[1] not in [possible_capture[1] for possible_capture in moves_info["possible_captures"]]:
                                raise Exception("Last moved bishop cannot capture the captured piece")
                        except Exception as e:
                            logger.error(f'Unable to find a {opposite_side} bishop to give energize stacks for bishop debuff capture at {entry["current_position"]}: {e}')        
                            is_valid_game_state = False
                        else:
                            for piece in new_game_state["board_state"][entry["current_position"][0]][entry["current_position"][1]]:
                                piece["energize_stacks"] += 10

                                if piece["energize_stacks"] > 100:
                                    piece["energize_stacks"] = 100

    return is_valid_game_state, should_increment_turn_count


def record_moved_pieces_this_turn(new_game_state, moved_pieces):
    def is_captured_or_spawned(moved_pieces_entry):
        return moved_pieces_entry["previous_position"][0] is None \
        or  moved_pieces_entry["current_position"][0] is None
    filtered_moved_pieces = [entry for entry in moved_pieces if not is_captured_or_spawned(entry)]

    # in theory filtered_moved_pieces should only have one moved piece
    # except when performing castling but this behavior is checked elsewhere
    
    if filtered_moved_pieces:
        new_game_state["latest_movement"] = {
            "turn_count": new_game_state["turn_count"],
            "record": filtered_moved_pieces
        }
    
    # keep the previous record if there are no new moved pieces
    # to faciliate record keeping for granting bishop energize stacks
    # to bishops that perform special captures with their debuff


# old game's turn count is representative of what side should be moving (even is white, odd is black)
def invalidate_game_if_wrong_side_moves(moved_pieces, is_valid_game_state, old_game_turn_count):
    side_that_should_be_moving = "white" if not old_game_turn_count % 2 else "black"
    for side in [piece_info["side"] for piece_info in moved_pieces if piece_info["previous_position"][0] is not None and piece_info["current_position"][0] is not None]:
        if side != side_that_should_be_moving and side != "neutral":
            logger.error(f"{side} moved instead of {side_that_should_be_moving}")
            is_valid_game_state = False
    return is_valid_game_state


# new game's turn count is representative of what side should be moving next turn (even is white, odd is black)
def are_all_non_king_pieces_stunned(new_game_state):
    new_game_turn_count = new_game_state["turn_count"]
    side_that_should_be_moving_next_turn = "white" if not new_game_turn_count % 2 else "black"
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


def can_king_move(old_game_state, new_game_state):
    new_game_turn_count = new_game_state["turn_count"]
    side_that_should_be_moving_next_turn = "white" if not new_game_turn_count % 2 else "black"
    output = False
    unsafe_positions = get_unsafe_positions_for_king(old_game_state, new_game_state)
    for i in range(len(new_game_state["board_state"])):
        for j in range(len(new_game_state["board_state"][0])):
            square = new_game_state["board_state"][i][j]

            if square:
                for piece in square:
                    if piece.get("type") == f"{side_that_should_be_moving_next_turn}_king":
                        output = len(
                            [
                                move for move in moves.get_moves_for_king(
                                    new_game_state,
                                    old_game_state,
                                    [i, j]
                                )["possible_moves"] if move not in unsafe_positions[side_that_should_be_moving_next_turn]
                            ]
                        ) > 0
    return output


def get_unsafe_positions_for_king(old_game_state, new_game_state):
    output = {
        "white": set(),
        "black": set()
    }
    # iterate through board
    for row in range(len(new_game_state["board_state"])):
        for col in range(len(new_game_state["board_state"][0])):
            # for every square iterate through the pieces
            square = new_game_state["board_state"][row][col] or []
            for piece in square:
                # if piece is white or black
                if "king" not in piece.get("type") and ("white" in piece.get("type", "") or "black" in piece.get("type", "")):
                    side = piece["type"].split("_")[0]
                    opposite_side = "white" if side == "black" else "black"
                    moves_info = moves.get_moves(old_game_state, new_game_state, [row, col], piece)
                    # get second positions from all possible captures
                    # get all positions from possible moves (kings are not included in possible captures)
                    # add both to opposite side's unsafe position array
                    output[opposite_side] = output[opposite_side].union({tuple(possible_capture[1]) for possible_capture in moves_info["possible_captures"]})
                    output[opposite_side] = output[opposite_side].union({tuple(possible_move) for possible_move in moves_info["possible_moves"]})
                # if piece is neutral
                elif "neutral" in piece.get("type", ""):
                    # add current square and all adjacent squares to both sides of unsafe position array
                    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]

                    for delta in deltas:
                        position = (row+delta[0], col+delta[1])
                        if position[0] < 0 or position[0] >= 8 or position[1] < 0 or position[1] >= 8:
                            continue
                        output["white"] = output["white"].union({position})
                        output["black"] = output["black"].union({position})
    
    output = {side: [list(position_tuple) for position_tuple in output[side]] for side in output}
    # return {
    #   "white": [[row1, col1], ... ]
    #   "black": [[row1, col1], ... ]
    # }
    return output


def trim_moves(moves_info, unsafe_position_for_one_side):
    moves_info_copy = copy.deepcopy(moves_info)
    unsafe_positions_set = set([tuple(position) for position in unsafe_position_for_one_side])

    i = 0
    while i < len(moves_info_copy["possible_moves"]):
        if tuple(moves_info_copy["possible_moves"][i]) in unsafe_positions_set:
            moves_info_copy["possible_moves"].pop(i)
        else:
            i += 1

    i = 0
    while i < len(moves_info_copy["possible_captures"]):
        if tuple(moves_info_copy["possible_captures"][0][i]) in unsafe_positions_set:
            moves_info_copy["possible_captures"][0].pop(i)
        else:
            i += 1
    
    return moves_info_copy


def was_a_new_position_in_play_selected(moved_pieces, old_game_state, new_game_state):
    return not len([mp for mp in moved_pieces if mp["previous_position"][0] is not None and mp["current_position"][0] is not None]) and \
    old_game_state["position_in_play"] != new_game_state["position_in_play"]


# assumption is that there is a valid position_in_play in the new_game_state before using this function
def does_position_in_play_match_turn(old_game_state, new_game_state):
    side_that_should_be_moving = "white" if not old_game_state["turn_count"] % 2 else "black"

    square = old_game_state["board_state"][new_game_state["position_in_play"][0]][new_game_state["position_in_play"][1]] or []

    for piece in square:
        if side_that_should_be_moving in piece.get("type", ""):
            return True
        
    return False


def verify_queen_reset_turn_is_valid(
    old_game_state,
    new_game_state,
    moved_pieces,
    is_valid_game_state
):
    moving_side = "white" if not bool(old_game_state["turn_count"] % 2) else "black"
    # check for proper queen moving or that proper queen is set as the position in play
    proper_queen_found = False
    is_proper_queen_in_play = False

    for moved_piece in moved_pieces:
        if moved_piece["side"] == moving_side and \
        moved_piece["previous_position"][0] is not None and \
        moved_piece["current_position"][0] is not None:
            piece_type = moved_piece["piece"].get("type")
            if "queen" in piece_type:
                proper_queen_found = True
            else:
                is_valid_game_state = False
                logger.error(f"A non-queen piece moved for {moving_side} instead of the queen using its turn reset")
    
    if new_game_state["position_in_play"][0] is not None:
        position_in_play = new_game_state["position_in_play"]
        square_in_play = new_game_state["board_state"][position_in_play[0]][position_in_play[1]] or []
        is_proper_queen_in_play = any(f"{moving_side}_queen" == piece.get("type") for piece in square_in_play)

    if not proper_queen_found and not is_proper_queen_in_play:
        is_valid_game_state = False
        logger.error(f"{moving_side}'s queen is not in play and has not moved despite its turn reset")

    return is_valid_game_state


# conditionally mutates new_game_state
def reset_queen_turn_on_kill_or_assist(old_game_state, new_game_state, moved_pieces, should_increment_turn_count):
    moving_side = "white" if not bool(old_game_state["turn_count"] % 2) else "black"
    for i in range(len(old_game_state["board_state"])):
        row = old_game_state["board_state"][i]
        for j in range(len(row)):
            square = row[j] or []
            for piece in square:
                if piece["type"] == f"{moving_side}_queen":
                    queen_possible_moves_and_captures = moves.get_moves_for_queen(
                        curr_game_state=old_game_state, 
                        prev_game_state=old_game_state.get("previous_state"), 
                        curr_position=[i, j]
                    )

                    for moved_piece in moved_pieces:
                        if moved_piece["current_position"][0] is None and \
                        (
                            # assist condition for queen reset
                            moved_piece["previous_position"] in queen_possible_moves_and_captures["possible_moves"] or \
                            # capture condition for queen reset
                            moved_piece["previous_position"] in [capture_info[1] for capture_info in queen_possible_moves_and_captures["possible_captures"]]
                        ):
                            new_game_state["queen_reset"] = True
                            should_increment_turn_count = False
    return should_increment_turn_count


# conditionally mutates new_game_state
def set_queen_as_position_in_play(old_game_state, new_game_state):
    moving_side = "white" if not bool(old_game_state["turn_count"] % 2) else "black"
    for i in range(len(new_game_state["board_state"])):
        row = new_game_state["board_state"][i]
        for j in range(len(row)):
            square = row[j] or []
            for piece in square:
                if piece["type"] == f"{moving_side}_queen":
                    new_game_state["position_in_play"] = [i, j]


# conditionally mutates new_game_state
def spawn_sword_in_the_stone(new_game_state):
    if new_game_state["turn_count"] and not new_game_state["turn_count"] % 10:
        row_range = range(2, 6)
        candidate_squares = []
        for i in row_range:
            for j in range(8):
                if not new_game_state["board_state"][i][j]:
                    candidate_squares.append([i, j])
        if candidate_squares:
            new_game_state["sword_in_the_stone_position"] = random.choice(candidate_squares)


def exhaust_sword_in_the_stone(new_game_state, moved_pieces):
    for moved_piece in moved_pieces:
        if new_game_state["sword_in_the_stone_position"] == moved_piece["current_position"] and \
        "king" in moved_piece["piece"].get("type"):
                new_game_state["sword_in_the_stone_position"] = None
                for piece in new_game_state["board_state"][moved_piece["current_position"][0]][moved_piece["current_position"][1]]:
                    if piece.get("type") == moved_piece["piece"].get("type"):
                        if "check_protection" in piece and isinstance(piece["check_protection"], int):
                            piece["check_protection"] += 1
                        else:
                            piece["check_protection"] = 1


def trim_king_moves(moves_info, old_game_state, new_game_state, side):
    unsafe_positions = get_unsafe_positions_for_king(old_game_state, new_game_state)
    trimmed_moves_info = trim_moves(moves_info, unsafe_positions[side])
    return trimmed_moves_info