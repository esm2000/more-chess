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
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]

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

    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
        curr_game_state["board_state"][3][1] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][2][2] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][1][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][0][6] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][3][4] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][5][5] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][6][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][4][2] = [{"type": f"{opposite_side}_pawn"}]

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
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
        curr_game_state["board_state"][2][3] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][1][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][4][4] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][5][5] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][6][3] = [{"type": f"{opposite_side}_pawn"}]


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
        # vertical                          # horizontal                        # diagonal
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bK|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|bK|##|__|##|  
    ## 3 |##|__|##|wq|##|__|##|__|      ## 3 |##|__|##|wq|bK|__|##|__|      ## 3 |##|__|##|wq|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|wK|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|wK|##|__|##|  
    ## 3 |##|__|##|bq|##|__|##|__|      ## 3 |##|__|##|bq|wK|__|##|__|      ## 3 |##|__|##|bq|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    king_positions = [[2, 3], [2, 4], [3, 4], [4, 4], [4, 3], [4, 2], [3, 2], [2, 2]]
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
            curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{opposite_side}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_moves"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0

def test_queen_interactions_with_neutral_monster():
    # vertical                          # horizontal                        # diagonal
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|nd|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wq|##|__|##|__|      ## 3 |##|__|##|wq|nd|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|nd|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bq|##|__|##|__|      ## 3 |##|__|##|bq|nd|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    neutral_monster_positions = [[2, 3], [2, 4], [3, 4], [4, 4], [4, 3], [4, 2], [3, 2], [2, 2]]
    for side in ["white", "black"]:
        for neutral_monster_position in neutral_monster_positions:
            for health in [5, 1]:
                for monster in ["dragon", "baron_nashor", "board_herald"]:
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
                    curr_game_state["board_state"][neutral_monster_position[0]][neutral_monster_position[1]] = [{
                        "type": f"neutral_{monster}",
                        "health": health
                    }]

                    prev_game_state = copy.deepcopy(curr_game_state)

                    curr_position = [3, 3]
                    
                    possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)
                    assert neutral_monster_position in possible_moves_and_captures["possible_moves"]

                    if health == 1:
                        assert [[neutral_monster_position, neutral_monster_position]] == possible_moves_and_captures["possible_captures"]
                    else:
                        assert [neutral_monster_position, neutral_monster_position] not in possible_moves_and_captures["possible_captures"]
                        assert len(possible_moves_and_captures["possible_captures"]) == 0     

def test_queen_starting_position():
    curr_game_state = copy.deepcopy(starting_game)
    starting_positions = [[0, 3], [7, 3]]

    for starting_position in starting_positions:
        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, None, [starting_position[0], starting_position[1]])
        if starting_position == [0, 3]:
            assert possible_moves_and_captures["possible_moves"] == [[1, 3]]
        elif starting_position == [7, 3]:
            assert len(possible_moves_and_captures["possible_moves"]) == 0
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_queen_capturing_adjacent_bishop():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|bp|bb|__|##|__|      ## 1 |##|__|##|wp|wb|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wq|##|__|##|__|      ## 3 |##|__|##|bq|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
        curr_game_state["board_state"][1][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][1][4] = [{"type": f"{opposite_side}_bishop"}]

        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, None, [3, 3])

        # moving to [1, 3] would allow the capturing of [1, 3] and [1, 4], 
        # moving to [1, 5] would allow the capturing of [1, 4]
        # moving to [2, 3] would allow the capturing of [1, 4]
        # moving to [2, 4] would allow the capturing of [1, 4]

        assert sorted(possible_moves_and_captures["possible_captures"]) == sorted([
            [[1, 3], [1, 3]], 
            [[1, 3], [1, 4]], 
            [[1, 5], [1, 4]], 
            [[2, 3], [1, 4]],
            [[2, 4], [1, 4]]
        ])


def test_queen_not_being_allowed_to_move_to_sword_in_stone_square():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|__|##|__|##|
    ## 3 |##|__|##|wr|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|__|##|__|##|
    ## 3 |##|__|##|br|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    position_map = [
        # diagonal
        [[2, 4]],
        [[2, 2]],
        [[4, 2], [5, 1]],
        [[4, 4], [5, 5]],

        # vertical and hortizontal
        [[2, 3]],
        [[3, 4], [3, 5], [3, 6], [3, 7]],
        [[4, 3], [5, 3]],
        [[3, 2], [3, 1], [3, 0]]
    ]

    for side in ["white", "black"]:
        for positions in position_map:
            for j in range(len(positions)):
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["turn_count"] = 0
                curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
                curr_game_state["sword_in_the_stone_position"] = positions[j]

                prev_game_state = copy.deepcopy(curr_game_state)
                curr_position = [3, 3]

                possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)
                for k in range(j, len(positions)):
                    assert positions[k] not in possible_moves_and_captures["possible_moves"]
                for k in range(j):
                    assert positions[k] in possible_moves_and_captures["possible_moves"]


