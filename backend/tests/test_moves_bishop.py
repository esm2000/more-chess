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


def test_bishop_capture():
    pass


def test_bishop_blocked():
    pass


def test_bishop_cant_capture_king():
    pass


def test_bishop_interactions_with_neutral_monster():
    pass


def test_bishop_starting_position():
    pass


def test_bishop_capturing_adjacent_bishop():
    pass