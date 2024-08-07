import copy 
from fastapi import Response
from mocks.empty_game import empty_game
from src.logging import logger
import src.api as api

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