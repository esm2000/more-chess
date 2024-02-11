import copy
import src.moves as moves
from mocks.empty_game import empty_game
from mocks.starting_game import starting_game

def test_rook_movement():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wr|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|br|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [1, 3], [0, 3],
            [3, 4], [3, 5], [3, 6],
            [3, 2], [3, 1], [3, 0],
            [4, 3], [5, 3], [6, 3]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_rook_range():
    ##    0  1  2  3  4  5  6  7
    ## 0 |wr|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |br|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    range_dict = {
        3: [
            [0, 1], [0, 2], [0, 3],
            [1, 0], [2, 0], [3, 0]
        ],
        4: [
            [0, 1], [0, 2], [0, 3], [0, 4],
            [1, 0], [2, 0], [3, 0], [4, 0]
        ],
        5: [
            [0, 1], [0, 2], [0, 3], [0, 4], [0, 5],
            [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]
        ],
        6: [
            [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6],
            [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0]
        ]
    }

    turn_to_range = {
        0: 3,
        5: 3,
        10: 3,
        15: 4, 
        20: 5,
        25: 6
    }

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][0][0] = [{"type": f"{'white' if not i else 'black'}_rook"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [0, 0]

        
        for turn_count in [0, 5, 10, 15, 20, 25]:
            curr_game_state["turn_count"] = turn_count
            prev_game_state["turn_count"] = turn_count - 1 if turn_count else turn_count
            possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)

            assert sorted(range_dict[turn_to_range[turn_count]]) == sorted(possible_moves_and_captures["possible_moves"])
            assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_rook_capture():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|bp|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |bp|wr|##|__|bp|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|bp|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|wp|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |wp|br|##|__|wp|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|wp|##|__|##|__|##|__|

    moves_dict = {
        3: [
            [3, 0], 
            [2, 1], [1, 1],
            [3, 2], [3, 3], [3, 4],
            [4, 1], [5, 1], [6, 1]
        ],
        4: [
            [3, 0], 
            [2, 1], [1, 1],
            [3, 2], [3, 3], [3, 4],
            [4, 1], [5, 1], [6, 1], [7, 1]
        ]
    }

    captures_dict = {
        3: [
            [[3, 0], [3, 0]],
            [[1, 1], [1, 1]],
            [[3, 4], [3, 4]]
        ],
        4: [
            [[3, 0], [3, 0]],
            [[1, 1], [1, 1]],
            [[3, 4], [3, 4]],
            [[7, 1], [7, 1]]
        ]
    }

    turn_to_range = {
        0: 3,
        5: 3,
        10: 3,
        15: 4
    }

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][1] = [{"type": f"{'white' if not i else 'black'}_rook"}]

        curr_game_state["board_state"][3][0] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][3][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][7][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 1]
        
        for turn_count in [0, 5, 10, 15]:
            curr_game_state["turn_count"] = turn_count
            prev_game_state["turn_count"] = turn_count - 1 if turn_count else turn_count
            possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)

            assert sorted(moves_dict[turn_to_range[turn_count]]) == sorted(possible_moves_and_captures["possible_moves"])
            assert sorted(captures_dict[turn_to_range[turn_count]]) == sorted(possible_moves_and_captures["possible_captures"])


def test_rook_blocked():
    pass


def test_rook_cant_capture_king():
    pass


def test_rook_interactions_with_neutral_monster():
    pass


def test_rook_starting_position():
    pass


def test_rook_capturing_adjacent_bishop():
    pass