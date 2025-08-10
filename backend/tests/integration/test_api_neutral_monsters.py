import copy
from fastapi import HTTPException, Response
import pytest

from mocks.starting_game import starting_game
import src.api as api
from src.utils.game_state import clear_game
from tests.test_utils import (
    select_white_piece, select_black_piece, 
    move_white_piece, move_black_piece, 
    select_and_move_white_piece, select_and_move_black_piece
)


def test_spawn_monsters(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn['board_state'] = starting_game['board_state']
    game_on_next_turn["turn_count"] = 9
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_black_piece(game=game, from_row=1, from_col=2, to_row=2, to_col=2)

    assert game["board_state"][4][7][0]["type"] == "neutral_dragon"
    assert game["board_state"][3][0][0]["type"] == "neutral_board_herald"

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 34
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=2, to_row=5, to_col=2)

    assert game["board_state"][3][0][0]["type"] == "neutral_baron_nashor"
    


def test_neutral_monsters_cannot_move(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
        
    game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
    game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
    game_on_next_turn['board_state'][6][0] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]

    game_on_next_turn["turn_count"] = 9

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_black_piece(game=game, from_row=1, from_col=0, to_row=2, to_col=0)

    assert game["turn_count"] == 10
    assert any([piece.get("type") == "neutral_dragon" for piece in game["board_state"][4][7]])
    assert any([piece.get("type") == "neutral_board_herald" for piece in game["board_state"][3][0]])

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][4][7]
        game_on_next_turn["board_state"][4][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][1] = game_on_next_turn["board_state"][3][0]
        game_on_next_turn["board_state"][3][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][4][7]
        game_on_next_turn["board_state"][4][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][1] = game_on_next_turn["board_state"][3][0]
        game_on_next_turn["board_state"][3][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

def test_neutral_monsters_can_be_hurt(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
        
    game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
    game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
    game_on_next_turn['board_state'][6][0] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]
    
    game_on_next_turn["board_state"][2][5] = [{"type": "black_bishop"}]
    game_on_next_turn["board_state"][2][7] = [{"type": "black_rook"}]

    game_on_next_turn["board_state"][6][5] = [{"type": "white_bishop"}]
    game_on_next_turn["board_state"][6][7] = [{"type": "white_rook"}]

    game_on_next_turn["turn_count"] = 9

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_black_piece(game=game, from_row=1, from_col=0, to_row=2, to_col=0)

    assert game["turn_count"] == 10
    assert any([piece.get("type") == "neutral_dragon" for piece in game["board_state"][4][7]])
    assert any([piece.get("type") == "neutral_board_herald" for piece in game["board_state"][3][0]])
    assert any([piece.get("health", 0) == 5 for piece in game["board_state"][4][7]])
    assert any([piece.get("health", 0) == 5 for piece in game["board_state"][3][0]])

    # landing directly on neutral monster
    game = select_white_piece(game=game, row=6, col=5)
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][6][5][0])
    game_on_next_turn["board_state"][6][5] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["board_state"][4][7][0]["health"] == 4

    game = select_black_piece(game=game, row=2, col=5)
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][2][5][0])
    game_on_next_turn["board_state"][2][5] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False)

    assert game["board_state"][4][7][0]["health"] == 3
    assert any([piece.get("type") == "black_bishop" for piece in game["board_state"][4][7]])
    assert not any([piece.get("type") == "white_bishop" for piece in game["board_state"][4][7]])

    # landing adjacent to neutral monster
    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)

    assert game["board_state"][4][7][0]["health"] == 2
    # Bishops can be captured by landing on any square adjacent to it, even those not on diagonals.
    assert not any([piece.get("type") == "black_bishop" for piece in game["board_state"][4][7]])

    game = select_and_move_black_piece(game=game, from_row=2, from_col=7, to_row=3, to_col=7)
    
    assert game["board_state"][4][7][0]["health"] == 1



def test_neutral_monster_captures_after_spawning_on_any_non_king_piece(game):
    # neutral monster should automatically send non-king pieces to the graveyard
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][3][7] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][1] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][7][1] = [{"type": "white_king"}]
 
    game_on_next_turn["turn_count"] = 9

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    
    game = select_and_move_black_piece(game=game, from_row=3, from_col=7, to_row=4, to_col=7)

    assert game["turn_count"] == 10
    assert game["board_state"][4][7][0].get("type") == "neutral_dragon"
    assert "black_pawn" in game["graveyard"] 



def test_neutral_monster_ends_game_after_spawning_on_king(game):
    # neutral monster should automatically send non-king pieces to the graveyard
    for side in ["white", "black"]:
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        
        game_on_next_turn["board_state"][1][0] = [{"type": "black_pawn"}]

        if side == "black":
            game_on_next_turn["board_state"][3][7] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][7][1] = [{"type": "white_king"}]
        else:
            game_on_next_turn["board_state"][7][1] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][4][7] = [{"type": "white_king"}]
    
        game_on_next_turn["turn_count"] = 9

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        if side == "black":
            game = select_and_move_black_piece(game=game, from_row=3, from_col=7, to_row=4, to_col=7)
        else:
            game = select_and_move_white_piece(game=game, from_row=7, from_col=1, to_row=7, to_col=2)

        assert (game["board_state"][4][7] or [{}])[0].get("type") == "neutral_dragon"
        if side == "black":
            assert game["black_defeat"]
            assert not game["white_defeat"]
        else:
            assert game["white_defeat"]
            assert not game["black_defeat"]



