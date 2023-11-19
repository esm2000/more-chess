import copy

import src.moves as moves
from mocks.empty_game import empty_game

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
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_bishop"}]

        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [0, 0], [1, 1], [2, 2], [4, 4], [5, 5], [6, 6], [7, 7], 
            [6, 0], [5, 1], [4, 2], [2, 4], [1, 5], [0, 6]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0
    # black square 
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][4] = [{"type": f"{'white' if not i else 'black'}_bishop"}]

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
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_bishop"}]
        curr_game_state["board_state"][2][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][6][0] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][7][7] = [{"type": f"{'black' if not i else 'white'}_pawn"}]


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
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][4] = [{"type": f"{'white' if not i else 'black'}_bishop"}]
        curr_game_state["board_state"][2][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][6] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][6][7] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][7][0] = [{"type": f"{'black' if not i else 'white'}_pawn"}]


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
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_bishop"}]
        curr_game_state["board_state"][1][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][6][0] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][7][7] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        curr_game_state["board_state"][2][2] = [{"type": f"{'white' if not i else 'black'}_pawn"}]
        curr_game_state["board_state"][5][1] = [{"type": f"{'white' if not i else 'black'}_pawn"}]
        curr_game_state["board_state"][6][6] = [{"type": f"{'black' if not i else 'white'}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 4], [1, 5], [0, 6], [4, 2], [4, 4], [5, 5], [6, 6]
        ]) == sorted(possible_moves_and_captures["possible_moves"])

        assert [[7, 7], [7, 7]] not in possible_moves_and_captures["possible_captures"]
        assert sorted([[[6, 6], [6, 6]]]) == sorted(possible_moves_and_captures["possible_captures"])
    
    # black square
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][4] = [{"type": f"{'white' if not i else 'black'}_bishop"}]
        curr_game_state["board_state"][1][6] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][6][7] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][7][0] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        curr_game_state["board_state"][2][5] = [{"type": f"{'white' if not i else 'black'}_pawn"}]
        curr_game_state["board_state"][5][6] = [{"type": f"{'white' if not i else 'black'}_pawn"}]
        curr_game_state["board_state"][6][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 4]

        possible_moves_and_captures = moves.get_moves_for_bishop(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [1, 2], [0, 1], [4, 5], [4, 3], [5, 2], [6, 1]
        ]) == sorted(possible_moves_and_captures["possible_moves"])

        assert [[7, 0], [7, 0]] not in possible_moves_and_captures["possible_captures"]
        assert sorted([[[6, 1], [6, 1]]]) == sorted(possible_moves_and_captures["possible_captures"])


def test_bishop_cant_capture_king():
    pass


def test_bishop_interactions_with_neutral_monster():
    pass


def test_bishop_starting_position():
    pass


def test_bishop_capturing_adjacent_bishop():
    pass