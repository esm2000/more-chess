import random


# conditionally mutates new_game_state
def spawn_sword_in_the_stone(old_game_state, new_game_state):
    if new_game_state["turn_count"] and not new_game_state["turn_count"] % 10 and old_game_state["turn_count"] % 10:
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
                    if piece.get("type", "") == moved_piece["piece"].get("type"):
                        if "check_protection" in piece and isinstance(piece["check_protection"], int):
                            piece["check_protection"] += 1
                        else:
                            piece["check_protection"] = 1