def test_neutral_monster_health_regen(game):
    # test that neutral monster heals after 3 turns of not being damaged
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 11
    game_on_next_turn["board_state"][4][7] = [{"type": "neutral_dragon", "health": 5}]

    game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][1][1] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][2][7] = [{"type": "black_pawn"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    
    game = select_and_move_black_piece(game=game, from_row=2, from_col=7, to_row=3, to_col=7)

    assert game["board_state"][4][7][0]["health"] == 4
    assert game["turn_count"] == 12

    game = select_and_move_white_piece(game=game, from_row=7, from_col=7, to_row=7, to_col=6)

    assert game["board_state"][4][7][0]["health"] == 4
    assert game["turn_count"] == 13

    game = select_and_move_black_piece(game=game, from_row=0, from_col=0, to_row=0, to_col=1)

    assert game["board_state"][4][7][0]["health"] == 4
    assert game["turn_count"] == 14

    game = select_and_move_white_piece(game=game, from_row=7, from_col=6, to_row=7, to_col=5)

    assert game["board_state"][4][7][0]["health"] == 5
    assert game["turn_count"] == 15



def test_check_by_neutral_monster(game):
    # test that the game ends when a king stays near a neutral monster
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][5][7] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][7][3] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][0][0] = [{"type": f"black_rook"}]
        game_on_next_turn["turn_count"] = 9

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [0, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

        game_on_next_turn = copy.deepcopy(game)
        
        game_on_next_turn["board_state"][0][1] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)
        
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]
        assert all(["king" in piece.get("type") for piece in game["board_state"][5][7]])
        assert any([piece.get("type") == "neutral_dragon" for piece in game["board_state"][4][7]])
        assert game["check"][side] and not game["check"][opposite_side]            

        if side == "white":
            game = select_white_piece(game=game, row=5, col=7)
        else:
            game = select_and_move_white_piece(game=game, from_row=7, from_col=3, to_row=7, to_col=4)
            game = select_black_piece(game=game, row=5, col=7)

        # must get out of check
        with pytest.raises(HTTPException):
            if side == "white":
                game = move_white_piece(game=game, from_row=5, from_col=7, to_row=5, to_col=6)
            else:
                game = move_black_piece(game=game, from_row=5, from_col=7, to_row=5, to_col=6)

        if side == "white":
            game = move_white_piece(game=game, from_row=5, from_col=7, to_row=6, to_col=7)
        else:
            game = move_black_piece(game=game, from_row=5, from_col=7, to_row=6, to_col=7)

        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]
        assert all(["king" in piece.get("type") for piece in game["board_state"][6][7]])
        assert not game["check"][side] and not game["check"][opposite_side]



def test_capture_behavior_when_neutral_and_normal_piece_are_on_same_square(game):
    # test both when the neutral monster has over 1hp and when it has 1 hp
    for test_case in ["damage", "slay"]:
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"white_king"}]
        game_on_next_turn["board_state"][7][0] = [{"type": f"black_king"}]
        game_on_next_turn["board_state"][1][7] = [{"type": f"white_rook"}]
        game_on_next_turn["board_state"][7][7] = [{"type": f"black_rook"}]

        game_on_next_turn["turn_count"] = 9

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game = select_and_move_black_piece(game=game, from_row=7, from_col=0, to_row=6, to_col=0)

        if test_case == "slay":
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][4][7][0]["health"] = 2
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game = select_white_piece(game=game, row=1, col=7)

        game_on_next_turn = copy.deepcopy(game)
        white_rook = game_on_next_turn["board_state"][1][7][0]
        game_on_next_turn["board_state"][4][7].append(white_rook)
        game_on_next_turn["board_state"][1][7] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
        
        assert len(game["board_state"][4][7]) == 2
        assert game["board_state"][4][7][0].get("health", -1) == (4 if test_case == "damage" else 1)

        game = select_black_piece(game=game, row=7, col=7)

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["captured_pieces"]["black"].append("white_rook")
        game_on_next_turn["gold_count"]["black"] = 10
        game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][7][7][0])
        game_on_next_turn["board_state"][4][7].remove(white_rook)
        game_on_next_turn["board_state"][7][7] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

        if test_case == "damage":
            assert len(game["board_state"][4][7]) == 2
            assert game["board_state"][4][7][0].get("health", -1) == 3
            assert game["board_state"][4][7][1]["type"] == "black_rook"
        else:
            assert len(game["board_state"][4][7]) == 1
            assert game["board_state"][4][7][0]["type"] == "black_rook"
            assert "neutral_dragon" in game["captured_pieces"]["black"]