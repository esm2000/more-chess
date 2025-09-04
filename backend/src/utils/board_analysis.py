from src.log import logger


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
            pieces_on_curr_square = [piece.get("type", "") for piece in curr_square]
            pieces_on_prev_square = [piece.get("type", "") for piece in prev_square]

            # check for any missing pieces from current board by getting diff
            pieces_missing_from_curr_board = list(set(pieces_on_prev_square) - set(pieces_on_curr_square))
            
            # check for any additonal pieces by getting opposite diff
            pieces_added_to_curr_board = list(set(pieces_on_curr_square) - set(pieces_on_prev_square))

            # iterate through both results and record results in output array 
            curr_square_dict = {}
            prev_square_dict = {}
            
            for piece in curr_square:
                curr_square_dict[piece.get("type", "")] = piece
            for piece in prev_square:
                prev_square_dict[piece.get("type", "")] = piece

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


def get_move_counts(moved_pieces):
    move_count_for_white, move_count_for_black = 0, 0
    for moved_piece in moved_pieces:        
        if moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
            if moved_piece["side"] == "white":
                move_count_for_white += 1
            else:
                move_count_for_black += 1
    return move_count_for_white, move_count_for_black


def evaluate_current_position(curr_position, curr_game_state):
    if curr_position[0] is None or curr_position[1] is None:
        raise Exception(f"Invalid position, {curr_position}, cannot have None value as a position")
    if curr_position[0] < -1 or curr_position[0] > 7 or curr_position[1] < -1 or curr_position[1] > 7:
        raise Exception(f"Invalid position, {curr_position}, out of bounds")
    if not curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        raise Exception(f"No piece at position {curr_position}")


def get_neutral_monster_slain_positions(moved_pieces):
    neutral_monster_slain_positions = []
    for moved_piece in moved_pieces:
        if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is None and moved_piece["previous_position"][0] is not None:
            neutral_monster_slain_positions.append(moved_piece["previous_position"])
    return neutral_monster_slain_positions