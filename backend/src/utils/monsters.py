import copy

from src.log import logger
from .board_analysis import get_neutral_monster_slain_positions


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
    
    if not monsters:
        return

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
                if "king" in piece.get("type", ""):
                    if "white" in piece["type"]:
                        game_state["white_defeat"] = True
                    else:
                        game_state["black_defeat"] = True
                    i += 1
                else:
                    game_state["graveyard"].append(piece.get("type", ""))
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
                        k = 0
                        while k < len(game_state["board_state"][i][j]):
                            piece = game_state["board_state"][i][j][k]
                            side = piece["type"].split("_")[0]
                            if side in sides:
                                neutral_kill_mark = piece.get("neutral_kill_mark", -1)

                                if neutral_kill_mark == game_state["turn_count"]:
                                    # if a king gets captured that's game over
                                    if "king" in piece["type"]:
                                        game_state["black_defeat"] = side == "black"
                                        game_state["white_defeat"] = side == "white"
                                        k += 1
                                    else:
                                        game_state["board_state"][i][j].remove(piece)
                                        game_state["graveyard"].append(piece.get("type", ""))
                                        # Don't increment k since we removed an element
                                elif game_state["turn_count"] - neutral_kill_mark > 2:
                                    game_state["board_state"][i][j][k]["neutral_kill_mark"] = game_state["turn_count"] + 2
                                    k += 1
                                else:
                                    k += 1
                            else:
                                k += 1



def damage_neutral_monsters(new_game_state, moved_pieces, capture_positions):
    for moved_piece in moved_pieces:
        # if a piece is on the same square or adjacent to neutral monsters, they should damage or kill them
        if moved_piece["previous_position"][0] is not None and moved_piece["current_position"][0] is not None:
            for neutral_monster in MONSTER_INFO:
                if is_neutral_monster_spawned(neutral_monster,new_game_state["board_state"]):
                    row_diff = abs(moved_piece["current_position"][0] - MONSTER_INFO[neutral_monster]["position"][0])
                    col_diff = abs(moved_piece["current_position"][1] - MONSTER_INFO[neutral_monster]["position"][1])
                    if row_diff in [-1, 0, 1] and col_diff in [-1, 0, 1]:
                        for i, piece in enumerate(new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]]):
                            if piece.get("type", "") == neutral_monster:
                                new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]][i]["health"] = piece["health"] - 1
                    
                                if new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]][i]["health"] < 1:
                                    neutral_monster_piece = new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]].pop(i)
                                    new_game_state["captured_pieces"][moved_piece["side"]].append(neutral_monster)
                                    moved_pieces.append({
                                        "piece": neutral_monster_piece,
                                        "side": "neutral",
                                        "previous_position": MONSTER_INFO[neutral_monster]["position"],
                                        "current_position": [None, None]
                                    })
                                    # Add capture information so handle_neutral_monster_buffs can find the captor
                                    capture_positions.append([moved_piece["current_position"], MONSTER_INFO[neutral_monster]["position"]])



# conditionally mutates new_game_state
def heal_neutral_monsters(old_game_state, new_game_state):
    turn_count = new_game_state["turn_count"]
    monster_info = copy.deepcopy(MONSTER_INFO)

    # neutral_attack_log example: {
    #   "neutral_dragon": {"turn": 12},
    #   "neutral_baron_harold": {"turn": 14}
    # }
    for monster in monster_info:
        position = monster_info[monster]["position"]
        max_health = monster_info[monster]["max_health"]
        last_turn_attacked = new_game_state["neutral_attack_log"].get(monster, {"turn": turn_count})["turn"]

        # attempt to find neutral monster for old_game_state and new_game_state
        old_index, new_index = None, None
        old_square = old_game_state["board_state"][position[0]][position[1]] or []
        for index in range(len(old_square)):
            if old_square[index].get("type") == monster:
                old_index = index
                break
        
        if old_index is None:
            continue

        new_square = new_game_state["board_state"][position[0]][position[1]] or []
        for index in range(len(new_square)):
            if new_square[index].get("type") == monster:
                new_index = index
                break

        # if you can't find neutral monster in new_game_state remove record of that neutral monster from neutral_attack_log in new game
        if new_index is None:
            new_game_state["neutral_attack_log"].pop(monster, None)

        # if the monster has been attacked, take note of the turn in neutral_attack_log
        elif old_square[old_index]["health"] > new_square[new_index]["health"]:
            new_game_state["neutral_attack_log"][monster] = {"turn": turn_count}
            
        # if the monster has not been attacked and the last turn it got attacked is at least 3 turns before the current one, regenerate the monster's health
        elif old_square[old_index]["health"] == new_square[new_index]["health"] and turn_count - last_turn_attacked >= 3:
            new_square[new_index]["health"] = max_health


