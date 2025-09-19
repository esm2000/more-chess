import copy

from src.utils.piece_mechanics import enable_adjacent_bishop_captures
from src.utils.board_analysis import evaluate_current_position
# get_moves() returns possible_moves_dict
# {
#   "possible_moves": [[row, col], ...] - positions where piece can move
#   "possible_captures": [[[row, col], [row, col]], ...] - first position is where piece has to move to capture piece in second position
#   "threatening_move": [[row, col]] - position where king of opposite side is threatened by the piece in its current position
#   "castle_moves": [[row, col]] - positions where piece can move to facilitate a castle
# }
def get_moves(old_game_state, new_game_state, curr_position, piece):
    if "pawn" in piece["type"]:
        moves_info = get_moves_for_pawn(
            curr_game_state=new_game_state, 
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    if "knight" in piece["type"]:
        moves_info = get_moves_for_knight(
            curr_game_state=new_game_state, 
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    if "bishop" in piece["type"]:
        moves_info = get_moves_for_bishop(
            curr_game_state=new_game_state, 
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    if "rook" in piece["type"]:
        moves_info = get_moves_for_rook(
            curr_game_state=new_game_state, 
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    if "queen" in piece["type"]:
        moves_info = get_moves_for_queen(
            curr_game_state=new_game_state, 
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    if "king" in piece["type"]:
        moves_info = get_moves_for_king(
            curr_game_state=new_game_state, 
            prev_game_state=old_game_state,
            curr_position=curr_position
        )
    return moves_info


# moves list is either list of possible moves or list of possible captures
def filter_moves_for_file_control(moves_list, curr_position, is_capture=False):
        center_squares = [
            [2, 2], [2, 3], [2, 4], [2, 5],
            [3, 2], [3, 3], [3, 4], [3, 5],
            [4, 2], [4, 3], [4, 4], [4, 5],
            [5, 2], [5, 3], [5, 4], [5, 5]
        ]
        index = 0
        while index < len(moves_list):
            move = moves_list[index] if not is_capture else moves_list[index][0]

            # determine if it's a vertical move
            if curr_position[1] == move[1]:
                # eliminate move if row 3 or 4 is passed and curr_position is not a center square
                if (
                    (curr_position[0] < 2 and move[0] > 5) or 
                    (curr_position[0] > 5 and move[0] < 2)
                ) and (curr_position not in center_squares):
                    moves_list.pop(index)
                    continue
            index += 1


def process_possible_moves_dict(curr_game_state, curr_position, side, possible_moves_dict, is_king=False):
    possible_moves_dict = enable_adjacent_bishop_captures(curr_game_state, side, possible_moves_dict)

    # remove moves and captures that involve moving to a sword in stone buff unless we're dealing with a king
    if not is_king and curr_game_state["sword_in_the_stone_position"]:
        possible_moves_dict["possible_moves"] = [move for move in possible_moves_dict["possible_moves"] if move != curr_game_state["sword_in_the_stone_position"]]
        possible_moves_dict["possible_captures"] = [capture for capture in possible_moves_dict["possible_captures"] if capture[0] != curr_game_state["sword_in_the_stone_position"]]
        
    # remove duplicates
    possible_captures_with_no_duplicates = []
    for entry in possible_moves_dict["possible_captures"]:
        if entry not in possible_captures_with_no_duplicates:
            possible_captures_with_no_duplicates.append(copy.deepcopy(entry))
    possible_moves_dict["possible_captures"] = possible_captures_with_no_duplicates

    # enforce file control - no vertical moves past the center of the board unless piece originates in center
    # apply filtering to both possible_moves and possible_captures
    filter_moves_for_file_control(possible_moves_dict["possible_moves"], curr_position)
    filter_moves_for_file_control(possible_moves_dict["possible_captures"], curr_position, is_capture=True)

    if "castle_moves" not in possible_moves_dict:
        possible_moves_dict["castle_moves"] = []
    return possible_moves_dict


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
    # check to see if a piece with the board herald buff is nearby 
    board_herald_buff_active = False
    baron_buff_active = False
    dragon_buff = 0

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for delta in deltas:
        position = curr_position
        position[0] += delta[0]
        position[1] += delta[1]

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
            
            # unit collision with ally pawns are allowed with three dragon buff stacks
            if dragon_buff == 3:
                are_squares_ahead_free = all(
                    [not square or
                    (any("neutral" in piece.get("type", "") for piece in square) and all(opposing_side not in piece.get("type", "") for piece in square)) or
                    any(f"{side}_pawn" == piece.get("type", "") for piece in square)
                    for square in squares_ahead]
                )
            # TODO: add separate logic for dragon_buff >= 4
            else:
                are_squares_ahead_free = all(
                    [not square or (any("neutral" in piece.get("type", "") for piece in square) and all(side not in piece.get("type", "") and opposing_side not in piece.get("type", "") for piece in square)) for square in squares_ahead]
                )

            if len(squares_ahead) == 1:
                are_squares_leading_to_square_ahead_free = True
            elif dragon_buff == 3:
                are_squares_leading_to_square_ahead_free = all(
                    [not square or
                    (any("neutral" in piece.get("type", "") for piece in square) and all(opposing_side not in piece.get("type", "") for piece in square)) or
                    any(f"{side}_pawn" == piece.get("type", "") for piece in square)
                    for square in squares_ahead[:-1]]
                )
            # TODO: add separate logic for dragon_buff >= 4
            else:
                are_squares_leading_to_square_ahead_free = all(
                    [not square or (any("neutral" in piece.get("type", "") for piece in square) and all(side not in piece.get("type", "") and opposing_side not in piece.get("type", "") for piece in square)) for square in squares_ahead[:-1]]
                )
            
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
                    
                # TODO: UNCOMMENT for 4+ stacks of dragon buff
                # if dragon_buff >= 4 and \
                #     any(opposing_side in piece.get("type") for piece in (curr_game_state["board_state"][row_ahead][curr_position[1]] or [])):
                #     continue

                possible_moves.append([row_ahead, curr_position[1]])
            
            # not having the baron buff and an opposing pawn having the baron buff makes the opposing pawn immune
            if not (
                not baron_buff_active and \
                any([piece.get("baron_nashor_buff") and f"{opposing_side}_pawn" == piece.get("type") for piece in squares_ahead[-1]])
            ):
                
                # if capture point advantage is +2 or pawn buff = 1 and enemy pawn is present on square ahead add to list of possible moves
                if pawn_buff >= 1 and \
                not are_squares_ahead_free and \
                are_squares_leading_to_square_ahead_free and \
                any(piece.get("type", "None") == f"{opposing_side}_pawn" and piece.get("pawn_buff", 0) < 1 for piece in squares_ahead[-1]):
                    possible_moves.append([row_ahead, curr_position[1]])
                    possible_captures.append([[row_ahead, curr_position[1]], [row_ahead, curr_position[1]]])

                # if the board herald buff is active and enemy piece is present on square ahead add to list of possible moves
                if board_herald_buff_active and \
                not are_squares_ahead_free and \
                are_squares_leading_to_square_ahead_free:
                    if any([f"{opposing_side}_king" == piece.get("type", "") for piece in squares_ahead[-1]]) and not threatening_move:
                        threatening_move.append([row_ahead, curr_position[1]])
                    elif any([opposing_side in piece.get("type", "") for piece in squares_ahead[-1]]):
                        possible_moves.append([row_ahead, curr_position[1]])
                        possible_captures.append([[row_ahead, curr_position[1]], [row_ahead, curr_position[1]]])

                # if the baron nashor buff is active and enemy piece is present on square ahead add to list of possible moves                
                if baron_buff_active and \
                not are_squares_ahead_free and \
                are_squares_leading_to_square_ahead_free and \
                not any([piece.get("baron_nashor_buff") and f"{opposing_side}_pawn" == piece.get("type") for piece in squares_ahead[-1]]):
                    if any([f"{opposing_side}_king" == piece.get("type", "") for piece in squares_ahead[-1]]) and not threatening_move:
                        threatening_move.append([row_ahead, curr_position[1]])
                    elif any([opposing_side in piece.get("type", "") for piece in squares_ahead[-1]]):
                        possible_moves.append([row_ahead, curr_position[1]])
                        possible_captures.append([[row_ahead, curr_position[1]], [row_ahead, curr_position[1]]])

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

                if not square or \
                    (dragon_buff < 3 and any([s for s in squares_ahead[:-1]])) or \
                    (dragon_buff == 3 and any([s and not all(f"{side}_pawn" == p.get("type", "") for p in s) for s in squares_ahead[:-1]])):
                    # TODO: UNCOMMENT for 4+ stacks of dragon buff
                    #any(not all(opposing_side not in p.get("type", "") for p in s) for s in squares_ahead[:-1]):
                    continue
                
                # not having the baron buff and an opposing pawn having the baron buff makes the opposing pawn immune
                if not (
                    not baron_buff_active and \
                    any([piece.get("baron_nashor_buff") and f"{opposing_side}_pawn" == piece.get("type") for piece in square])
                ):
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

        if not (
            not baron_buff_active and \
            any([piece.get("baron_nashor_buff") and f"{opposing_side}_pawn" == piece.get("type") for piece in lateral_square])
        ):
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

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move})


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
        raise Exception(f"No knight found at position {curr_position}")
    
    possible_moves = []
    possible_captures = []
    threatening_move = []

    dragon_buff = piece_in_play.get("dragon_buff", 0)

    # relative_positions represent all possible moves knight can take
    relative_positions = [[1, -2], [1, 2], [2, -1], [2, 1], [-1, -2],  [-1, 2], [-2, -1], [-2, 1]]
    
    for relative_position in relative_positions:
        potential_position = [curr_position[0] + relative_position[0], curr_position[1] + relative_position[1]]

        if potential_position[0] < 0 or potential_position[0] > 7 or \
        potential_position[1] < 0 or potential_position[1] > 7:
            continue

        path_1_free = True
        path_2_free = True

        # checking to see if path is unblocked to potential move
        path_1_positions = []
        path_2_positions = []

        if abs(relative_position[0]) == 2: # moving 2 squares in x-direction
            path_1_positions.append([curr_position[0] + relative_position[0] // 2, curr_position[1]]) 
            path_1_positions.append([curr_position[0] + relative_position[0], curr_position[1]]) 
            path_2_positions.append([curr_position[0], curr_position[1] + relative_position[1]])
            path_2_positions.append([curr_position[0] + relative_position[0] // 2, curr_position[1] + relative_position[1]])

        else: # moving 2 squares in y-direction
            path_1_positions.append([curr_position[0], curr_position[1] + relative_position[1] // 2])
            path_1_positions.append([curr_position[0], curr_position[1] + relative_position[1]]) 
            path_2_positions.append([curr_position[0] + relative_position[0], curr_position[1]])
            path_2_positions.append([curr_position[0] + relative_position[0], curr_position[1] + relative_position[1] // 2])

        # check if path positions are free
        for i, path_positions in enumerate([path_1_positions, path_2_positions]):
            for path_position in path_positions:
                square = curr_game_state["board_state"][path_position[0]][path_position[1]]

                if (square and not (dragon_buff == 3 and all(piece.get('type') == f"{side}_pawn" for piece in square))) \
                    or curr_game_state["sword_in_the_stone_position"] == path_position:
                    if not i:
                        path_1_free = False
                    else:
                        path_2_free = False
                    break

        potential_position_free = path_1_free or path_2_free
        # if path is unblocked knight is free to move to position 
        if potential_position_free:
            potential_square = curr_game_state["board_state"][potential_position[0]][potential_position[1]]
            if not potential_square:
                possible_moves.append(potential_position)
            
            if potential_square:
                for piece in potential_square:
                    if (opposing_side in piece.get("type", "")):
                        if 'king' in piece.get('type', 'None'):
                            threatening_move.append(potential_position)
                        else:
                            possible_moves.append(potential_position)
                            possible_captures.append([potential_position, potential_position])
                            break
                    if len(potential_square) == 1 and "neutral" in piece.get("type", ""):
                        possible_moves.append(potential_position)
                        if piece.get("health", 0) == 1:
                            possible_captures.append([potential_position, potential_position])

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move})
                    
def get_moves_for_bishop(curr_game_state, prev_game_state, curr_position):
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "bishop" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No bishop found at position {curr_position}")
    
    possible_moves = []
    possible_captures = []
    threatening_move = []

    dragon_buff = piece_in_play.get("dragon_buff", 0)

    directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
    for direction in directions:
        possible_position = [curr_position[0] + direction[0], curr_position[1] + direction[1]]
        while possible_position[0] >= 0 and possible_position[0] <= 7 and possible_position[1] >= 0 and possible_position[1] <= 7:
            if not curr_game_state["board_state"][possible_position[0]][possible_position[1]] and possible_position != curr_game_state["sword_in_the_stone_position"]:
                possible_moves.append(possible_position.copy())
            # if the piece has 3 dragon buff stacks and a same side pawn is on the same square ignore unit collision
            elif not (dragon_buff == 3 and any(piece.get("type") == f"{side}_pawn" for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]] or [])):
                # check for a piece from the same side or sword in stone buff, break out of the current loop if there's one present
                if possible_position == curr_game_state["sword_in_the_stone_position"] or any(side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    break
                # check for a piece from the opposing side, add piece's position to the possible_moves and possible_captures
                # (UNLESS IT'S A KING) and break out of the current loop 
                if any(opposing_side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    if all(f"{opposing_side}_king" != piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                        possible_moves.append(possible_position.copy())
                        possible_captures.append([possible_position.copy(), possible_position.copy()])
                    else:
                        threatening_move.append(possible_position)
                    break
                # check for a neutral monster, add monster's position to possible_moves and only add monster's position 
                # to possible_captures if it has a health of 1. Then break
                if any("neutral" in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    possible_moves.append(possible_position.copy())
                    for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]:
                        if "neutral" in piece["type"] and piece.get("health", 0) == 1:
                            possible_captures.append([possible_position.copy(), possible_position.copy()])
                    break
            possible_position[0] += direction[0]
            possible_position[1] += direction[1]

    if piece_in_play.get("energize_stacks", 0) == 100:
        adjacent_diagonal_squares = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
        # iterate through possible moves
        for possible_move in possible_moves:
            # iterate through every adjacent square
            for adjacent_square in adjacent_diagonal_squares:
                potential_capture_square = [possible_move[0] + adjacent_square[0], possible_move[1] + adjacent_square[1]]
                # continue if square is out of bounds 
                if potential_capture_square[0] < 0 or potential_capture_square[0] > 7 or potential_capture_square[1] < 0 or potential_capture_square[1] > 7:
                    continue
                square = curr_game_state["board_state"][potential_capture_square[0]][potential_capture_square[1]]
                if square and \
                (
                    any(opposing_side in piece.get("type", "") for piece in square) or \
                    any("neutral" in piece.get("type", "") and piece.get("health", 0) == 1 for piece in square) 
                ):
                    if any("king" in piece.get("type", "") for piece in square):
                        threatening_move.append(possible_move)
                    else:
                        possible_captures.append([possible_move, potential_capture_square])

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move})


def get_moves_for_rook(curr_game_state, prev_game_state, curr_position):
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "rook" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No rook found at position {curr_position}")
    
    possible_moves = []
    possible_captures = []
    threatening_move = []
    castle_moves = []
    
    range_limit = 3
    current_turn_count = curr_game_state["turn_count"]

    if current_turn_count >= 15:
        range_limit += (current_turn_count - 10) // 5
    
    directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    for direction in directions:
        possible_position = [curr_position[0] + direction[0], curr_position[1] + direction[1]]
        range_count = 1
        while possible_position[0] >= 0 and possible_position[0] <= 7 and possible_position[1] >= 0 and possible_position[1] <= 7 and range_count <= range_limit:
            if not curr_game_state["board_state"][possible_position[0]][possible_position[1]] and possible_position != curr_game_state["sword_in_the_stone_position"]:
                possible_moves.append(possible_position.copy())
            else:
                # check for a piece from the same side or sword in stone buff, break out of the current loop if there's one present
                if possible_position == curr_game_state["sword_in_the_stone_position"] or any(side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    break
                # check for a piece from the opposing side, add piece's position to the possible_moves and possible_captures
                # (UNLESS IT'S A KING) and break out of the current loop 
                if any(opposing_side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    if all(f"{opposing_side}_king" != piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                        possible_moves.append(possible_position.copy())
                        possible_captures.append([possible_position.copy(), possible_position.copy()])
                    else:
                        threatening_move.append(possible_position.copy())
                    break
                # check for a neutral monster, add monster's position to possible_moves and only add monster's position 
                # to possible_captures if it has a health of 1. Then break
                if any("neutral" in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    possible_moves.append(possible_position.copy())
                    for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]:
                        if "neutral" in piece["type"] and piece.get("health", 0) == 1:
                            possible_captures.append([possible_position.copy(), possible_position.copy()])
                    break
            range_count += 1
            possible_position[0] += direction[0]
            possible_position[1] += direction[1]
    
    # Define constants for each side
    start_row = 7 if side == "white" else 0
    rook_cols = {"left": 0, "right": 7}
    rook_targets = {"left": 3, "right": 5}

    # Check if king is at starting position and hasn't moved
    king_present = any(
        "king" in piece.get("type", "") 
        for piece in curr_game_state["board_state"][start_row][4] or []
    )
    if king_present and not curr_game_state["castle_log"][side]["has_king_moved"]:
        # Determine valid rook moves
        if curr_position == [start_row, rook_cols["left"]] and not curr_game_state["castle_log"][side]["has_left_rook_moved"]:
            castle_moves.append([start_row, rook_targets["left"]])
        elif curr_position == [start_row, rook_cols["right"]] and not curr_game_state["castle_log"][side]["has_right_rook_moved"]:
            castle_moves.append([start_row, rook_targets["right"]])
    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move, "castle_moves": castle_moves})


def get_moves_for_queen(curr_game_state, prev_game_state, curr_position):
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "queen" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No queen found at position {curr_position}")
    
    possible_moves = []
    possible_captures = []
    threatening_move = []
    
    directions = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, 1], [1, -1], [-1, -1]]
    for direction in directions:
        possible_position = [curr_position[0] + direction[0], curr_position[1] + direction[1]]
        while possible_position[0] >= 0 and possible_position[0] <= 7 and possible_position[1] >= 0 and possible_position[1] <= 7:
            if not curr_game_state["board_state"][possible_position[0]][possible_position[1]] and possible_position != curr_game_state["sword_in_the_stone_position"]:
                possible_moves.append(possible_position.copy())
            else:
                # check for a piece from the same side or sword in stone buff, break out of the current loop if there's one present
                if possible_position == curr_game_state["sword_in_the_stone_position"] or any(side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    break
                # check for a piece from the opposing side, add piece's position to the possible_moves and possible_captures
                # (UNLESS IT'S A KING) and break out of the current loop 
                if any(opposing_side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    if all(f"{opposing_side}_king" != piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                        possible_moves.append(possible_position.copy())
                        possible_captures.append([possible_position.copy(), possible_position.copy()])
                    else:
                        threatening_move.append(possible_position.copy())
                    break
                # check for a neutral monster, add monster's position to possible_moves and only add monster's position 
                # to possible_captures if it has a health of 1. Then break
                if any("neutral" in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                    possible_moves.append(possible_position.copy())
                    for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]:
                        if "neutral" in piece["type"] and piece.get("health", 0) == 1:
                            possible_captures.append([possible_position.copy(), possible_position.copy()])
                    break
            possible_position[0] += direction[0]
            possible_position[1] += direction[1]
            
    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move})


# must be called with get_unsafe_posiitons() where unsafe positions are filtered out
# (unable to do that within this function without circular importing in can_king_move())
def get_moves_for_king(curr_game_state, prev_game_state, curr_position):
    evaluate_current_position(curr_position, curr_game_state)
    piece_in_play = None

    for piece in curr_game_state["board_state"][curr_position[0]][curr_position[1]]:
        if "king" in piece["type"]:
            piece_in_play = piece
            side = piece["type"].split("_")[0]
            opposing_side = "white" if side == "black" else "black"
            break

    if not piece_in_play:
        raise Exception(f"No king found at position {curr_position}")
    
    possible_moves = []
    possible_captures = []
    castle_moves = []
    
    directions = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, 1], [1, -1], [-1, -1]]
    for direction in directions:
        possible_position = [curr_position[0] + direction[0], curr_position[1] + direction[1]]
        if not (possible_position[0] >= 0 and possible_position[0] <= 7 and possible_position[1] >= 0 and possible_position[1] <= 7):
            continue

        if not curr_game_state["board_state"][possible_position[0]][possible_position[1]]:
            possible_moves.append(possible_position.copy())
        # check for a piece from the opposing side, add piece's position to the possible_moves and possible_captures
        # (UNLESS IT'S A KING)
        elif any(opposing_side in piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
            if all(f"{opposing_side}_king" != piece["type"] for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
                possible_moves.append(possible_position.copy())
                possible_captures.append([possible_position.copy(), possible_position.copy()])
        # the king shouldn't be allowed to be on the same square as a neutral monster and can only move to a neutral monster's square to slay it
        # check for a neutral monster, only add monster's position to possible_moves and possible_captures if it has a health of 1.
        elif any(("neutral" in piece["type"] and piece.get("health", 0) == 1) for piece in curr_game_state["board_state"][possible_position[0]][possible_position[1]]):
            possible_moves.append(possible_position.copy())
            possible_captures.append([possible_position.copy(), possible_position.copy()])
    
    start_row = 7 if side == "white" else 0
    king_start = [start_row, 4]
    
    # Only allow castling if king is in its starting position and hasn't moved
    if curr_position == king_start and not curr_game_state["castle_log"][side]["has_king_moved"]:
        # Helper function to check if a rook is present on a specific square
        def rook_present(row, col):
            return any(
                "rook" in piece.get("type", "")
                for piece in curr_game_state["board_state"][row][col] or []
            )

        # Check for left (queenside) rook
        if (rook_present(start_row, 0) and 
            not curr_game_state["castle_log"][side]["has_left_rook_moved"]):
            castle_moves.append([start_row, 2])  # King moves to column 2

        # Check for right (kingside) rook
        if (rook_present(start_row, 7) and 
            not curr_game_state["castle_log"][side]["has_right_rook_moved"]):
            castle_moves.append([start_row, 6])  # King moves to column 6
    
    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": [], "castle_moves": castle_moves}, is_king=True)