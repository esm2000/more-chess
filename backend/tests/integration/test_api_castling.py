import copy
from fastapi import HTTPException, Response
import pytest

from mocks.starting_game import starting_game
import src.api as api
from src.utils.game_state import clear_game
from tests.test_utils import (
    select_and_move_white_piece, select_and_move_black_piece
)


def test_castle_log(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 1

    game_on_next_turn["board_state"][0][0] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][7] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][1][1] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][7][0] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_rook"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert not game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    game = select_and_move_black_piece(game=game, from_row=1, from_col=1, to_row=2, to_col=1)

    assert not game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    # king moved
    game = select_and_move_white_piece(game=game, from_row=7, from_col=4, to_row=7, to_col=5)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    game = select_and_move_black_piece(game=game, from_row=0, from_col=4, to_row=0, to_col=5)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    # left rook moved
    game = select_and_move_white_piece(game=game, from_row=7, from_col=0, to_row=7, to_col=1)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    game = select_and_move_black_piece(game=game, from_row=0, from_col=0, to_row=0, to_col=1)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    # right rook moved
    game = select_and_move_white_piece(game=game, from_row=7, from_col=7, to_row=7, to_col=6)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    game = select_and_move_black_piece(game=game, from_row=0, from_col=7, to_row=0, to_col=6)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert game["castle_log"]["black"]["has_left_rook_moved"]
    assert game["castle_log"]["black"]["has_right_rook_moved"]


def test_left_castles(game):
    # clear spaces in between left rooks and kings
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(starting_game)
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=1, to_row=4, to_col=1)

    game = select_and_move_black_piece(game=game, from_row=1, from_col=1, to_row=3, to_col=1)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=1, to_row=5, to_col=0)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=1, to_row=2, to_col=0)

    game = select_and_move_white_piece(game=game, from_row=6, from_col=3, to_row=4, to_col=3)

    game = select_and_move_black_piece(game=game, from_row=2, from_col=3, to_row=3, to_col=3)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=2, to_row=3, to_col=6)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=2, to_row=4, to_col=6)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=3, to_row=6, to_col=3)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=3, to_row=1, to_col=3)

    # the UI will show a castle button when no position in play is selected and conditions are met
    # so no need to select a position in play
    # white castle
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][4]
    game_on_next_turn["board_state"][7][4] = None

    game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][7][0]
    game_on_next_turn["board_state"][7][0] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    assert any([piece.get("type") == "white_king" for piece in game["board_state"][7][2] or []])
    assert any([piece.get("type") == "white_rook" for piece in game["board_state"][7][3] or []])
    assert not game["board_state"][7][4]
    assert not game["board_state"][7][0]

    # the UI will show a castle button when no position in play is selected and conditions are met
    # so no need to select a position in play
    # black castle
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][0][2] = game_on_next_turn["board_state"][0][4]
    game_on_next_turn["board_state"][0][4] = None

    game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][0][0]
    game_on_next_turn["board_state"][0][0] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    assert any([piece.get("type") == "black_king" for piece in game["board_state"][0][2] or []])
    assert any([piece.get("type") == "black_rook" for piece in game["board_state"][0][3] or []])
    assert not game["board_state"][0][4]
    assert not game["board_state"][0][0]


