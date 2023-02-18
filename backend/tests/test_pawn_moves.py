import copy
import src.moves as moves
from mocks.empty_game import empty_game


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
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if i else 3][2] = [{"type": f"{'black' if i else 'white'}_pawn"}]
        curr_game_state["board_state"][4 if i else 3][4] = [{"type": f"{'black' if i else 'white'}_king"}]
        curr_game_state["board_state"][5 if i else 2][3] = [{"type": f"{'white' if i else 'black'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if i else 1][3] = [{"type": f"{'white' if i else 'black'}_pawn"}]
        
        curr_position = [5 if i else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[4 if i else 3, 3], [4 if i else 3, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert [[[4 if i else 3, 2], [4 if i else 3, 2]]] == possible_moves_and_captures["possible_captures"]
        

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
    
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if i else 3][3] = [{"type": f"{'black' if i else 'white'}_pawn"}]
        curr_game_state["board_state"][4 if i else 3][2] = [{"type": f"{'black' if i else 'white'}_king"}]
        curr_game_state["board_state"][5 if i else 2][3] = [{"type": f"{'white' if i else 'black'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if i else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if i else 2][3])
        prev_game_state["board_state"][5 if i else 2][3] = None

        curr_position = [5 if i else 2, 3]

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

    for i in range(2):
        for pawn_buff in [1, 2]:
            curr_game_state = copy.deepcopy(empty_game)
            curr_game_state["board_state"][4 if i else 3][3] = [{"type": f"{'black' if i else 'white'}_pawn"}]
            curr_game_state["board_state"][5 if i else 2][3] = [{
                                                                    "type": f"{'white' if i else 'black'}_pawn",
                                                                    "pawn_buff": pawn_buff
                                                                }]
            
            prev_game_state = copy.deepcopy(curr_game_state)
            prev_game_state["board_state"][6 if i else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if i else 2][3])
            prev_game_state["board_state"][5 if i else 2][3] = None
            
            curr_position = [5 if i else 2, 3]

            possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

            assert sorted([[4 if i else 3, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
            assert [[[4 if i else 3, 3], [4 if i else 3, 3]]] == possible_moves_and_captures["possible_captures"]


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

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if i else 3][2] = [{
                                                                "type": f"{'black' if i else 'white'}_pawn",
                                                                "pawn_buff": 2
                                                            }]
        curr_game_state["board_state"][5 if i else 2][3] = [{
                                                                "type": f"{'white' if i else 'black'}_pawn"
                                                            }]
        
        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if i else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if i else 2][3])
        prev_game_state["board_state"][5 if i else 2][3] = None
        
        curr_position = [5 if i else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[4 if i else 3, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
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

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if i else 3][3] = [{
                                                                "type": "neutral_dragon",
                                                            }]
        curr_game_state["board_state"][5 if i else 2][3] = [{
                                                                "type": f"{'white' if i else 'black'}_pawn"
                                                            }]
        
        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if i else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if i else 2][3])
        prev_game_state["board_state"][5 if i else 2][3] = None
        
        curr_position = [5 if i else 2, 3]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[4 if i else 3, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
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
        for i in range(2):
            for boss in ["dragon", "baron_nashor", "board_herald"]:
                curr_game_state = copy.deepcopy(empty_game)
                curr_game_state["board_state"][4 if i else 3][2] = [{
                                                                        "type": f"neutral_{boss}",
                                                                        "health": health
                                                                    }]
                curr_game_state["board_state"][5 if i else 2][3] = [{
                                                                        "type": f"{'white' if i else 'black'}_pawn"
                                                                    }]
                
                prev_game_state = copy.deepcopy(curr_game_state)
                prev_game_state["board_state"][6 if i else 1][3] = copy.deepcopy(curr_game_state["board_state"][5 if i else 2][3])
                prev_game_state["board_state"][5 if i else 2][3] = None
                
                curr_position = [5 if i else 2, 3]

                possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

                assert sorted([[4 if i else 3, 3], [4 if i else 3, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
                if health != 1:
                    assert len(possible_moves_and_captures["possible_captures"]) == 0
                else:
                    assert [[[4 if i else 3, 2], [4 if i else 3, 2]]] == possible_moves_and_captures["possible_captures"]


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
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][1 if i else 6][2] = [{"type": f"{'black' if i else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        
        curr_position = [1 if i else 6, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[2 if i else 5, 2], [3 if i else 4, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
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

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][1 if i else 6][2] = [{"type": f"{'black' if i else 'white'}_pawn"}]
        curr_game_state["board_state"][3 if i else 4][2] = [{"type": f"{'white' if i else 'black'}_knight"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][4 if i else 3][4] = copy.deepcopy(curr_game_state["board_state"][3 if i else 4][2])
        prev_game_state["board_state"][3 if i else 4][2] = None
        
        curr_position = [1 if i else 6, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[2 if i else 5, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
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

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][1 if i else 6][2] = [{"type": f"{'black' if i else 'white'}_pawn"}]
        curr_game_state["board_state"][2 if i else 5][2] = [{"type": f"{'white' if i else 'black'}_queen"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][7 if i else 0][2] = copy.deepcopy(curr_game_state["board_state"][2 if i else 5][2])
        prev_game_state["board_state"][2 if i else 5][2] = None
        
        curr_position = [1 if i else 6, 2]

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

    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][2 if i else 5][2] = [{"type": f"{'black' if i else 'white'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][1 if i else 6][2] = copy.deepcopy(curr_game_state["board_state"][2 if i else 5][2])
        prev_game_state["board_state"][2 if i else 5][2] = None
        
        curr_position = [2 if i else 5, 2]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[3 if i else 4, 2]]) == sorted(possible_moves_and_captures["possible_moves"])
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
    
    for i in range(2):
        curr_game_state = copy.deepcopy(empty_game)
        curr_game_state["board_state"][4 if i else 3][4] = [{"type": f"{'black' if i else 'white'}_pawn"}]
        curr_game_state["board_state"][4 if i else 3][3] = [{"type": f"{'white' if i else 'black'}_pawn"}]

        prev_game_state = copy.deepcopy(curr_game_state)
        prev_game_state["board_state"][6 if i else 1][3] = [{"type": f"{'white' if i else 'black'}_pawn"}]
        prev_game_state["board_state"][4 if i else 3][3] = None

        curr_position = [4 if i else 3, 4]

        possible_moves_and_captures = moves.get_moves_for_pawn(curr_game_state, prev_game_state, curr_position)

        assert sorted([[5 if i else 2, 4], [5 if i else 2, 3]]) == sorted(possible_moves_and_captures["possible_moves"])
        assert [[[5 if i else 2, 3], [4 if i else 3, 3]]] == possible_moves_and_captures["possible_captures"]
    