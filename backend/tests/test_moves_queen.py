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
    pass

def test_queen_blocked():
    pass

def test_queen_cant_capture_king():
    pass

def test_queen_interactions_with_neutral_monster():
    pass

def test_queen_starting_position():
    pass

def test_queen_capturing_adjacent_bishop():
    pass