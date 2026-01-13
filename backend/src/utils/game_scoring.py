from .board_analysis import get_piece_value


# gets the average piece value for each side
def get_average_piece_value_for_each_side(new_game_state):
    piece_values = {"white": 0, "black": 0}
    piece_counts = {"white": 0, "black": 0}

    for row in range(len(new_game_state['board_state'])):
        for col in range(len(new_game_state['board_state'])):
            square = new_game_state["board_state"][row][col] or []
            for piece in square:
                piece_type = piece.get("type", "")
                for side in ["white", "black"]:
                    if side in piece_type:
                        piece_values[side] += get_piece_value(piece_type)
                        piece_counts[side] += 1
                        break

    # Return averages (avoid division by zero)
    return {
        side: piece_values[side] / piece_counts[side] if piece_counts[side] > 0 else 0
        for side in ["white", "black"]
    }


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
    piece_values = get_average_piece_value_for_each_side(new_game_state)
    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]

    if capture_point_advantage == 0: 
        new_game_state["capture_point_advantage"] = None
    else:
        new_game_state["capture_point_advantage"] = [winning_side, capture_point_advantage]


def reassign_pawn_buffs(new_game_state):
    piece_values = get_average_piece_value_for_each_side(new_game_state)
    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]
    pawn_buff = capture_point_advantage if capture_point_advantage < 4 else 3 # capped at 3
    for row in range(8):
        for col in range(8):
            square = new_game_state["board_state"][row][col]
            if square:
                for i, piece in enumerate(square):
                    if "pawn" in piece.get("type", ""):
                        if piece.get("side") == winning_side:
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = pawn_buff
                        elif piece.get("side") == losing_side:
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = 0