def test_right_castles(game):
    # clear spaces in between right rooks and kings
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(starting_game)
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=6, to_row=4, to_col=6)

    game = select_and_move_black_piece(game=game, from_row=1, from_col=6, to_row=3, to_col=6)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=6, to_row=5, to_col=7)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=6, to_row=2, to_col=7)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=5, to_row=6, to_col=6)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=5, to_row=1, to_col=6)

    # the UI will show a castle button when no position in play is selected and conditions are met
    # so no need to select a position in play
    # white castle
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][7][6] = game_on_next_turn["board_state"][7][4]
    game_on_next_turn["board_state"][7][4] = None

    game_on_next_turn["board_state"][7][5] = game_on_next_turn["board_state"][7][7]
    game_on_next_turn["board_state"][7][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    assert any([piece.get("type") == "white_king" for piece in game["board_state"][7][6] or []])
    assert any([piece.get("type") == "white_rook" for piece in game["board_state"][7][5] or []])
    assert not game["board_state"][7][4]
    assert not game["board_state"][7][7]

    # the UI will show a castle button when no position in play is selected and conditions are met
    # so no need to select a position in play
    # black castle
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][0][6] = game_on_next_turn["board_state"][0][4]
    game_on_next_turn["board_state"][0][4] = None

    game_on_next_turn["board_state"][0][5] = game_on_next_turn["board_state"][0][7]
    game_on_next_turn["board_state"][0][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert game["castle_log"]["black"]["has_right_rook_moved"]

    assert any([piece.get("type") == "black_king" for piece in game["board_state"][0][6] or []])
    assert any([piece.get("type") == "black_rook" for piece in game["board_state"][0][5] or []])
    assert not game["board_state"][0][4]
    assert not game["board_state"][0][7]


def test_castle_should_not_be_allowed_when_in_check(game):
    # white
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][7] = [{"type": "black_bishop"}]

    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_rook"}]
    game_on_next_turn["turn_count"] = 1

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_black_piece(game=game, from_row=0, from_col=7, to_row=5, to_col=2)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][6] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None

        game_on_next_turn["board_state"][7][5] = game_on_next_turn["board_state"][7][7]
        game_on_next_turn["board_state"][7][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
    
    # black
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][7] = [{"type": "black_rook"}]

    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_bishop"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=7, from_col=7, to_row=2, to_col=2)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][6] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None

        game_on_next_turn["board_state"][0][5] = game_on_next_turn["board_state"][0][7]
        game_on_next_turn["board_state"][0][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)    


def test_castle_should_not_be_allowed_after_moving_king(game):
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][0] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][0][7] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][0] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][6][7] = [{"type": "white_pawn"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=7, from_col=4, to_row=6, to_col=4)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=4, to_row=1, to_col=4)

    game = select_and_move_white_piece(game=game, from_row=6, from_col=4, to_row=7, to_col=4)

    game = select_and_move_black_piece(game=game, from_row=1, from_col=4, to_row=0, to_col=4)

    assert game["castle_log"]["white"]["has_king_moved"]
    assert not game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert game["castle_log"]["black"]["has_king_moved"]
    assert not game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]
    
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None

        game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][7][0]
        game_on_next_turn["board_state"][7][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][6] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None

        game_on_next_turn["board_state"][7][5] = game_on_next_turn["board_state"][7][7]
        game_on_next_turn["board_state"][7][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][2] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None

        game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][6] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None

        game_on_next_turn["board_state"][0][5] = game_on_next_turn["board_state"][0][7]
        game_on_next_turn["board_state"][0][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)


def test_castle_should_not_be_allowed_after_moving_rook(game):
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][0] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][0][7] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][0] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][6][7] = [{"type": "white_pawn"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=7, from_col=0, to_row=7, to_col=1)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=0, to_row=0, to_col=1)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=1, to_row=7, to_col=0)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=1, to_row=0, to_col=0)

    
    assert not game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert not game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert game["castle_log"]["black"]["has_left_rook_moved"]
    assert not game["castle_log"]["black"]["has_right_rook_moved"]

    game = select_and_move_white_piece(game=game, from_row=7, from_col=7, to_row=7, to_col=6)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=7, to_row=0, to_col=6)

    game = select_and_move_white_piece(game=game, from_row=7, from_col=6, to_row=7, to_col=7)

    game = select_and_move_black_piece(game=game, from_row=0, from_col=6, to_row=0, to_col=7)

    assert not game["castle_log"]["white"]["has_king_moved"]
    assert game["castle_log"]["white"]["has_left_rook_moved"]
    assert game["castle_log"]["white"]["has_right_rook_moved"]

    assert not game["castle_log"]["black"]["has_king_moved"]
    assert game["castle_log"]["black"]["has_left_rook_moved"]
    assert game["castle_log"]["black"]["has_right_rook_moved"]

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None

        game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][7][0]
        game_on_next_turn["board_state"][7][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][6] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None

        game_on_next_turn["board_state"][7][5] = game_on_next_turn["board_state"][7][7]
        game_on_next_turn["board_state"][7][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][2] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None

        game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][6] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None

        game_on_next_turn["board_state"][0][5] = game_on_next_turn["board_state"][0][7]
        game_on_next_turn["board_state"][0][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)


