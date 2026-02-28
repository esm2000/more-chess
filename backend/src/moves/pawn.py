from src.moves._helpers import (
    evaluate_current_position,
    process_possible_moves_dict,
    _add_marked_for_death_threats,
    _is_path_clear,
    _is_diagonal_path_blocked,
    _is_baron_immune,
    _add_forward_capture,
)


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

    # check to see if a piece with the board herald buff is nearby
    board_herald_buff_active = False
    baron_buff_active = False
    dragon_buff = 0

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for delta in deltas:
        position = [curr_position[0] + delta[0], curr_position[1] + delta[1]]

        if position[0] > 7 or position[0] < 0 or position[1] > 7 or position[1] < 0:
            continue

        square = curr_game_state["board_state"][position[0]][position[1]] or []

        for piece in square:
            if side in piece.get("type", "") and piece.get("board_herald_buff", False):
                board_herald_buff_active = True

    baron_buff_active = piece_in_play.get("baron_nashor_buff", False)

    # check and record what buffs that the pawn has
    pawn_buff = piece_in_play.get("pawn_buff", 0)
    dragon_buff = piece_in_play.get("dragon_buff", 0)


    possible_moves = []
    possible_captures = []
    threatening_move = []

    pawn_range = 2 if dragon_buff >= 1 else 1
    # if square ahead is blank or only has neutral monsters add to list of possible moves
    for distance in range(1, pawn_range+1):
        row_ahead = curr_position[0] + (-distance if side == "white" else distance)
        if row_ahead > -1 and row_ahead < 8:
            modifier = -1 if side == "white" else 1
            squares_ahead = [curr_game_state["board_state"][curr_position[0] + (modifier*d)][curr_position[1]] or [] for d in range(1, distance+1)]

            are_squares_ahead_free = _is_path_clear(squares_ahead, side, opposing_side, dragon_buff)

            if len(squares_ahead) == 1:
                are_squares_leading_to_square_ahead_free = True
            else:
                are_squares_leading_to_square_ahead_free = _is_path_clear(squares_ahead[:-1], side, opposing_side, dragon_buff)

            if are_squares_ahead_free:
                extra_row_ahead = curr_position[0] + (-distance - 1 if side == "white" else distance + 1)
                if extra_row_ahead > -1 and extra_row_ahead < 8:
                    # if pawn is in starting square include square two squares ahead if square ahead is blank or neutral monster is present
                    starting_row = 6 if side == "white" else 1
                    square_extra_row_ahead = curr_game_state["board_state"][extra_row_ahead][curr_position[1]] or []
                    is_square_two_squares_ahead_free = not square_extra_row_ahead or any(["neutral" in piece_in_square.get("type") for piece_in_square in square_extra_row_ahead])
                    if curr_position[0] == starting_row and is_square_two_squares_ahead_free:
                        possible_moves.append([extra_row_ahead, curr_position[1]])

                # are_squares_ahead_free can be True if dragon_buff is 3 and there is a ally pawn in the path
                if dragon_buff == 3 and \
                    any(f"{side}_pawn" == piece.get("type") for piece in (curr_game_state["board_state"][row_ahead][curr_position[1]] or [])):
                    continue

                if dragon_buff >= 4 and \
                    any(side in piece.get("type") for piece in (curr_game_state["board_state"][row_ahead][curr_position[1]] or [])):
                    continue

                possible_moves.append([row_ahead, curr_position[1]])

            # not having the baron buff and an opposing pawn having the baron buff makes the opposing pawn immune
            if not _is_baron_immune(squares_ahead[-1], opposing_side, baron_buff_active):
                move_position = [row_ahead, curr_position[1]]

                # if capture point advantage is +2 or pawn buff = 1 and enemy pawn is present on square ahead add to list of possible moves
                if pawn_buff >= 1 and \
                not are_squares_ahead_free and \
                are_squares_leading_to_square_ahead_free and \
                any(piece.get("type", "None") == f"{opposing_side}_pawn" and piece.get("pawn_buff", 0) < 1 for piece in squares_ahead[-1]):
                    possible_moves.append(move_position)
                    possible_captures.append([move_position, move_position])

                # if the board herald buff is active and enemy piece is present on square ahead add to list of possible moves
                if board_herald_buff_active and \
                not are_squares_ahead_free and \
                are_squares_leading_to_square_ahead_free:
                    _add_forward_capture(possible_moves, possible_captures, threatening_move, squares_ahead[-1], move_position, opposing_side)

                # if the baron nashor buff is active and enemy piece is present on square ahead add to list of possible moves
                if baron_buff_active and \
                not are_squares_ahead_free and \
                are_squares_leading_to_square_ahead_free and \
                not any(piece.get("baron_nashor_buff") and f"{opposing_side}_pawn" == piece.get("type") for piece in squares_ahead[-1]):
                    _add_forward_capture(possible_moves, possible_captures, threatening_move, squares_ahead[-1], move_position, opposing_side)

            # check if diagonally forward adjacent squares have enemy non-king piece or neutral monster or a non pawn-buffed (2) pawn
            # and add it to list of possible moves
            diagonal_forward_adjacent_positions = [
                [row_ahead, curr_position[1] - distance], [row_ahead, curr_position[1] + distance]
            ]

            for i, diagonal_forward_adjacent_position in enumerate(diagonal_forward_adjacent_positions):
                modifier = -1 if not i else 1
                if diagonal_forward_adjacent_position[1] < 0 or diagonal_forward_adjacent_position[1] > 7:
                    continue

                square = curr_game_state["board_state"][diagonal_forward_adjacent_position[0]][diagonal_forward_adjacent_position[1]]
                row_modifier = -1 if side == "white" else 1
                squares_ahead = [curr_game_state["board_state"][curr_position[0]+(d*row_modifier)][curr_position[1]+(d*modifier)] or [] for d in range(1, distance+1)]

                if not square or _is_diagonal_path_blocked(squares_ahead[:-1], side, dragon_buff):
                    continue

                # not having the baron buff and an opposing pawn having the baron buff makes the opposing pawn immune
                if not _is_baron_immune(square, opposing_side, baron_buff_active):
                    if all((opposing_side in piece.get("type", "") or "neutral" in piece.get("type", "")) and \
                        not ("pawn" in piece.get("type", "") and piece.get("pawn_buff", 0) > 1) \
                        for piece in square):
                        if any("king" in piece.get('type', '') for piece in square):
                            threatening_move.append(diagonal_forward_adjacent_position)
                        else:
                            possible_moves.append(diagonal_forward_adjacent_position)
                            if not all("neutral" in piece.get("type", "") and piece.get("health", 0) != 1 for piece in square):
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
        lateral_square = curr_game_state["board_state"][lateral_position[0]][lateral_position[1]] or []

        # not having the baron buff and an opposing pawn having the baron buff makes the opposing pawn immune
        if not _is_baron_immune(lateral_square, opposing_side, baron_buff_active):
            opposing_starting_position = [6 if opposing_side == "white" else 1, lateral_position[1]]
            if prev_game_state:
                prev_opposing_starting_square = prev_game_state["board_state"][opposing_starting_position[0]][opposing_starting_position[1]]
            else:
                prev_opposing_starting_square = []
            curr_opposing_starting_square = curr_game_state["board_state"][opposing_starting_position[0]][opposing_starting_position[1]]

            en_passant_dest_row = curr_position[0] + (-1 if side == "white" else 1)
            if en_passant_dest_row < 0 or en_passant_dest_row > 7:
                continue
            destination_square = curr_game_state["board_state"][en_passant_dest_row][lateral_position[1]] or []
            if ((side == "black" and curr_position[0] == 4) or (side == "white" and curr_position[0] == 3)) and \
            (lateral_square and any(piece.get("type", "None") == f"{opposing_side}_pawn" for piece in lateral_square)) and \
            (prev_opposing_starting_square and any(piece.get("type", "None") == f"{opposing_side}_pawn" for piece in prev_opposing_starting_square)) and \
            (not curr_opposing_starting_square or all(piece.get("type", "None") != f"{opposing_side}_pawn" for piece in curr_opposing_starting_square)) and \
            (not destination_square) and \
            (all("king" not in piece.get("type", "None") for piece in destination_square)):
                possible_moves.append([en_passant_dest_row, lateral_position[1]])
                possible_captures.append([[en_passant_dest_row, lateral_position[1]], [curr_position[0] , lateral_position[1]]])

    if dragon_buff >= 5:
        _add_marked_for_death_threats(possible_moves, threatening_move, opposing_side, curr_game_state["board_state"])

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move})
