from src.utility import evaluate_current_position
def get_moves():
    pass

# get_moves_for_x() returns possible_moves_dict
# {
#   "possible_moves": [[row, col], ...] - positions where piece can move
#   "possible_captures": [[[row, col], [row, col]], ...] - first position is where piece has to move to capture piece in second position
# }

def get_moves_for_pawn(curr_game_state, prev_game_state, curr_position):
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "pawn" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No pawn found at position {curr_position}")
    
    # TODO: check and record if game-wide buffs are active 
    
    # check and record what buffs that the pawn has 
    pawn_buff = piece.get("pawn_buff", 0)
    
    possible_moves = []
    possible_captures = []

    # if square ahead is blank or only has neutral monsters add to list of possible moves
    row_ahead = curr_position[0] + (-1 if side == "white" else 1)
    if row_ahead > -1 and row_ahead < 8:
        
        square_ahead = curr_game_state["board_state"][row_ahead][curr_position[1]]
        is_square_ahead_free = not square_ahead or any("neutral" in piece.get("type", "None") for piece in square_ahead)
        
        if is_square_ahead_free:
            possible_moves.append([row_ahead, curr_position[1]])

            two_rows_ahead = curr_position[0] + (-2 if side == "white" else 2)
            if two_rows_ahead > -1 and two_rows_ahead < 8:
                # if pawn is in starting square include square two squares ahead if square ahead is blank or neutral monster is present
                starting_row = 6 if side == "white" else 1
                square_two_squares_ahead = curr_game_state["board_state"][two_rows_ahead][curr_position[1]]
                is_square_two_squares_ahead_free = not square_two_squares_ahead or any(["neutral" in piece_in_square.get("type") for piece_in_square in square_two_squares_ahead])
                if curr_position[0] == starting_row and is_square_two_squares_ahead_free:
                    possible_moves.append([two_rows_ahead, curr_position[1]])

        # if capture point advantage is +2 or pawn buff = 1 and enemy pawn is present on square ahead add to list of possible moves
        if pawn_buff >= 1 and \
        not is_square_ahead_free and \
        any(piece.get("type", "None") == f"{opposing_side}_pawn" and piece.get("pawn_buff", 0) < 1 for piece in square_ahead):
            possible_moves.append([row_ahead, curr_position[1]])
            possible_captures.append([[row_ahead, curr_position[1]], [row_ahead, curr_position[1]]])

        # check if diagonally forward adjacent squares have enemy non-king piece or neutral monster or a non pawn-buffed (2) pawn 
        # and add it to list of possible moves
        diagonal_forward_adjacent_positions = [
            [row_ahead, curr_position[1] - 1], [row_ahead, curr_position[1] + 1]
        ]

        for diagonal_forward_adjacent_position in diagonal_forward_adjacent_positions:
            if diagonal_forward_adjacent_position[1] < 0 or diagonal_forward_adjacent_position[1] > 7:
                continue

            square = curr_game_state["board_state"][diagonal_forward_adjacent_position[0]][diagonal_forward_adjacent_position[1]]

            if not square:
                continue

            if all("king" not in piece.get("type", None) and \
                   (opposing_side in piece.get("type", None) or "neutral" in piece.get("type", None)) and \
                   not ("pawn" in piece.get("type", None) and piece.get("pawn_buff", 0) > 1) \
                   for piece in square):
                possible_moves.append(diagonal_forward_adjacent_position)
                if not all("neutral" in piece.get("type", None) and piece.get("health", 0) != 1 for piece in square):
                    possible_captures.append([diagonal_forward_adjacent_position, diagonal_forward_adjacent_position])

    # En passant

    # if side is black and on row 4 or side is white and on row 3
    # and there's a opposing side's pawn next to the piece in play
    # that happened to be in its original row in the previous game state
    lateral_positions = [
        [curr_position[0] , curr_position[1] - 1], [curr_position[0] , curr_position[1] + 1]
    ]

    for lateral_position in lateral_positions:
        if lateral_position[1] < 0 or lateral_position[1] > 7:
            continue
        lateral_square = curr_game_state["board_state"][lateral_position[0]][lateral_position[1]]
        opposing_starting_position = [6 if opposing_side == "white" else 1, lateral_position[1]]
        if prev_game_state:
            prev_opposing_starting_square = prev_game_state["board_state"][opposing_starting_position[0]][opposing_starting_position[1]]
        else:
            prev_opposing_starting_square = []
        curr_opposing_starting_square = curr_game_state["board_state"][opposing_starting_position[0]][opposing_starting_position[1]]
        
        if ((side == "black" and curr_position[0] == 4) or (side == "white" and curr_position[0] == 3)) and \
        (lateral_square and any(piece.get("type", "None") == f"{opposing_side}_pawn" for piece in lateral_square)) and \
        (prev_opposing_starting_square and any(piece.get("type", "None") == f"{opposing_side}_pawn" for piece in prev_opposing_starting_square)) and \
        (not curr_opposing_starting_square or all(piece.get("type", "None") != f"{opposing_side}_pawn" for piece in curr_opposing_starting_square)) and \
        (all("king" not in piece.get("type", "None") for piece in (curr_game_state["board_state"][curr_position[0]][lateral_position[1]] or []))):
            possible_moves.append([curr_position[0] + (-1 if side == "white" else 1), lateral_position[1]])
            possible_captures.append([[curr_position[0] + (-1 if side == "white" else 1), lateral_position[1]], [curr_position[0] , lateral_position[1]]])
    
    
    return {"possible_moves": possible_moves, "possible_captures": possible_captures}