def test_castle_should_not_be_allowed_with_pieces_in_path(game):
    game = clear_game(game)
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][7] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][7][5] = [{"type": "white_bishop"}]
    
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][7] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][0][5] = [{"type": "black_bishop"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][6] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None
        game_on_next_turn["board_state"][7][5] = game_on_next_turn["board_state"][7][7]
        game_on_next_turn["board_state"][7][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
        
    game = select_and_move_white_piece(game=game, from_row=7, from_col=5, to_row=6, to_col=4)
        
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][6] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None
        game_on_next_turn["board_state"][0][5] = game_on_next_turn["board_state"][0][7]
        game_on_next_turn["board_state"][0][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)
    
    game = clear_game(game)
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][7][4] = [{"type": "white_king"}]
    game_on_next_turn["board_state"][7][0] = [{"type": "white_rook"}]
    game_on_next_turn["board_state"][7][1] = [{"type": "white_knight"}]
    
    game_on_next_turn["board_state"][0][4] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][0][0] = [{"type": "black_rook"}]
    game_on_next_turn["board_state"][0][1] = [{"type": "black_knight"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None
        game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][7][0]
        game_on_next_turn["board_state"][7][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
        
    game = select_and_move_white_piece(game=game, from_row=7, from_col=1, to_row=5, to_col=2)
        
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][2] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None
        game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)


def test_queenside_castle_should_be_allowed_with_pieces_in_path_amid_4_or_more_dragon_stacks(game):
    for dragon_buff in [4, 5]:
        game = clear_game(game)
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][4] = [{"type": "white_king", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][7][0] = [{"type": "white_rook", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][7][1] = [{"type": "white_knight"}]
        
        game_on_next_turn["board_state"][0][4] = [{"type": "black_king", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][0][0] = [{"type": "black_rook", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][0][1] = [{"type": "black_knight"}]
        
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][4]
        game_on_next_turn["board_state"][7][4] = None
        game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][7][0]
        game_on_next_turn["board_state"][7][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

        assert any([piece.get("type") == "white_king" for piece in game["board_state"][7][2] or []])
        assert any([piece.get("type") == "white_rook" for piece in game["board_state"][7][3] or []])
        assert any([piece.get("type") == "white_knight" for piece in game["board_state"][7][1] or []])
        assert not game["board_state"][7][4]
        assert not game["board_state"][7][0]
            
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][2] = game_on_next_turn["board_state"][0][4]
        game_on_next_turn["board_state"][0][4] = None
        game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

        assert any([piece.get("type") == "black_king" for piece in game["board_state"][0][2] or []])
        assert any([piece.get("type") == "black_rook" for piece in game["board_state"][0][3] or []])
        assert any([piece.get("type") == "black_knight" for piece in game["board_state"][0][1] or []])
        assert not game["board_state"][0][4]
        assert not game["board_state"][0][0]


def test_queenside_castle_should_be_not_allowed_with_pieces_in_path_amid_3_or_less_dragon_stacks(game):
    for dragon_buff in [1, 2, 3]:
        game = clear_game(game)
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][4] = [{"type": "white_king", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][7][0] = [{"type": "white_rook", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][7][1] = [{"type": "white_knight"}]
        
        game_on_next_turn["board_state"][0][4] = [{"type": "black_king", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][0][0] = [{"type": "black_rook", "dragon_buff": dragon_buff}]
        game_on_next_turn["board_state"][0][1] = [{"type": "black_knight"}]
        
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
        
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][4]
            game_on_next_turn["board_state"][7][4] = None
            game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][7][0]
            game_on_next_turn["board_state"][7][0] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())
        
        game = select_and_move_white_piece(game=game, from_row=7, from_col=1, to_row=5, to_col=2)

        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][0][2] = game_on_next_turn["board_state"][0][4]
            game_on_next_turn["board_state"][0][4] = None
            game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][0][0]
            game_on_next_turn["board_state"][0][0] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=False)
