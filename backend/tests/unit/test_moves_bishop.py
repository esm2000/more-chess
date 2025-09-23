import copy

import src.moves as moves
from mocks.empty_game import empty_game
from mocks.starting_game import starting_game

def test_bishop_movement():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    # white square
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]

        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [0, 0], [1, 1], [2, 2], [4, 4], [5, 5], [6, 6], [7, 7], 
            [6, 0], [5, 1], [4, 2], [2, 4], [1, 5], [0, 6]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0
    # black square 
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][4] = [{"type": f"{side}_bishop"}]

        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 4]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [7, 0], [6, 1], [5, 2], [4, 3], [2, 5], [1, 6], [0, 7],
            [0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_bishop_capture():
    # white square                      # black square
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|bp|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|bp|__| 
    ## 2 |__|##|__|##|bp|##|__|##|      ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|      ## 3 |##|__|##|__|wb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |bp|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|bp|
    ## 7 |##|__|##|__|##|__|##|bp|      ## 7 |bp|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|wp|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|wp|__| 
    ## 2 |__|##|__|##|wp|##|__|##|      ## 2 |__|##|__|wp|__|##|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|      ## 3 |##|__|##|__|bb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |wp|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|wp|
    ## 7 |##|__|##|__|##|__|##|wp|      ## 7 |wp|__|##|__|##|__|##|__|
    
    # white square
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
        curr_game_state["board_state"][2][4] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][1][1] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][6][0] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][7][7] = [{"type": f"{opposite_side}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 4], [2, 2], [1, 1], [4, 2], [5, 1], [6, 0], [4, 4], [5, 5], [6, 6], [7, 7]
        ]) == sorted(possible_moves_and_captures["possible_moves"])

        assert sorted([
            [[2, 4], [2, 4]],
            [[1, 1], [1, 1]], 
            [[6, 0], [6, 0]],
            [[7, 7], [7, 7]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])

    # black square
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][4] = [{"type": f"{side}_bishop"}]
        curr_game_state["board_state"][2][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][1][6] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][6][7] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][7][0] = [{"type": f"{opposite_side}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 4]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [2, 5], [1, 6], [4, 5], [5, 6], [6, 7], [4, 3], [5, 2], [6, 1], [7, 0]
        ]) == sorted(possible_moves_and_captures["possible_moves"])

        assert sorted([
            [[2, 3], [2, 3]],
            [[1, 6], [1, 6]], 
            [[6, 7], [6, 7]],
            [[7, 0], [7, 0]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])


def test_bishop_blocked():
    # white square                      # black square
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|bp|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|bp|__| 
    ## 2 |__|##|wp|##|__|##|__|##|      ## 2 |__|##|__|##|__|wp|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|      ## 3 |##|__|##|__|wb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|wp|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|wp|__|
    ## 6 |bp|##|__|##|__|##|bp|##|      ## 6 |__|bp|__|##|__|##|__|bp|
    ## 7 |##|__|##|__|##|__|##|bp|      ## 7 |bp|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|wp|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|wp|__| 
    ## 2 |__|##|bp|##|__|##|__|##|      ## 2 |__|##|__|##|__|bp|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|      ## 3 |##|__|##|__|bb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|bp|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|bp|__|
    ## 6 |wp|##|__|##|__|##|wp|##|      ## 6 |__|wp|__|##|__|##|__|wp|
    ## 7 |##|__|##|__|##|__|##|wp|      ## 7 |wp|__|##|__|##|__|##|__|

    # white square
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
        curr_game_state["board_state"][1][1] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][6][0] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][7][7] = [{"type": f"{opposite_side}_pawn"}]

        curr_game_state["board_state"][2][2] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][5][1] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][6][6] = [{"type": f"{opposite_side}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 4], [1, 5], [0, 6], [4, 2], [4, 4], [5, 5], [6, 6]
        ]) == sorted(possible_moves_and_captures["possible_moves"])

        assert [[7, 7], [7, 7]] not in possible_moves_and_captures["possible_captures"]
        assert sorted([[[6, 6], [6, 6]]]) == sorted(possible_moves_and_captures["possible_captures"])
    
    # black square
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][4] = [{"type": f"{side}_bishop"}]
        curr_game_state["board_state"][1][6] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][6][7] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][7][0] = [{"type": f"{opposite_side}_pawn"}]

        curr_game_state["board_state"][2][5] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][5][6] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][6][1] = [{"type": f"{opposite_side}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 4]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [1, 2], [0, 1], [4, 5], [4, 3], [5, 2], [6, 1]
        ]) == sorted(possible_moves_and_captures["possible_moves"])

        assert [[7, 0], [7, 0]] not in possible_moves_and_captures["possible_captures"]
        assert sorted([[[6, 1], [6, 1]]]) == sorted(possible_moves_and_captures["possible_captures"])


