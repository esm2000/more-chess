import copy
import src.moves as moves
from mocks.empty_game import empty_game
from mocks.starting_game import starting_game


def test_knight_movement():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]

        prev_game_state = copy.deepcopy(curr_game_state)

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
        assert sorted([[1, 4], [2, 5], [4, 5], [5, 2], [5, 4], [4, 1], [2, 1], [1, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_knight_capture():
#     ##    0  1  2  3  4  5  6  7
#     ## 0 |__|##|__|##|__|##|__|##|
#     ## 1 |##|__|bp|__|bp|__|##|__|
#     ## 2 |__|bp|__|##|__|bp|__|##|
#     ## 3 |##|__|##|wk|##|__|##|__|
#     ## 4 |__|bp|__|##|__|bp|__|##|
#     ## 5 |##|__|bp|__|bp|__|##|__|
#     ## 6 |__|##|__|##|__|##|__|##|
#     ## 7 |##|__|##|__|##|__|##|__|

#     ##    0  1  2  3  4  5  6  7
#     ## 0 |__|##|__|##|__|##|__|##|
#     ## 1 |##|__|wp|__|wp|__|##|__|
#     ## 2 |__|wp|__|##|__|wp|__|##|
#     ## 3 |##|__|##|bk|##|__|##|__|
#     ## 4 |__|wp|__|##|__|wp|__|##|
#     ## 5 |##|__|wp|__|wp|__|##|__|
#     ## 6 |__|##|__|##|__|##|__|##|
#     ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]

        curr_game_state["board_state"][1][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][2][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][4][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][5][2] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][5][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][4][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][2][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][2] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][2][1] = None
        prev_game_state["board_state"][1][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
        assert sorted([[1, 4], [2, 5], [4, 5], [5, 2], [5, 4], [4, 1], [2, 1], [1, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert sorted([
            [[1, 4], [1, 4]],
            [[2, 5], [2, 5]],
            [[4, 5], [4, 5]],
            [[5, 2], [5, 2]],
            [[5, 4], [5, 4]],
            [[4, 1], [4, 1]],
            [[2, 1], [2, 1]],
            [[1, 2], [1, 2]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])


def test_knight_blocked():
    ##    0  1  2  3  4  5  6  7       0  1  2  3  4  5  6  7      0  1  2  3  4  5  6  7       0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|  0 |__|##|__|##|__|##|__|##| 0 |__|##|__|##|__|##|__|##| 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|bp|__|##|__|  1 |##|__|##|wp|bp|__|##|__| 1 |##|__|##|__|bp|__|##|__| 1 |##|__|##|bp|bp|__|##|__|
    ## 2 |__|##|__|wp|__|##|__|##|  2 |__|##|__|##|__|##|__|##| 2 |__|##|__|bp|bp|##|__|##| 2 |__|##|__|##|bp|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|  3 |##|__|##|wk|##|__|##|__| 3 |##|__|##|wk|##|__|##|__| 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|  4 |__|##|__|##|__|##|__|##| 4 |__|##|__|##|__|##|__|##| 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|  5 |##|__|##|__|##|__|##|__| 5 |##|__|##|__|##|__|##|__| 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|  6 |__|##|__|##|__|##|__|##| 6 |__|##|__|##|__|##|__|##| 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|  7 |##|__|##|__|##|__|##|__| 7 |##|__|##|__|##|__|##|__| 7 |##|__|##|__|##|__|##|__|

    #  not blocked                  not blocked                 blocked                     blocked

    # 3, 3 -> 1, 4 | squares in possible paths = [3, 4] [2, 4] [2, 3] [1, 3]

    # [1, 4] - [3, 3] = [-2, 1]

    # [2, 3] - [3, 3] = [-1, 0] # up 1 row (negative)
    # [1, 3] - [3, 3] = [-2, 0] # up 2 rows (negative)
    # [3, 4] - [3, 3] = [0, 1] # up 1 column (positive)
    # [2, 4] - [3, 3] = [-1, 1] #  # up 1 row (negative), up 1 column (positive)

    # 3, 3 -> 4, 1 | squares in possible paths = [3, 2] [3, 1] [4, 3] [4, 2]

    # [4, 1] - [3, 3] = [1, -2] 

    # [3, 2] - [3, 3] = [0, -1]  # up 1 column (negative)
    # [3, 1] - [3, 3] = [0, -2]  # up 2 columns (negative)
    # [4, 3] - [3, 3] = [1, 0]   # up 1 row (positive)
    # [4, 2] - [3, 3] = [1, -1]  # up 1 row (positive), up 1 column (negative)

    enemy_positions = [[4, 1], [5, 2], [5, 4], [4, 5], [2, 5], [1, 4], [1, 2], [2, 1]]
    curr_position = [3, 3]

    for i in range(2):
        for enemy_position in enemy_positions:
            path_1_blocking_positions = []
            path_2_blocking_positions = []
            negative_row = True if enemy_position[0] - curr_position[0] < 0 else False
            negative_column = True if enemy_position[1] - curr_position[1] < 0 else False
            if abs(enemy_position[0] - curr_position[0]) == 2:
                path_1_blocking_positions.append([-1 if negative_row else 1, 0])
                path_1_blocking_positions.append([-2 if negative_row else 2, 0])
                path_2_blocking_positions.append([0, -1 if negative_column else 1])
                path_2_blocking_positions.append([-1 if negative_row else 1, -1 if negative_column else 1])
            elif abs(enemy_position[1] - curr_position[1]) == 2:
                path_1_blocking_positions.append([0, -1 if negative_column else 1])
                path_1_blocking_positions.append([0, -2 if negative_column else 2])
                path_2_blocking_positions.append([-1 if negative_row else 1, 0])
                path_2_blocking_positions.append([-1 if negative_row else 1, -1 if negative_column else 1])

            for blocking_index, blocking_position in enumerate(path_1_blocking_positions):
                path_1_blocking_positions[blocking_index] = [blocking_position[0] + curr_position[0], blocking_position[1] + curr_position[1]] 

            for blocking_index, blocking_position in enumerate(path_2_blocking_positions):
                path_2_blocking_positions[blocking_index] = [blocking_position[0] + curr_position[0], blocking_position[1] + curr_position[1]] 
            
            # confirm that being blocked on one of the two paths to a square shouldn't block knight
            for blocking_position in path_1_blocking_positions + path_2_blocking_positions:
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
                curr_game_state["board_state"][enemy_position[0]][enemy_position[1]] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
                curr_game_state["board_state"][blocking_position[0]][blocking_position[1]] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

                prev_game_state = copy.deepcopy(curr_game_state)

                possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
                assert enemy_position in possible_moves_and_captures["possible_moves"]
                assert [enemy_position, enemy_position] in possible_moves_and_captures["possible_captures"]
            # confirm that being blocked on two of the paths to a square should block a knight
            for path_1_blocking_index in range(2):
                for path_2_blocking_index in range(2):
                    path_1_blocking_position = path_1_blocking_positions[path_1_blocking_index]
                    path_2_blocking_position = path_2_blocking_positions[path_2_blocking_index]
                    
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
                    for enemy_position_ in enemy_positions:
                        curr_game_state["board_state"][enemy_position_[0]][enemy_position_[1]] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

                    curr_game_state["board_state"][path_1_blocking_position[0]][path_1_blocking_position[1]] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
                    curr_game_state["board_state"][path_2_blocking_position[0]][path_2_blocking_position[1]] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

                    prev_game_state = copy.deepcopy(curr_game_state)

                    possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
                    expected_positions = copy.deepcopy(enemy_positions)
                    expected_positions.remove(enemy_position)

                    assert enemy_position not in possible_moves_and_captures["possible_moves"]
                    assert [enemy_position, enemy_position] not in possible_moves_and_captures["possible_captures"]

                    # blocking the paths to one possible move can possibly block the path to another possible move
                    # TODO: (nice to have) tighten up validation so that we validate the expected positions exactly
                    count_of_possible_moves_in_expected_positions = 0
                    for expected_position in expected_positions:
                        if expected_position in possible_moves_and_captures["possible_moves"] and \
                        [expected_position, expected_position] in possible_moves_and_captures["possible_captures"]:
                            count_of_possible_moves_in_expected_positions += 1
                    assert count_of_possible_moves_in_expected_positions in [len(enemy_positions) - 2, len(enemy_positions) - 1]


def test_knight_cant_capture_king():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|bK|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|wK|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    enemy_positions = [
        [1, 4], [2, 5], [4, 5], [5, 4],
        [5, 2], [4, 1], [2, 1], [1, 2]
    ]
    curr_position = [3, 3]

    for i in range(2):
        for enemy_position in enemy_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][curr_position[0]][curr_position[0]] = [{"type": f"{'white' if not i else 'black'}_knight"}]
            curr_game_state["board_state"][enemy_position[0]][enemy_position[1]] = [{"type": f"{'black' if not i else 'white'}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
            expected_positions = copy.deepcopy(enemy_positions)
            expected_positions.remove(enemy_position)

            assert sorted(expected_positions) == sorted(possible_moves_and_captures["possible_moves"])
            assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_knight_overflow():
    for i in range(2):
        relative_positions = [[1, 2], [-1, 2], [1, -2], [-1, -2], [2, 1], [-2, 1], [2, -1], [-2, -1]]
        rows_and_columns = [0, 1, 6, 7]

        for row in rows_and_columns:
            for col in rows_and_columns:
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][row][col] = [{"type": f"{'white' if not i else 'black'}_knight"}]
                prev_game_state = copy.deepcopy(curr_game_state)
                for relative_position in relative_positions:
                    ending_position = [relative_position[0] + row, relative_position[1] + col]
                    possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, [row, col])
                    if ending_position[0] >= 8 or ending_position[1] >= 8 or ending_position[0] < 0 or ending_position[1] < 0:
                        assert ending_position not in possible_moves_and_captures["possible_moves"]
                    else:
                        assert ending_position in possible_moves_and_captures["possible_moves"]
                    assert len(possible_moves_and_captures["possible_captures"]) == 0

def test_knight_interactions_with_neutral_monster():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|nd|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|nd|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    relative_positions = [[1, 2], [-1, 2], [1, -2], [-1, -2], [2, 1], [-2, 1], [2, -1], [-2, -1]]

    for i in range(2):
        for health in [5, 1]:
            for monster in ["dragon", "baron_nashor", "board_herald"]:
                for relative_position in relative_positions:
                    monster_position = [3 + relative_position[0], 3 + relative_position[1]]
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
                    curr_game_state["board_state"][monster_position[0]][monster_position[1]] = [
                        {
                            "type": f"neutral_{monster}",
                            "health": health
                        }
                    ]
                    possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, None, [3, 3])
                    assert monster_position in possible_moves_and_captures["possible_moves"]
                    if health > 1:
                        assert len(possible_moves_and_captures["possible_captures"]) == 0
                    else:
                        assert [[monster_position, monster_position]] == possible_moves_and_captures["possible_captures"]


def test_knight_starting_position():
    curr_game_state = copy.deepcopy(starting_game)
    starting_positions = [[0, 1], [0, 6], [7, 1], [7, 6]]

    for starting_position in starting_positions:
        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, None, [starting_position[0], starting_position[1]])
        assert len(possible_moves_and_captures["possible_moves"]) == 0
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_knight_capturing_adjacent_bishop():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|bb|##|__|      ## 1 |##|__|##|__|##|wb|##|__|
    ## 2 |__|##|__|##|__|bp|__|##|      ## 2 |__|##|__|##|__|wp|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|      ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
        curr_game_state["board_state"][1][5] = [{"type": f"{'black' if not i else 'white'}_bishop"}]
        curr_game_state["board_state"][2][5] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, None, [3, 3])

        # moving to [2, 5] would allow the capturing of [1, 5] and [2, 5]
        # moving to [1, 4] would allow the capturing of [1, 5]
        assert sorted(possible_moves_and_captures["possible_captures"]) == sorted([
            [
                [2, 5], 
                [2, 5]
            ], 
            [
                [2, 5], 
                [1, 5]
            ], 
            [
                [1, 4], 
                [1, 5]
            ]
        ])


def test_knight_not_being_allowed_to_move_to_sword_in_stone_square():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|ss|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|ss|__|##|__|
    ## 2 |__|##|__|__|__|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        for sword_in_the_stone_position in [[1, 4], [2, 5], [4, 5], [5, 2], [5, 4], [4, 1], [2, 1], [1, 2]]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["turn_count"] = 0
            curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
            curr_game_state["sword_in_the_stone_position"] = sword_in_the_stone_position

            prev_game_state = copy.deepcopy(curr_game_state)
            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
            assert sword_in_the_stone_position not in possible_moves_and_captures["possible_moves"]


def test_knight_blocked_by_sword_in_stone_and_another_piece():
    # sword in stone buff should be able to block knight
    # (when used with another piece due to every possible move having two paths)
    
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|bk|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|wk|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
        curr_game_state["sword_in_the_stone_position"] = [2, 2]
        curr_game_state["board_state"][2][4] = [{"type": f"{'black' if not i else 'white'}_knight"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
        assert [2, 2] not in possible_moves_and_captures["possible_moves"]


def test_knight_partially_blocked_by_sword_in_stone():
    # even thought the sword in stone buff is blocking the knight, 
    # it should still have access via an alternate route

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|__|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|__|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
        curr_game_state["sword_in_the_stone_position"] = [2, 2]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)
        expected_positions = [[1, 2], [1, 4], [2, 1], [2, 5]]
        for expected_position in expected_positions:
            assert expected_position in possible_moves_and_captures["possible_moves"]


def test_knight_threatening_move():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|bK|__|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wk|##|__|##|__|      ## 3 |##|__|##|wk|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|wK|__|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bk|##|__|##|__|      ## 3 |##|__|##|bk|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    king_positions = [[None, None], [1, 4], [4, 5], [5, 4], [5, 2], [4, 1], [2, 1], [1, 2]]
    for i in range(2):
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_knight"}]
            if king_position[0] is not None:
                curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{'black' if not i else 'white'}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_knight(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_captures"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0
            if king_position[0] is not None:
                assert [king_position] == possible_moves_and_captures["threatening_move"]
            else:
                assert [king_position] not in possible_moves_and_captures["threatening_move"]
                assert len(possible_moves_and_captures["threatening_move"]) == 0