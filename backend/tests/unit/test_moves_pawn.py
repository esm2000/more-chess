import copy
import src.moves as moves
from mocks.empty_game import empty_game


def test_pawn_movement():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wp|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bp|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][2 if side == 'black' else 4][3] = copy.deepcopy(curr_game_state["board_state"][5 if side == 'black' else 2][3])
        prev_game_state["board_state"][3][3] = None

        curr_position = [3, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)
        assert [[4 if side == 'black' else 2, 3]] == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0



def test_pawn_capture():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|bp|##|bK|##|__|##|
    ## 5 |##|__|##|wp|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|wp|__|wK|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if side == 'black' else 3][2] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]
        curr_game_state["board_state"][4 if side == 'black' else 3][4] = [{"type": f"{'black' if side == 'black' else 'white'}_king"}]
        curr_game_state["board_state"][5 if side == 'black' else 2][3] = [{"type": f"{'white' if side == 'black' else 'black'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if side == 'black' else 1][3] = [{"type": f"{'white' if side == 'black' else 'black'}_pawn"}]
        
        curr_position = [5 if side == 'black' else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[4 if side == 'black' else 3, 3], [4 if side == 'black' else 3, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert [[[4 if side == 'black' else 3, 2], [4 if side == 'black' else 3, 2]]] == possible_moves_and_captures["possible_captures"]
        

def test_blocked_pawn():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|bK|bp|__|##|__|##|
    ## 5 |##|__|##|wp|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|wK|wp|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if side == 'black' else 3][3] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]
        curr_game_state["board_state"][4 if side == 'black' else 3][2] = [{"type": f"{'black' if side == 'black' else 'white'}_king"}]
        curr_game_state["board_state"][5 if side == 'black' else 2][3] = [{"type": f"{'white' if side == 'black' else 'black'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if side == 'black' else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if side == 'black' else 2][3])
        prev_game_state["board_state"][5 if side == 'black' else 2][3] = None

        curr_position = [5 if side == 'black' else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert len(possible_moves_and_captures["possible_moves"]) == 0
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_buffed_pawn_capture():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|bp|__|##|__|##|
    ## 5 |##|__|##|wp|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|##|wp|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        for pawn_buff in [1, 2]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][4 if side == 'black' else 3][3] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]
            curr_game_state["board_state"][5 if side == 'black' else 2][3] = [{
                                                                    "type": f"{'white' if side == 'black' else 'black'}_pawn",
                                                                    "pawn_buff": pawn_buff
                                                                }]
            
            prev_game_state = copy.deepcopy(curr_game_state)
            prev_game_state["board_state"][6 if side == 'black' else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if side == 'black' else 2][3])
            prev_game_state["board_state"][5 if side == 'black' else 2][3] = None
            
            curr_position = [5 if side == 'black' else 2, 3]

            possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

            assert sorted([[4 if side == 'black' else 3, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
            assert [[[4 if side == 'black' else 3, 3], [4 if side == 'black' else 3, 3]]] == possible_moves_and_captures["possible_captures"]


def test_buffed_pawn_invicibility():
     ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|bp|##|__|##|__|##|
    ## 5 |##|__|##|wp|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|wp|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if side == 'black' else 3][2] = [{
                                                                "type": f"{'black' if side == 'black' else 'white'}_pawn",
                                                                "pawn_buff": 2
                                                            }]
        curr_game_state["board_state"][5 if side == 'black' else 2][3] = [{
                                                                "type": f"{'white' if side == 'black' else 'black'}_pawn"
                                                            }]
        
        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if side == 'black' else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if side == 'black' else 2][3])
        prev_game_state["board_state"][5 if side == 'black' else 2][3] = None
        
        curr_position = [5 if side == 'black' else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[4 if side == 'black' else 3, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_pawn_interactions_with_neutral_monster():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|nd|__|##|__|##|
    ## 5 |##|__|##|wp|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|##|nd|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if side == 'black' else 3][3] = [{
                                                                "type": "neutral_dragon",
                                                            }]
        curr_game_state["board_state"][5 if side == 'black' else 2][3] = [{
                                                                "type": f"{'white' if side == 'black' else 'black'}_pawn"
                                                            }]
        
        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if side == 'black' else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if side == 'black' else 2][3])
        prev_game_state["board_state"][5 if side == 'black' else 2][3] = None
        
        curr_position = [5 if side == 'black' else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[4 if side == 'black' else 3, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|nd|##|__|##|__|##|
    ## 5 |##|__|##|wp|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|bp|__|##|__|##|
    ## 3 |##|__|nd|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for health in [5, 1]:
        for side in ["white", "black"]:
            for boss in ["dragon", "baron_nashor", "board_herald"]:
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][4 if side == 'black' else 3][2] = [{
                                                                        "type": f"neutral_{boss}",
                                                                        "health": health
                                                                    }]
                curr_game_state["board_state"][5 if side == 'black' else 2][3] = [{
                                                                        "type": f"{'white' if side == 'black' else 'black'}_pawn"
                                                                    }]
                
                prev_game_state = copy.deepcopy(curr_game_state)
                prev_game_state["board_state"][6 if side == 'black' else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if side == 'black' else 2][3])
                prev_game_state["board_state"][5 if side == 'black' else 2][3] = None
                
                curr_position = [5 if side == 'black' else 2, 3]

                possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

                assert sorted([[4 if side == 'black' else 3, 3], [4 if side == 'black' else 3, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
                if health != 1:
                    assert len(possible_moves_and_captures["possible_captures"]) == 0
                else:
                    assert [[[4 if side == 'black' else 3, 2], [4 if side == 'black' else 3, 2]]] == possible_moves_and_captures["possible_captures"]


def test_pawn_starting_position():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|wp|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|bp|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][1 if side == 'black' else 6][2] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        
        curr_position = [1 if side == 'black' else 6, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[2 if side == 'black' else 5, 2], [3 if side == 'black' else 4, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|bk|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|wp|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|bp|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|wk|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][1 if side == 'black' else 6][2] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]
        curr_game_state["board_state"][3 if side == 'black' else 4][2] = [{"type": f"{'white' if side == 'black' else 'black'}_knight"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][4 if side == 'black' else 3][4] = copy.deepcopy(curr_game_state["board_state"][3 if side == 'black' else 4][2])
        prev_game_state["board_state"][3 if side == 'black' else 4][2] = None
        
        curr_position = [1 if side == 'black' else 6, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[2 if side == 'black' else 5, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|bq|__|##|__|##|__|
    ## 6 |__|##|wp|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|bp|__|##|__|##|__|
    ## 2 |__|##|wq|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][1 if side == 'black' else 6][2] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]
        curr_game_state["board_state"][2 if side == 'black' else 5][2] = [{"type": f"{'white' if side == 'black' else 'black'}_queen"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][7 if side == 'black' else 0][2] = copy.deepcopy(curr_game_state["board_state"][2 if side == 'black' else 5][2])
        prev_game_state["board_state"][2 if side == 'black' else 5][2] = None
        
        curr_position = [1 if side == 'black' else 6, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert len(possible_moves_and_captures["possible_captures"]) == 0
        assert len(possible_moves_and_captures["possible_captures"]) == 0



def test_pawn_second_move():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|wp|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|bp|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][2 if side == 'black' else 5][2] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][1 if side == 'black' else 6][2] = copy.deepcopy(curr_game_state["board_state"][2 if side == 'black' else 5][2])
        prev_game_state["board_state"][2 if side == 'black' else 5][2] = None
        
        curr_position = [2 if side == 'black' else 5, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[3 if side == 'black' else 4, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert len(possible_moves_and_captures["possible_captures"]) == 0


def test_pawn_en_passant_capture():

    ##    0  1  2  3  4  5  6  7                ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|              ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|bp|##|__|##|__|              ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|              ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|wp|__|##|__|              ## 3 |##|__|##|bp|wp|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|              ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|              ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|              ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|              ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7                ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|              ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|              ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|              ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|__|##|__|##|__|              ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|bp|##|__|##|              ## 4 |__|##|__|wp|bp|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|              ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|wp|__|##|__|##|              ## 6 |__|##|__|##|__|##|__|##| 
    ## 7 |##|__|##|__|##|__|##|__|              ## 7 |##|__|##|__|##|__|##|__|
    
    for side in ["white", "black"]:
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if side == 'black' else 3][4] = [{"type": f"{'black' if side == 'black' else 'white'}_pawn"}]
        curr_game_state["board_state"][4 if side == 'black' else 3][3] = [{"type": f"{'white' if side == 'black' else 'black'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if side == 'black' else 1][3] = [{"type": f"{'white' if side == 'black' else 'black'}_pawn"}]
        prev_game_state["board_state"][4 if side == 'black' else 3][3] = None

        curr_position = [4 if side == 'black' else 3, 4]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[5 if side == 'black' else 2, 4], [5 if side == 'black' else 2, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert [[[5 if side == 'black' else 2, 3], [4 if side == 'black' else 3, 3]]] == possible_moves_and_captures["possible_captures"]


def test_pawn_en_passant_neagtive_1():
    # En passant should be blocked when the opposing king occupies the destination square.

    ##    0  1  2  3  4  5  6  7                ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|              ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|bp|##|__|##|__|   prev       ## 1 |##|__|##|__|##|__|##|__|   prev
    ## 2 |__|##|__|bk|__|##|__|##|              ## 2 |__|##|__|__|__|##|__|##|
    ## 3 |##|__|##|bp|wp|__|##|__|   curr       ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|              ## 4 |__|##|__|wp|bp|##|__|##|   curr
    ## 5 |##|__|##|__|##|__|##|__|              ## 5 |##|__|##|wk|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|              ## 6 |__|##|__|wp|__|##|__|##|   prev
    ## 7 |##|__|##|__|##|__|##|__|              ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        opposing_side = "black" if side == "white" else "white"
        curr_row = 3 if side == "white" else 4
        row_ahead = 2 if side == "white" else 5
        opposing_start_row = 1 if opposing_side == "black" else 6

        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][curr_row][4] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][curr_row][3] = [{"type": f"{opposing_side}_pawn"}]
        curr_game_state["board_state"][row_ahead][3] = [{"type": f"{opposing_side}_king"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][opposing_start_row][3] = [{"type": f"{opposing_side}_pawn"}]
        prev_game_state["board_state"][curr_row][3] = None

        result = moves.get_moves_for_pawn(curr_game_state, prev_game_state, [curr_row, 4])

        assert [row_ahead, 3] not in result["possible_moves"]
        assert not any(capture[0] == [row_ahead, 3] for capture in result["possible_captures"])


def test_pawn_en_passant_neagtive_2():
    # En passant should be blocked when the destination square is already occupied.

    ##    0  1  2  3  4  5  6  7                ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|              ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|bp|##|__|##|__|   prev       ## 1 |##|__|##|__|##|__|##|__|   prev
    ## 2 |__|##|__|wp|__|##|__|##|  destination ## 2 |__|##|__|__|__|##|__|##|
    ## 3 |##|__|##|bp|wp|__|##|__|   curr       ## 3 |##|__|##|__|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|              ## 4 |__|##|__|wp|bp|##|__|##|   curr
    ## 5 |##|__|##|__|##|__|##|__|              ## 5 |##|__|##|bp|##|__|##|__|  destination
    ## 6 |__|##|__|##|__|##|__|##|              ## 6 |__|##|__|wp|__|##|__|##|   prev
    ## 7 |##|__|##|__|##|__|##|__|              ## 7 |##|__|##|__|##|__|##|__|

    for side in ["white", "black"]:
        opposing_side = "black" if side == "white" else "white"
        curr_row = 3 if side == "white" else 4
        row_ahead = 2 if side == "white" else 5
        opposing_start_row = 1 if opposing_side == "black" else 6

        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][curr_row][4] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][curr_row][3] = [{"type": f"{opposing_side}_pawn"}]
        # Destination square is occupied by a friendly pawn
        curr_game_state["board_state"][row_ahead][3] = [{"type": f"{side}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][opposing_start_row][3] = [{"type": f"{opposing_side}_pawn"}]
        prev_game_state["board_state"][curr_row][3] = None

        result = moves.get_moves_for_pawn(curr_game_state, prev_game_state, [curr_row, 4])

        assert [row_ahead, 3] not in result["possible_moves"]
        assert not any(capture[0] == [row_ahead, 3] for capture in result["possible_captures"])


def test_pawn_capturing_adjacent_bishop():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|bb|__|##|__|      ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|bp|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|wp|##|__|##|__|      ## 3 |##|__|##|bk|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|wp|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|wb|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][3][3] = [{"type": f"{side}_pawn"}]
        curr_game_state["board_state"][2 if side == 'white' else 4][4] = [{"type": f"{opposite_side}_pawn"}]
        curr_game_state["board_state"][1 if side == 'white' else 5][4] = [{"type": f"{opposite_side}_bishop"}]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, None, [3, 3])

        # moving to [2, 4] would allow the capturing of [2, 4] and [1, 4]
        # moving to [2, 3] would allow the capturing of [1, 4]
        assert sorted(possible_moves_and_captures["possible_captures"]) == sorted([
            [
                [2, 4] if side == 'white' else [4, 4], 
                [2, 4] if side == 'white' else [4, 4]
            ], 
            [
                [2, 4] if side == 'white' else [4, 4],
                [1, 4] if side == 'white' else [5, 4]
            ], 
            [
                [2, 3] if side == 'white' else [4, 3], 
                [1, 4] if side == 'white' else [5, 4]
            ]
        ])


def test_pawn_not_being_allowed_to_move_to_sword_in_stone_square():
    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|ss|__|##|__|##|
    ## 3 |##|__|##|wp|##|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|
    ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bp|##|__|##|__|
    ## 4 |__|##|__|ss|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|
    for side in ["white", "black"]:
        for sword_in_the_stone_position in ([[2, 2], [2, 3], [2, 4]] if side == 'white' else [[4, 2], [4, 3], [4, 4]]):
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["turn_count"] = 0
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_pawn"}]
            curr_game_state["sword_in_the_stone_position"] = sword_in_the_stone_position

            prev_game_state = copy.deepcopy(curr_game_state)
            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)
            assert sword_in_the_stone_position not in possible_moves_and_captures["possible_moves"]


def test_pawn_threatening_move():
    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|bK|##|__|##|
    ## 3 |##|__|##|wp|##|__|##|__|      ## 3 |##|__|##|wp|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|__|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|

    ##    0  1  2  3  4  5  6  7        ##    0  1  2  3  4  5  6  7
    ## 0 |__|##|__|##|__|##|__|##|      ## 0 |__|##|__|##|__|##|__|##|
    ## 1 |##|__|##|__|##|__|##|__|      ## 1 |##|__|##|__|##|__|##|__| 
    ## 2 |__|##|__|##|__|##|__|##|      ## 2 |__|##|__|##|__|##|__|##|
    ## 3 |##|__|##|bp|##|__|##|__|      ## 3 |##|__|##|bp|__|__|##|__|
    ## 4 |__|##|__|##|__|##|__|##|      ## 4 |__|##|__|##|wK|##|__|##|
    ## 5 |##|__|##|__|##|__|##|__|      ## 5 |##|__|##|__|##|__|##|__|
    ## 6 |__|##|__|##|__|##|__|##|      ## 6 |__|##|__|##|__|##|__|##|
    ## 7 |##|__|##|__|##|__|##|__|      ## 7 |##|__|##|__|##|__|##|__|
    
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        if side == 'white':
            king_positions = [[None, None], [2, 2], [2, 4]]
        else:
            king_positions = [[None, None], [4, 2], [4, 4]]

        for king_position in king_positions:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][3][3] = [{"type": f"{side}_pawn"}]
            if king_position[0] is not None:
                curr_game_state["board_state"][king_position[0]][king_position[1]] = [{"type": f"{opposite_side}_king"}]

            prev_game_state = copy.deepcopy(curr_game_state)

            curr_position = [3, 3]

            possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

            assert [king_position, king_position] not in possible_moves_and_captures["possible_captures"]
            assert len(possible_moves_and_captures["possible_captures"]) == 0
            if king_position[0] is not None:
                assert [king_position] == possible_moves_and_captures["threatening_move"]
            else:
                assert [king_position] not in possible_moves_and_captures["threatening_move"]
                assert len(possible_moves_and_captures["threatening_move"]) == 0

def test_pawn_forward_capture_when_average_piece_value_is_at_least_two_points_higher():
    # might need to change how its calculated in update_capture_point_advantage()
    # might need to implement
    pass

def test_pawn_immunity_when_average_piece_value_is_at_least_three_points_higher():
    # might need to change how its calculated in update_capture_point_advantage()
    # might need to implement
    pass

def test_board_herald_buff_enables_pawn_forward_capture():
    pass


def test_board_herald_buff_enables_pawn_forward_check():
    pass


def test_board_herald_buff_enables_adjacent_pawn_forward_capture():
    # test multiple positions with the board_herald buff location 

    # test multiple piece types with the piece being captured or in danger
    pass


def test_baron_nashor_buff_enables_forward_capture():
    pass


def test_baron_nashor_buff_enables_forward_check():
    pass


def test_baron_nashor_buff_prevents_pawn_capture():
    # test all possible pawn capture scenarios (even en passant and special buffs)
    pass


def test_baron_nashor_buff_negates_baron_nashor_buff_forward_capture():
    # test all possible pawn capture scenarios (even en passant and special buffs)
    pass

def test_pawn_extended_movement_with_one_or_more_dragon_buff_stacks():
    pass

def test_pawn_extended_diagonal_capture_with_one_or_more_dragon_buff_stacks():
    pass

def test_pawn_forward_capture_extended_range_with_one_or_more_dragon_buff_stacks():
    # there are multiple conditions/buffs that allow for a forward capture, account for them all
    pass

def test_pawn_with_three_or_more_dragon_buff_stacks_ignores_unit_collision_with_ally_pawns():
    # test starting square case
    # test extended range starting square case
    # test extended range standard movement case
    # test extended range diagonal capture case
    pass

def test_pawn_with_three_dragon_buff_stacks_does_not_ignore_unit_collision_with_ally_non_pawns():
    pass

def test_pawn_with_three_dragon_buff_stacks_does_not_ignore_unit_collision_with_enemy_pawns():
    pass

def test_pawn_with_three_dragon_buff_stacks_does_not_ignore_unit_collision_with_enemy_non_pawns():
    pass

def test_pawn_with_four_or_more_dragon_buff_stacks_ignores_unit_collision_with_ally_pieces():
    # test all possible ally pieces
    # test starting square case
    # test extended range starting square case
    # test extended range standard movement case
    # test extended range diagonal capture case
    pass

def test_pawn_with_four_or_more_dragon_buff_stacks_does_not_ignore_unit_collision_with_enemy_pieces():
    pass

def test_pawn_with_five_dragon_buff_stacks_marks_enemy_piece_for_death():
    pass

def test_pawn_with_five_dragon_buff_stacks_marks_enemy_pieces_for_death():
    pass

def test_pawn_with_five_dragon_buff_stacks_does_not_mark_enemy_pieces_for_death():
    pass

def test_pawn_with_five_dragon_buff_stacks_does_not_mark_enemy_kings():
    pass