import copy

import src.moves as moves
from mocks.empty_game import empty_game
from mocks.starting_game import starting_game

def test_king_movement():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["turn_count"] = 0
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_king"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_king(curr_game_state, prev_game_state, curr_position)
        assert sorted([
            [2, 3],
            [2, 4],
            [3, 4], 
            [4, 4], 
            [4, 3],
            [4, 2], 
            [3, 2], 
            [2, 2]
        ]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_king_capture():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|bk|##|__|##|
    ## 3 |##|__|##|wK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|wk|##|__|##|
    ## 3 |##|__|##|bK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for enemy_position in [[2, 3], [2, 4], [3, 4], [4, 4], [4, 3], [4, 2], [3, 2], [2, 2]]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["turn_count"] = 0
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_king"}]
            curr_game_state["board_state"][enemy_position[0]][enemy_position[1]] = [{"type": f"{opposite_side}_knight"}]

            prev_game_state = copy.deepcopy(curr_game_state)
            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_king(curr_game_state, prev_game_state, curr_position)
            assert sorted([
                [2, 3],
                [2, 4],
                [3, 4], 
                [4, 4], 
                [4, 3],
                [4, 2], 
                [3, 2], 
                [2, 2]
            ]) == sorted(possible_moves_and_captures["possible_moves"])
            assert [[enemy_position, enemy_position]] == possible_moves_and_captures["possible_captures"]


def test_king_interactions_with_neutral_monsters():
    # vertical                          # horizontal                        # diagonal
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
    neutral_monster_positions = [[2, 3], [2, 4], [3, 4], [4, 4], [4, 3], [4, 2], [3, 2], [2, 2]]
    for side in ["white", "black"]:
        for neutral_monster_position in neutral_monster_positions:
            for health in [5, 1]:
                for monster in ["dragon", "baron_nashor", "board_herald"]:
                    curr_game_state = copy.deepcopy(empty_game)
                    curr_game_state["board_state"][3][3] = [{"type": f"{side}_king"}]
                    curr_game_state["board_state"][neutral_monster_position[0]][neutral_monster_position[1]] = [{
                        "type": f"neutral_{monster}",
                        "health": health
                    }]

                    prev_game_state = copy.deepcopy(curr_game_state)

                    curr_position = [3, 3]
                    
                    possible_moves_and_captures = moves.get_moves_for_king(curr_game_state, prev_game_state, curr_position)
                    

                    if health == 1:
                        assert neutral_monster_position in possible_moves_and_captures["possible_moves"]
                        assert [[neutral_monster_position, neutral_monster_position]] == possible_moves_and_captures["possible_captures"]
                    else:
                        assert neutral_monster_position not in possible_moves_and_captures["possible_moves"]
                        assert [neutral_monster_position, neutral_monster_position] not in possible_moves_and_captures["possible_captures"]
                        assert len(possible_moves_and_captures["possible_captures"]) == 0     


def test_king_starting_positions():
    curr_game_state = copy.deepcopy(starting_game)
    starting_positions = [[0, 4], [7, 4]]

    for starting_position in starting_positions:
        possible_moves_and_captures = moves.get_moves_for_king(curr_game_state, None, [starting_position[0], starting_position[1]])
        if starting_position == [0, 4]:
            assert possible_moves_and_captures["possible_moves"] == [[1, 3]]
        elif starting_position == [7, 4]:
            assert len(possible_moves_and_captures["possible_moves"]) == 0
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_king_capturing_adjacent_bishop():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|##|bb|__|##|      ## 2 |__|##|__|##|__|wb|__|##|
    ## 3 |##|__|##|wK|##|__|##|__|      ## 3 |##|__|##|bK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_king"}]
        curr_game_state["board_state"][2][5] = [{"type": f"{opposite_side}_bishop"}]
        possible_moves_and_captures = moves.get_moves_for_king(curr_game_state, None, [3, 3])
        assert [[2, 4], [2, 5]] in sorted(possible_moves_and_captures["possible_captures"])

def test_king_being_allowed_to_move_to_sword_in_stone_square():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|ss|##|__|##|
    ## 3 |##|__|##|wK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|ss|##|__|##|
    ## 3 |##|__|##|bK|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        for sword_in_the_stone_position in [[2, 3], [2, 4], [3, 4], [4, 4], [4, 3], [4, 2], [3, 2], [2, 2]]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["turn_count"] = 0
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_king"}]
            curr_game_state["sword_in_the_stone_position"] = sword_in_the_stone_position

            prev_game_state = copy.deepcopy(curr_game_state)
            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_king(curr_game_state, prev_game_state, curr_position)
            assert sword_in_the_stone_position in possible_moves_and_captures["possible_moves"]