def test_bishop_cant_capture_king():
    # white square                      # black square
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|##|bK|##|__|##|      ## 2 |__|##|__|bK|__|##|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|      ## 3 |##|__|##|__|wb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|##|wK|##|__|##|      ## 2 |__|##|__|wK|__|##|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|      ## 3 |##|__|##|__|bb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # white square
    king_positions = [[2, 4], [1, 1], [6, 0], [7, 7]]
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
            curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{opposite_side}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_captures"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0

    # black square
    king_positions = [[2, 3], [1, 6], [6, 7], [7, 0]]
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][4] = [{"type": f"{side}_bishop"}]
            curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{opposite_side}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 4]

            possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_moves"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_bishop_interactions_with_neutral_monster():
    # white square                      # black square
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|##|nd|##|__|##|      ## 2 |__|##|__|nd|__|##|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|      ## 3 |##|__|##|__|wb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|##|nd|##|__|##|      ## 2 |__|##|__|nd|__|##|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|      ## 3 |##|__|##|__|bb|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # white square
    neutral_monster_positions = [[2, 4], [1, 1], [6, 0], [7, 7]]
    for side in ["white", "black"]:
        for neutral_monster_position in neutral_monster_positions:
            for health in [5, 1]:
                for monster in ["dragon", "baron_nashor", "board_herald"]:
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
                    curr_game_state["board_state"][neutral_monster_position[0]][neutral_monster_position[1]] = [{
                        "type": f"neutral_{monster}",
                        "health": health
                    }]

                    prev_game_state = copy.deepcopy(curr_game_state)

                    curr_position = [3, 3]

                    possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
                    assert neutral_monster_position in possible_moves_and_captures["possible_moves"]

                    if health == 1:
                        assert [[neutral_monster_position, neutral_monster_position]] == possible_moves_and_captures["possible_captures"]
                    else:
                        assert [neutral_monster_position, neutral_monster_position] not in possible_moves_and_captures["possible_captures"]
                        assert len(possible_moves_and_captures["possible_captures"]) == 0

    # black square
    neutral_monster_positions = [[2, 3], [1, 6], [6, 7], [7, 0]]
    for side in ["white", "black"]:
        for neutral_monster_position in neutral_monster_positions:
            for health in [5, 1]:
                for monster in ["dragon", "baron_nashor", "board_herald"]:
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][4] = [{"type": f"{side}_bishop"}]
                    curr_game_state["board_state"][neutral_monster_position[0]][neutral_monster_position[1]] = [{
                        "type": f"neutral_{monster}",
                        "health": health
                    }]

                    prev_game_state = copy.deepcopy(curr_game_state)

                    curr_position = [3, 4]

                    possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
                    assert neutral_monster_position in possible_moves_and_captures["possible_moves"]

                    if health == 1:
                        assert [[neutral_monster_position, neutral_monster_position]] == possible_moves_and_captures["possible_captures"]
                    else:
                        assert [neutral_monster_position, neutral_monster_position] not in possible_moves_and_captures["possible_captures"]
                        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_bishop_starting_position():
    curr_game_state = copy.deepcopy(starting_game)
    starting_positions = [[0, 2], [0, 5], [7, 2], [7, 5]]

    for starting_position in starting_positions:
        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, None, [starting_position[0], starting_position[1]])
        if starting_position != [0, 2]:
            assert len(possible_moves_and_captures["possible_moves"]) == 0
        else:
            assert sorted([[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_bishop_capturing_adjacent_bishop():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|bp|##|__|      ## 1 |##|__|##|__|##|wp|##|__|
    ## 2 |__|##|__|##|__|bb|__|##|      ## 2 |__|##|__|##|__|wb|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|      ## 3 |##|__|##|bb|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
        curr_game_state["board_state"][1][5] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][2][5] = [{"type": f"{opposite_side}_bishop"}]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, None, [3, 3])

        # moving to [1, 5] would allow the capturing of [1, 5] and [2, 5], 
        # moving to [2, 4] would allow the capturing of [2, 5]
        assert sorted(possible_moves_and_captures["possible_captures"]) == sorted([
            [
                [1, 5], 
                [1, 5]
            ], 
            [
                [2, 4], 
                [2, 5]
            ], 
            [
                [1, 5], 
                [2, 5]
            ]
        ])


def test_bishop_not_being_allowed_to_move_to_sword_in_stone_square():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|ss|##|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|ss|##|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    position_map = [
        [[2, 4]],
        [[2, 2]],
        [[4, 2], [5, 1]],
        [[4, 4], [5, 5]]
    ]

    for side in ["white", "black"]:
        for positions in position_map:
            for j in range(len(positions)):
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["turn_count"] = 0
                curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
                curr_game_state["sword_in_the_stone_position"] = positions[j]

                prev_game_state = copy.deepcopy(curr_game_state)
                curr_position = [3, 3]

                possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
                for k in range(j, len(positions)):
                    assert positions[k] not in possible_moves_and_captures["possible_moves"]
                for k in range(j):
                    assert positions[k] in possible_moves_and_captures["possible_moves"]

