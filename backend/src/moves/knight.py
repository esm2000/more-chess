from src.utils.board_analysis import evaluate_current_position
from src.moves._helpers import (
    process_possible_moves_dict,
    _add_marked_for_death_threats,
)


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

                if (square \
                    and not (dragon_buff == 3 and all(piece.get('type') == f"{side}_pawn" for piece in square)) \
                    and not (dragon_buff >= 4 and all(side in piece.get('type') for piece in square))) \
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

    if dragon_buff >= 5:
        _add_marked_for_death_threats(possible_moves, threatening_move, opposing_side, curr_game_state["board_state"])

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move})