def is_neutral_monster_spawned(neutral_monster_type, board_state):
    neutral_monster_position = MONSTER_INFO[neutral_monster_type]["position"]
    square = board_state[neutral_monster_position[0]][neutral_monster_position[1]]
    if not square:
        return False
    return any([piece.get("type", "") == neutral_monster_type for piece in square])


def is_neutral_monster_killed(moved_pieces):
    neutral_monster_slain_positions = get_neutral_monster_slain_positions(moved_pieces)

    for moved_piece in moved_pieces:
        if neutral_monster_slain_positions:
            if moved_piece["side"] != "neutral" and \
            moved_piece["current_position"][0] is not None:
                # Check if the piece is adjacent to ANY slain position
                for slain_position in neutral_monster_slain_positions:
                    if abs(moved_piece["current_position"][0] - slain_position[0]) in [0, 1] and \
                    abs(moved_piece["current_position"][1] - slain_position[1]) in [0, 1]:
                        return True
    return False


def handle_neutral_monster_buffs(moved_pieces, capture_positions, new_game_state, is_valid_game_state):
    # mark new buffs for any side that has captured a neutral monster
    # and apply buff if board herald buff acquired
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is None and moved_piece["previous_position"][0] is not None:
            captor = None
            captor_position = None

            for capture_info in capture_positions:
                if capture_info[1] != moved_piece["previous_position"]:
                    continue
                captor_position = capture_info[0]
                square = new_game_state["board_state"][captor_position[0]][captor_position[1]] or []

                if square:
                    captor = square[0]

            if not captor:
                neutral_monster_type = moved_piece["piece"].get("type", "Unknown")
                logger.error(f'Unable to find captor of {neutral_monster_type} (slain at {moved_piece["previous_position"]})')
                is_valid_game_state = False
            else:
                side = "white" if "white" in captor.get("type", "") else "black"
                neutral_monster_type = moved_piece["piece"]["type"].replace("neutral_", "")

                if neutral_monster_type == "dragon":
                    if new_game_state["neutral_buff_log"][side]["dragon"]["stacks"] < 5:
                        new_game_state["neutral_buff_log"][side]["dragon"]["stacks"] += 1
                    
                    new_game_state["neutral_buff_log"][side]["dragon"]["turn"] = new_game_state["turn_count"]
                else:
                    new_game_state["neutral_buff_log"][side][neutral_monster_type] = True

                    # grant board herald buff to captor if neutral_monster slain was board_herald
                    if neutral_monster_type == "board_herald":
                        new_game_state["board_state"][captor_position[0]][captor_position[1]][0]["board_herald_buff"] = True    
    # grant dragon and baron nashor buffs using neutral buff log (redundantly reapply all buffs just in case new pieces have been acquired through pawn exchange or the shop)
    for side in new_game_state["neutral_buff_log"]:
        if new_game_state["neutral_buff_log"][side]["baron_nashor"]:
            for row in range(len(new_game_state["board_state"])):
                for col in len(new_game_state["board_state"][0]):
                    square = new_game_state["board_state"][row][col] or []

                    for piece in square:
                        if piece["type"] == f"{side}_pawn":
                            piece["baron_nashor_buff"] = True
        
        if new_game_state["neutral_buff_log"][side]["dragon"]["stacks"]:
            for row in range(len(new_game_state["board_state"])):
                for col in range(len(new_game_state["board_state"][0])):
                    square = new_game_state["board_state"][row][col] or []

                    for piece in square:
                        if new_game_state["neutral_buff_log"][side]["dragon"]["stacks"] == 1:
                            if piece["type"] == f"{side}_pawn":
                                piece["dragon_buff"] = new_game_state["neutral_buff_log"][side]["dragon"]["stacks"]
                        elif new_game_state["neutral_buff_log"][side]["dragon"]["stacks"] >= 2 and new_game_state["neutral_buff_log"][side]["dragon"]["stacks"] <= 4:
                            if side in piece["type"]:
                                piece["dragon_buff"] = new_game_state["neutral_buff_log"][side]["dragon"]["stacks"]
                        elif new_game_state["neutral_buff_log"][side]["dragon"]["stacks"] == 5:
                            if side in piece["type"]:
                                # fifth dragon stack only lasts 3 turns
                                # (with new_game_state["turn_count"] already incremented three turns is covered by 5 turns ahead)
                                # 0th turn, 1st turn*, 2nd turn, 3rd turn*, 4 turn, 5th turn*
                                if new_game_state["turn_count"] < new_game_state["neutral_buff_log"][side]["dragon"]["turn"] + 6:
                                    piece["dragon_buff"] = 5
                                else:
                                    piece["dragon_buff"] = 4
                                
    return is_valid_game_state