def test_bishop_full_energize_stack_capture():
    # test that the bishop is able threaten neutral and enemy pieces adjacent to every square it can move to
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|bp|__|
    ## 2 |__|##|__|wb|__|##|__|##|
    ## 3 |bp|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|nd|
    ## 5 |bp|__|bp|__|##|__|##|__|
    ## 6 |__|##|__|##|__|bp|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|wp|__|
    ## 2 |__|##|__|bb|__|##|__|##|
    ## 3 |wp|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|nd|
    ## 5 |wp|__|wp|__|##|__|##|__|
    ## 6 |__|##|__|##|__|wp|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for dragon_health in [1, 5]:
        for energize_stacks in [0, 100]:
            for side in ["white", "black"]:
                opposite_side = "white" if side == "black" else "black"
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][2][3] = [{
                    "type": f"{side}_bishop",
                    "energize_stacks": energize_stacks
                }]
                curr_game_state["board_state"][3][0] = [{"type": f"{opposite_side}_pawn"}]
                curr_game_state["board_state"][5][0] = [{"type": f"{opposite_side}_pawn"}]
                curr_game_state["board_state"][5][2] = [{"type": f"{opposite_side}_pawn"}]
                curr_game_state["board_state"][6][5] = [{"type": f"{opposite_side}_pawn"}]
                curr_game_state["board_state"][1][6] = [{"type": f"{opposite_side}_pawn"}]
                curr_game_state["board_state"][4][7] = [{"type": f"neutral_dragon", "health": dragon_health}]

                possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, None, [2, 3])
                
                # bishop has to move to position_1 to capture piece in position_2
                if energize_stacks:
                    assert [[4, 1], [3, 0]] in possible_moves_and_captures["possible_captures"]
                    assert [[4, 1], [5, 0]] in possible_moves_and_captures["possible_captures"]
                    assert [[4, 1], [5, 2]] in possible_moves_and_captures["possible_captures"]
                    assert [[5, 6], [6, 5]] in possible_moves_and_captures["possible_captures"]
                    assert [[0, 5], [1, 6]] in possible_moves_and_captures["possible_captures"]
                    if dragon_health == 1:
                        assert [[5, 6], [4, 7]] in possible_moves_and_captures["possible_captures"]
                    else:
                        assert [[5, 6], [4, 7]] not in possible_moves_and_captures["possible_captures"]
                else:
                    assert [[4, 1], [3, 0]] not in possible_moves_and_captures["possible_captures"]
                    assert [[4, 1], [5, 0]] not in possible_moves_and_captures["possible_captures"]
                    assert [[4, 1], [5, 2]] not in possible_moves_and_captures["possible_captures"]
                    assert [[5, 6], [6, 5]] not in possible_moves_and_captures["possible_captures"]
                    assert [[0, 5], [1, 6]] not in possible_moves_and_captures["possible_captures"]
                    assert [[5, 6], [4, 7]] not in possible_moves_and_captures["possible_captures"]


def test_bishop_threatening_move():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|bK|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wb|##|__|##|__|      ## 3 |##|__|##|wb|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|wK|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bb|##|__|##|__|      ## 3 |##|__|##|bb|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    king_positions = [[None, None], [1, 5], [1, 1], [6, 0], [6, 6]]
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_bishop"}]
            if king_position[0] is not None:
                curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{opposite_side}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_captures"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0
            if king_position[0] is not None:
                assert [king_position] == possible_moves_and_captures["threatening_move"]
            else:
                assert [king_position] not in possible_moves_and_captures["threatening_move"]
                assert len(possible_moves_and_captures["threatening_move"]) == 0


def test_bishop_with_three_or_more_dragon_buff_stacks_ignores_unit_collision_with_ally_pawns():
    pass

def test_bishop_with_three_dragon_buff_stacks_does_not_ignores_unit_collision_with_ally_non_pawns():
    pass

def test_bishop_with_three_dragon_buff_stacks_does_not_ignores_unit_collision_with_enemy_pawns():
    pass

def test_bishop_with_three_dragon_buff_stacks_does_not_ignores_unit_collision_with_enemy_non_pawns():
    pass