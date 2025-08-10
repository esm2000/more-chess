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
