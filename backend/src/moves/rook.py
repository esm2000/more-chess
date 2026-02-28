from src.moves._helpers import (
    evaluate_current_position,
    process_possible_moves_dict,
    _add_marked_for_death_threats,
    _can_ignore_ally_collision,
)


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

    dragon_buff = piece_in_play.get("dragon_buff", 0)

    directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    for direction in directions:
        possible_position = [curr_position[0] + direction[0], curr_position[1] + direction[1]]
        range_count = 1
        while possible_position[0] >= 0 and possible_position[0] <= 7 and possible_position[1] >= 0 and possible_position[1] <= 7 and range_count <= range_limit:
            if not curr_game_state["board_state"][possible_position[0]][possible_position[1]] and possible_position != curr_game_state["sword_in_the_stone_position"]:
                possible_moves.append(possible_position.copy())
            elif not _can_ignore_ally_collision(curr_game_state["board_state"][possible_position[0]][possible_position[1]], side, dragon_buff):
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
    if dragon_buff >= 5:
        _add_marked_for_death_threats(possible_moves, threatening_move, opposing_side, curr_game_state["board_state"])

    return process_possible_moves_dict(curr_game_state, curr_position, side, {"possible_moves": possible_moves, "possible_captures": possible_captures, "threatening_move": threatening_move, "castle_moves": castle_moves})
