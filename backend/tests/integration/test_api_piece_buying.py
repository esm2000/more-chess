import copy
from fastapi import HTTPException, Response
import pytest

import src.api as api
from src.utils import clear_game
from tests.test_utils import select_and_move_white_piece




def test_buying_pieces_with_not_enough_gold_should_not_be_allowed(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    
    game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
    game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
    game_on_next_turn['board_state'][6][7] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["gold_count"]["white"] == 0
    assert game["gold_count"]["black"] == 0

    # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "white_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
    
    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)
    
    # black
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "black_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

    assert not game["board_state"][5][6]
    

def test_buying_kings_and_queens_should_not_be_allowed(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    
    game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
    game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
    game_on_next_turn['board_state'][6][7] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]

    game_on_next_turn["gold_count"] = {"white": 12, "black": 12}

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    # white
    for piece in ["queen", "king"]:
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][5][6] = [{"type": f"white_{piece}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())
    
    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)

    # black
    for piece in ["queen", "king"]:
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][5][6] = [{"type": f"black_{piece}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=False)

def test_buying_pieces(game):
    pieces = {
        "pawn": 1,
        "knight": 3,
        "bishop": 3,
        "rook": 5
    }
    for piece in pieces:
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        
        game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
        game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
        game_on_next_turn['board_state'][6][7] = [{"type": "white_pawn", "pawn_buff": 0}]
        game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]

        game_on_next_turn["gold_count"] = {"white": 5, "black": 5}

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        # white
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": f"white_{piece}"}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

        assert game["gold_count"]["white"] == 5 - pieces[piece]

        # black
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][6] = [{"type": f"black_{piece}"}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

        assert game["gold_count"]["black"] == 5 - pieces[piece]


def test_buying_pieces_when_it_is_not_your_turn_not_allowed(game):
    pieces = {
        "pawn": 1,
        "knight": 3,
        "bishop": 3,
        "rook": 5
    }
    for piece in pieces:
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        
        game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
        game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
        game_on_next_turn['board_state'][6][7] = [{"type": "white_pawn", "pawn_buff": 0}]
        game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]

        game_on_next_turn["gold_count"] = {"white": 5, "black": 5}

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        assert game["turn_count"] == 0

        # black
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][0][6] = [{"type": f"black_{piece}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=False)

        game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)

        # white
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][5][6] = [{"type": f"white_{piece}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())