def test_queen_file_control():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|wq|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|bq|##|__|##|__|

    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][7][3] = [{"type": f"{side}_queen"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [7, 3]

        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            # not allowed to cross the center to reach [[1, 3], [0, 3]]
            [6, 3], [5, 3], [4, 3], [3, 3], [2, 3],
            [7, 2], [7, 1], [7, 0],
            [7, 4], [7, 5], [7, 6], [7, 7],
            [6, 2], [5, 1], [4, 0],
            [6, 4], [5, 5], [4, 6], [3, 7]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_queen_threatening_move():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|bK|##|__|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wq|##|__|##|__|      ## 3 |##|__|##|wq|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|wK|##|__|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bq|##|__|##|__|      ## 3 |##|__|##|bq|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    king_positions = [[None, None], [1, 3], [1, 5], [3, 5], [5, 5], [5, 3], [5, 1], [3, 1], [1, 1]]
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen"}]
            if king_position[0] is not None:
                curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{opposite_side}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_captures"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0
            if king_position[0] is not None:
                assert [king_position] == possible_moves_and_captures["threatening_move"]
            else:
                assert [king_position] not in possible_moves_and_captures["threatening_move"]
                assert len(possible_moves_and_captures["threatening_move"]) == 0

def test_queen_file_control_limitations():
    pass

def test_queen_with_three_or_more_dragon_buff_stacks_ignores_unit_collision_with_ally_pawns():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|wp|wp|wp|##|__|##|      ## 2 |__|##|bp|bp|bp|##|__|##|
    ## 3 |##|__|wp|wq|wp|__|##|__|      ## 3 |##|__|bp|bq|bp|__|##|__|
    ## 4 |__|##|wp|wp|wp|##|__|##|      ## 4 |__|##|bp|bp|bp|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # Ally pawns at all 8 adjacent squares block all queen directions.
    # With 3+ dragon buff stacks, ally pawn collisions should be ignored.
    for side in ["white", "black"]:
        for dragon_buff_stacks in [3, 4, 5]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen", "dragon_buff": dragon_buff_stacks}]
            curr_game_state["board_state"][2][2] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][2][3] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][2][4] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][3][2] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][3][4] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][4][2] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][4][3] = [{"type": f"{side}_pawn"}]
            curr_game_state["board_state"][4][4] = [{"type": f"{side}_pawn"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, [3, 3])
            assert [1, 3] in possible_moves_and_captures["possible_moves"]
            assert [5, 3] in possible_moves_and_captures["possible_moves"]
            assert [3, 1] in possible_moves_and_captures["possible_moves"]
            assert [3, 5] in possible_moves_and_captures["possible_moves"]
            assert [1, 5] in possible_moves_and_captures["possible_moves"]
            assert [5, 5] in possible_moves_and_captures["possible_moves"]
            assert [5, 1] in possible_moves_and_captures["possible_moves"]
            assert [1, 1] in possible_moves_and_captures["possible_moves"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_queen_with_three_dragon_buff_stacks_does_not_ignore_unit_collision_with_ally_non_pawns():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|wr|wr|wr|##|__|##|      ## 2 |__|##|br|br|br|##|__|##|
    ## 3 |##|__|wr|wq|wr|__|##|__|      ## 3 |##|__|br|bq|br|__|##|__|
    ## 4 |__|##|wr|wr|wr|##|__|##|      ## 4 |__|##|br|br|br|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # With exactly 3 dragon buff stacks, ally non-pawn pieces should still block the queen.
    for side in ["white", "black"]:
        for ally_piece_type in ["knight", "bishop", "rook", "queen"]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen", "dragon_buff": 3}]
            curr_game_state["board_state"][2][2] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][2][3] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][2][4] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][3][2] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][3][4] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][4][2] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][4][3] = [{"type": f"{side}_{ally_piece_type}"}]
            curr_game_state["board_state"][4][4] = [{"type": f"{side}_{ally_piece_type}"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, [3, 3])
            assert len(possible_moves_and_captures["possible_moves"]) == 0
            assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_queen_with_three_dragon_buff_stacks_does_not_ignore_unit_collision_with_enemy_pawns():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|bp|bp|bp|##|__|##|      ## 2 |__|##|wp|wp|wp|##|__|##|
    ## 3 |##|__|bp|wq|bp|__|##|__|      ## 3 |##|__|wp|bq|wp|__|##|__|
    ## 4 |__|##|bp|bp|bp|##|__|##|      ## 4 |__|##|wp|wp|wp|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # With 3 dragon buff stacks, enemy pawns should still block the queen.
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen", "dragon_buff": 3}]
        curr_game_state["board_state"][2][2] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][2][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][2][4] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][3][2] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][3][4] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][4][2] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][4][3] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][4][4] = [{"type": f"{opposite_side}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)

        possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, [3, 3])
        # Queen captures enemy pawns but should NOT move beyond them
        assert [1, 3] not in possible_moves_and_captures["possible_moves"]
        assert [5, 3] not in possible_moves_and_captures["possible_moves"]
        assert [1, 1] not in possible_moves_and_captures["possible_moves"]
        assert [5, 5] not in possible_moves_and_captures["possible_moves"]


def test_queen_with_three_dragon_buff_stacks_does_not_ignore_unit_collision_with_enemy_non_pawns():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|br|br|br|##|__|##|      ## 2 |__|##|wr|wr|wr|##|__|##|
    ## 3 |##|__|br|wq|br|__|##|__|      ## 3 |##|__|wr|bq|wr|__|##|__|
    ## 4 |__|##|br|br|br|##|__|##|      ## 4 |__|##|wr|wr|wr|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # With 3 dragon buff stacks, enemy non-pawn pieces should still block the queen.
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for enemy_piece_type in ["knight", "bishop", "rook", "queen"]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen", "dragon_buff": 3}]
            curr_game_state["board_state"][2][2] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][2][3] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][2][4] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][3][2] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][3][4] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][4][2] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][4][3] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
            curr_game_state["board_state"][4][4] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, [3, 3])
            assert [1, 3] not in possible_moves_and_captures["possible_moves"]
            assert [5, 3] not in possible_moves_and_captures["possible_moves"]
            assert [1, 1] not in possible_moves_and_captures["possible_moves"]
            assert [5, 5] not in possible_moves_and_captures["possible_moves"]


