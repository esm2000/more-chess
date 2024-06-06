import copy
import src.moves as moves
from mocks.empty_game import empty_game
from mocks.starting_game import starting_game

def test_queen_movement():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wq|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bq|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_queen"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [1, 3], [0, 3],
            [2, 4], [1, 5], [0, 6],
            [3, 4], [3, 5], [3, 6], [3, 7],
            [4, 4], [5, 5], [6, 6], [7, 7],
            [4, 3], [5, 3], [6, 3], [7, 3],
            [4, 2], [5, 1], [6, 0],
            [3, 2], [3, 1], [3, 0],
            [2, 2], [1, 1], [0, 0]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_queen_capture():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|bp|##|
    ## 1 |##|__|##|bp|##|__|##|__|
    ## 2 |__|##|bp|##|__|##|__|##|
    ## 3 |##|bp|##|wq|bp|__|##|__|
    ## 4 |__|##|bp|##|__|##|__|##|
    ## 5 |##|__|##|__|##|bp|##|__|
    ## 6 |__|##|__|bp|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|wp|##|
    ## 1 |##|__|##|wp|##|__|##|__|
    ## 2 |__|##|wp|##|__|##|__|##|
    ## 3 |##|wp|##|bq|wp|__|##|__|
    ## 4 |__|##|wp|##|__|##|__|##|
    ## 5 |##|__|##|__|##|wp|##|__|
    ## 6 |__|##|__|wp|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_queen"}]
        curr_game_state["board_state"][3][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][2][2] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][0][6] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][3][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][5][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][6][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][4][2] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [1, 3],
            [2, 4], [1, 5], [0, 6],
            [3, 4],
            [4, 4], [5, 5],
            [4, 3], [5, 3], [6, 3],
            [4, 2],
            [3, 2], [3, 1],
            [2, 2]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert sorted([
            [[1, 3], [1, 3]],
            [[0, 6], [0, 6]],
            [[3, 4], [3, 4]],
            [[5, 5], [5, 5]],
            [[6, 3], [6, 3]],
            [[4, 2], [4, 2]],
            [[3, 1], [3, 1]],
            [[2, 2], [2, 2]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])

def test_queen_blocked():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|bp|##|__|##|__|
    ## 2 |__|##|__|wp|__|##|__|##|
    ## 3 |##|__|##|wq|##|__|##|__|
    ## 4 |__|##|__|##|bp|##|__|##|
    ## 5 |##|__|##|__|##|bp|##|__|
    ## 6 |__|##|__|bp|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|wp|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|##|bq|##|__|##|__|
    ## 4 |__|##|__|##|wp|##|__|##|
    ## 5 |##|__|##|__|##|wp|##|__|
    ## 6 |__|##|__|wp|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_queen"}]
        curr_game_state["board_state"][2][3] = [{"type": f"{'white' if not i else 'black'}_pawn"}]
        curr_game_state["board_state"][1][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][4][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][5][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][6][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]


        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 4], [1, 5], [0, 6],
            [3, 4], [3, 5], [3, 6], [3, 7],
            [4, 4],
            [4, 3], [5, 3], [6, 3],
            [4, 2], [5, 1], [6, 0],
            [3, 2], [3, 1], [3, 0],
            [2, 2], [1, 1], [0, 0]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert sorted([
            [[4, 4], [4, 4]],
            [[6, 3], [6, 3]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])
    pass

def test_queen_cant_capture_king():
    pass

def test_queen_interactions_with_neutral_monster():
    pass

def test_queen_starting_position():
    pass

def test_queen_capturing_adjacent_bishop():
    pass