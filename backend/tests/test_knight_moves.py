import copy
import src.moves as moves
from mocks.empty_game import empty_game


def test_knight_movement():
    pass


def test_knight_capture():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|bp|__|bp|__|##|__|
    ## 2 |__|bp|__|##|__|bp|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|bp|__|##|__|bp|__|##|
    ## 5 |##|__|##|__|bp|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|wp|__|wp|__|##|__|
    ## 2 |__|wp|__|##|__|wp|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|wp|__|##|__|wp|__|##|
    ## 5 |##|__|##|__|wp|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]

        curr_game_state["board_state"][1][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][2][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][4][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][5][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][4][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][2][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][2] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][3][3] = None
        prev_game_state["board_state"][5][2] = [{"type": f"{'white' if not i else 'black'}_pawn"}]

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
        assert sorted([[1, 4], [2, 5], [4, 5], [5, 2], [5, 4], [4, 1], [2, 1], [1, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert sorted([
            [[1, 4], [1, 4]],
            [[2, 5], [2, 5]],
            [[4, 5], [4, 5]],
            [[5, 4], [5, 4]],
            [[4, 1], [4, 1]],
            [[2, 1], [2, 1]],
            [[1, 2], [1, 2]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])


def test_knight_blocked():
    pass


def test_knight_cant_capture_king():
    pass


def test_knight_overflow():
    pass