def test_queen_with_four_or_more_dragon_buff_stacks_ignores_unit_collision_with_ally_pieces():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|wr|wr|wr|##|__|##|      ## 2 |__|##|br|br|br|##|__|##|
    ## 3 |##|__|wr|wq|wr|__|##|__|      ## 3 |##|__|br|bq|br|__|##|__|
    ## 4 |__|##|wr|wr|wr|##|__|##|      ## 4 |__|##|br|br|br|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # With 4+ dragon buff stacks, ALL ally pieces (including non-pawns) should be ignored.
    for side in ["white", "black"]:
        for dragon_buff_stacks in [4, 5]:
            for ally_piece_type in ["pawn", "knight", "bishop", "rook", "queen"]:
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen", "dragon_buff": dragon_buff_stacks}]
                curr_game_state["board_state"][2][2] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][2][3] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][2][4] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][3][2] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][3][4] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][4][2] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][4][3] = [{"type": f"{side}_{ally_piece_type}"}]
                curr_game_state["board_state"][4][4] = [{"type": f"{side}_{ally_piece_type}"}]

                prev_game_state = copy.deepcopy(curr_game_state)

                possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, [3, 3])
                assert [1, 3] in possible_moves_and_captures["possible_moves"]
                assert [5, 3] in possible_moves_and_captures["possible_moves"]
                assert [1, 5] in possible_moves_and_captures["possible_moves"]
                assert [5, 5] in possible_moves_and_captures["possible_moves"]
                assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_queen_with_four_or_more_dragon_buff_stacks_does_not_ignore_unit_collision_with_enemy_pieces():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|br|br|br|##|__|##|      ## 2 |__|##|wr|wr|wr|##|__|##|
    ## 3 |##|__|br|wq|br|__|##|__|      ## 3 |##|__|wr|bq|wr|__|##|__|
    ## 4 |__|##|br|br|br|##|__|##|      ## 4 |__|##|wr|wr|wr|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    # With 4+ dragon buff stacks, enemy pieces should still block the queen.
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for dragon_buff_stacks in [4, 5]:
            for enemy_piece_type in ["pawn", "knight", "bishop", "rook", "queen"]:
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][3][3] = [{"type": f"{side}_queen", "dragon_buff": dragon_buff_stacks}]
                curr_game_state["board_state"][2][2] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][2][3] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][2][4] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][3][2] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][3][4] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][4][2] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][4][3] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]
                curr_game_state["board_state"][4][4] = [{"type": f"{opposite_side}_{enemy_piece_type}"}]

                prev_game_state = copy.deepcopy(curr_game_state)

                possible_moves_and_captures = moves.get_moves_for_queen(curr_game_state, prev_game_state, [3, 3])
                assert [1, 3] not in possible_moves_and_captures["possible_moves"]
                assert [5, 5] not in possible_moves_and_captures["possible_moves"]
