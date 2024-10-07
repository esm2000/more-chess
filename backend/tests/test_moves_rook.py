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
            [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], # [6, 0] file control
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
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|bp|##|__|##|__|##|__|
    ## 2 |__|wp|__|##|__|##|__|##|
    ## 3 |##|wr|##|bp|bp|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|bp|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|wp|##|__|##|__|##|__|
    ## 2 |__|bp|__|##|__|##|__|##|
    ## 3 |##|br|##|wp|wp|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|wp|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][1] = [{"type": f"{'white' if not i else 'black'}_rook"}]

        curr_game_state["board_state"][1][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][2][1] = [{"type": f"{'white' if not i else 'black'}_pawn"}]

        curr_game_state["board_state"][3][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][3][4] = [{"type": f"{'black' if not i else 'white'}_pawn"}]

        curr_game_state["board_state"][6][1] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
    
        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 1]

        possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [3, 0], 
            [3, 2], [3, 3],
            [4, 1], [5, 1], [6, 1]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert sorted([
            [[3, 3], [3, 3]],
            [[6, 1], [6, 1]]
        ]) == sorted(possible_moves_and_captures["possible_captures"])


def test_rook_cant_capture_king():
    # vertical                          # horizontal
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|bK|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wr|##|__|##|__|      ## 3 |##|__|##|wr|bK|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|wK|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|br|##|__|##|__|      ## 3 |##|__|##|br|wK|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    king_positions = [[2, 3], [3, 4], [4, 3], [3, 2]]
    for i in range(2):
        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]
            curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{'black' if not i else 'white'}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_moves"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_rook_interactions_with_neutral_monster():
    # vertical                          # horizontal
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|nd|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wr|##|__|##|__|      ## 3 |##|__|##|wr|nd|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|nd|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|br|##|__|##|__|      ## 3 |##|__|##|br|nd|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    neutral_monster_positions = [[2, 3], [3, 4], [4, 3], [3, 2]]
    for i in range(2):
        for neutral_monster_position in neutral_monster_positions:
            for health in [5, 1]:
                for monster in ["dragon", "baron_nashor", "board_herald"]:
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]
                    curr_game_state["board_state"][neutral_monster_position[0]][neutral_monster_position[1]] = [{
                        "type": f"neutral_{monster}",
                        "health": health
                    }]

                    prev_game_state = copy.deepcopy(curr_game_state)

                    curr_position = [3, 3]
                    
                    possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)
                    assert neutral_monster_position in possible_moves_and_captures["possible_moves"]

                    if health == 1:
                        assert [[neutral_monster_position, neutral_monster_position]] == possible_moves_and_captures["possible_captures"]
                    else:
                        assert [neutral_monster_position, neutral_monster_position] not in possible_moves_and_captures["possible_captures"]
                        assert len(possible_moves_and_captures["possible_captures"]) == 0     


def test_rook_starting_position():
    curr_game_state = copy.deepcopy(starting_game)
    starting_positions = [[0, 0], [0, 7], [7, 0], [7, 7]]

    for starting_position in starting_positions:
        possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, None, [starting_position[0], starting_position[1]])
        assert len(possible_moves_and_captures["possible_moves"]) == 0
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_rook_capturing_adjacent_bishop():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|bp|bb|__|##|__|      ## 1 |##|__|##|wp|wb|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wr|##|__|##|__|      ## 3 |##|__|##|br|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]
        curr_game_state["board_state"][1][3] = [{"type": f"{'black' if not i else 'white'}_pawn"}]
        curr_game_state["board_state"][1][4] = [{"type": f"{'black' if not i else 'white'}_bishop"}]

        possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, None, [3, 3])

        # moving to [1, 3] would allow the capturing of [1, 3] and [1, 4], 
        # moving to [2, 3] would allow the capturing of [1, 4]
        assert sorted(possible_moves_and_captures["possible_captures"]) == sorted([
            [
                [1, 3], 
                [1, 3]
            ], 
            [
                [1, 3], 
                [1, 4]
            ], 
            [
                [2, 3], 
                [1, 4]
            ]
        ])


def test_rook_not_being_allowed_to_move_to_sword_in_stone_square():
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
        [[2, 3]],
        [[3, 4], [3, 5], [3, 6], [3, 7]],
        [[4, 3], [5, 3]],
        [[3, 2], [3, 1], [3, 0]]
    ]

    for i in range(2):
        for positions in position_map:
            for j in range(len(positions)):
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["turn_count"] = 0
                curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]
                curr_game_state["sword_in_the_stone_position"] = positions[j]

                prev_game_state = copy.deepcopy(curr_game_state)
                curr_position = [3, 3]

                possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)
                for k in range(j, len(positions)):
                    assert positions[k] not in possible_moves_and_captures["possible_moves"]
                for k in range(j):
                    assert positions[k] in possible_moves_and_captures["possible_moves"]


def test_rook_file_control_non_center():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|wr|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|br|##|__|##|__|

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 50
        curr_game_state["board_state"][7][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [7, 3]

        possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            # not allowed to cross the center to reach [[1, 3], [0, 3]]
            [6, 3], [5, 3], [4, 3], [3, 3], [2, 3],
            [7, 2], [7, 1], [7, 0],
            [7, 4], [7, 5], [7, 6], [7, 7]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_rook_file_control_center():
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
        curr_game_state["turn_count"] = 50
        curr_game_state["board_state"][3][3] = [{"type": f"{'white' if not i else 'black'}_rook"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_rook(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3], [1, 3], [0, 3],
            [3, 4], [3, 5], [3, 6], [3, 7],
            [4, 3], [5, 3], [6, 3], [7, 3],
            [3, 2], [3, 1], [3, 0]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0