def get_moves_for_knight(curr_game_state, prev_game_state, curr_position):
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "knight" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No pawn found at position {curr_position}")
    
    possible_moves = []
    possible_captures = []
    # relative_positions represent all possible moves knight can take
    relative_positions = [[1, -2], [1, 2], [2, -1], [2, 1], [-1, -2],  [-1, 2], [-2, -1], [-2, 1]]
    
    for relative_position in relative_positions:
        potential_position = [curr_position[0] + relative_position[0], curr_position[1] + relative_position[1]]

        if potential_position[0] < 0 or potential_position[0] > 7 or \
        potential_position[1] < 0 or potential_position[1] > 7:
            continue

        potential_position_free = True

        # checking to see if path is unblocked to potentional move
        for index_of_relative_position in range(2):
            if abs(relative_position[index_of_relative_position]) == 2:
                index_of_relative_position_with_absolute_value_of_2 = index_of_relative_position
        for j in range(2):
            relative_square = [None, None]
            relative_square[index_of_relative_position_with_absolute_value_of_2] = j + 1
            relative_square[0 if index_of_relative_position_with_absolute_value_of_2 else 1] = 0
            intermediate_square_on_the_way_to_destination = [curr_position[0] + relative_square[0], curr_position[1] + relative_square[1]]
            if curr_game_state["board_state"][intermediate_square_on_the_way_to_destination[0]][intermediate_square_on_the_way_to_destination[1]]:
                potential_position_free = False
        

        # if path is unblocked knight is free to move to position 
        if potential_position_free:
            potential_square = curr_game_state["board_state"][potential_position[0]][potential_position[1]]
            if not potential_square:
                possible_moves.append(potential_position)
            
            if potential_square and all('king' not in piece.get('type', 'None') for piece in potential_square):
                for piece in potential_square:
                    if (opposing_side in piece.get("type")):
                        possible_moves.append(potential_position)
                        possible_captures.append([potential_position, potential_position])
                        break
                    if len(potential_square) == 1 and "neutral" in piece.get("type"):
                        possible_moves.append(potential_position)
                        if piece.get("health", 0) == 1:
                            possible_captures.append([potential_position, potential_position])

    return {"possible_moves": possible_moves, "possible_captures": possible_captures}
                    

def get_moves_for_bishop():
    pass


def get_moves_for_rook():
    pass


def get_moves_for_queen():
    pass


def get_moves_for_king():
    pass