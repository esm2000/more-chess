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


# TODO: test pawn file control with 1st stack of dragon buff


def test_board_herald_buff_enables_pawn_forward_capture():
    pass


def test_board_herald_buff_enables_adjacent_pawn_forward_capture():
    # test multiple positions with the board_herald buff location 

    # test multiple piece types with the piece being captured or in danger
    pass