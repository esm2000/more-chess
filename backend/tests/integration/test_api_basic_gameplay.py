import copy
from fastapi import HTTPException, Response
import pytest

from mocks.starting_game import starting_game
import src.api as api
from src.utils import clear_game
from tests.test_utils import (
    select_white_piece, select_black_piece, 
    move_white_piece, move_black_piece, 
    select_and_move_white_piece, select_and_move_black_piece
)


def test_game_created(game):
    for key in [
        "id",
        "turn_count",
        "position_in_play",
        "board_state",
        "possible_moves",
        "possible_captures",
        "captured_pieces",
        "graveyard",
        "sword_in_the_stone_position",
        "capture_point_advantage",
        "black_defeat",
        "white_defeat",
        "gold_count",
    ]:
        assert key in game
    assert game["turn_count"] == 0
    assert game["position_in_play"] == [None, None]
    pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for i, black_piece in enumerate(game["board_state"][0]):
        assert "black" in black_piece[0]["type"]
        assert pieces[i] in black_piece[0]["type"]
    for i, black_piece in enumerate(game["board_state"][1]):
        if i == 3:
            continue
        assert "black" in black_piece[0]["type"]
        assert "pawn" in black_piece[0]["type"]
    for row in [2, 3, 4, 5]:
        for col in range(8):
            if row == 2 and col == 3:
                assert "black" in black_piece[0]["type"]
                assert "pawn" in black_piece[0]["type"]
            else:
                assert game["board_state"][row][col] is None
    pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    pieces += ["pawn"] * 8
    for i, white_piece in enumerate(game["board_state"][7] + game["board_state"][6]):
        assert "white" in white_piece[0]["type"]
        assert pieces[i] in white_piece[0]["type"]
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0
    assert len(game["captured_pieces"]["white"]) == 0
    assert len(game["captured_pieces"]["black"]) == 0
    assert len(game["graveyard"]) == 0
    assert (
        not game["sword_in_the_stone_position"]
        and not game["capture_point_advantage"]
        and not game["black_defeat"]
        and not game["white_defeat"]
        and not game["gold_count"]["white"]
        and not game["gold_count"]["black"]
    )


def test_piece_selection_and_movement(game):
    # white piece selection and movement
    game = select_white_piece(game=game, row=6, col=0)
    game_on_previous_turn = copy.deepcopy(game)

    assert game["position_in_play"] == [6, 0]
    assert game["turn_count"] == game_on_previous_turn["turn_count"]
    assert sorted(game["possible_moves"]) == sorted([[5, 0], [4, 0]])
    assert len(game["possible_captures"]) == 0

    game = move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)

    assert game["board_state"][5][0][0]["type"] == "white_pawn"
    assert game["board_state"][6][0] is None
    assert game["turn_count"] == 1
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0

    # black piece selection and movement
    game = select_black_piece(game=game, row=1, col=0)
    game_on_previous_turn = copy.deepcopy(game)

    assert game["position_in_play"] == [1, 0]
    assert game["turn_count"] == game_on_previous_turn["turn_count"]
    assert sorted(game["possible_moves"]) == sorted([[2, 0], [3, 0]])
    assert len(game["possible_captures"]) == 0

    game = move_black_piece(game=game, from_row=1, from_col=0, to_row=2, to_col=0)

    assert game["board_state"][2][0][0]["type"] == "black_pawn"
    assert game["board_state"][1][0] is None
    assert game["turn_count"] == 2
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0

    # cache removal
    assert game["turn_count"] == 2
    assert not game["previous_state"].get("previous_state")


def test_moving_more_than_one_piece_should_not_be_allowed(game):
    for position_in_play in [True, False]:
        for side in ["white", "black"]:
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)

            game_on_next_turn['board_state'] = starting_game['board_state']
            if side == "black":
                game_on_next_turn["turn_count"] = 1
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            # same piece types
            if side == "white":
                if position_in_play:
                    game = select_white_piece(game=game, row=6, col=3)

                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    game_on_next_turn["board_state"][5][3] = game_on_next_turn["board_state"][6][3]
                    game_on_next_turn["board_state"][6][3] = None
                    game_on_next_turn["board_state"][5][4] = game_on_next_turn["board_state"][6][4]
                    game_on_next_turn["board_state"][6][4] = None
                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response())

            if side == "black":
                if position_in_play:
                    game = select_black_piece(game=game, row=1, col=4)

                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    game_on_next_turn["board_state"][2][5] = game_on_next_turn["board_state"][1][5]
                    game_on_next_turn["board_state"][1][5] = None
                    game_on_next_turn["board_state"][2][4] = game_on_next_turn["board_state"][1][4]
                    game_on_next_turn["board_state"][1][4] = None
                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response(), player=False)

            # different piece types
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)

            game_on_next_turn['board_state'][1][1] = [{"type": "black_rook"}]
            game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
            game_on_next_turn['board_state'][1][7] = [{"type": "black_pawn"}]

            game_on_next_turn['board_state'][6][6] = [{"type": "white_rook"}]
            game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
            game_on_next_turn['board_state'][6][0] = [{"type": "white_pawn"}]

            if side == "black":
                game_on_next_turn["turn_count"] = 1
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            if side == "white":
                if position_in_play:
                    game = select_white_piece(game=game, row=6, col=6)

                # two pieces at once (and they're not a king and rook)
                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    game_on_next_turn["board_state"][6][7] = game_on_next_turn["board_state"][6][6]
                    game_on_next_turn["board_state"][6][6] = None
                    game_on_next_turn["board_state"][5][0] = game_on_next_turn["board_state"][6][0]
                    game_on_next_turn["board_state"][6][0] = None
                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response())

                # more than two pieces at once 
                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    game_on_next_turn["board_state"][6][7] = game_on_next_turn["board_state"][6][6]
                    game_on_next_turn["board_state"][6][6] = None
                    game_on_next_turn["board_state"][7][6] = game_on_next_turn["board_state"][7][7]
                    game_on_next_turn["board_state"][7][7] = None
                    game_on_next_turn["board_state"][5][0] = game_on_next_turn["board_state"][6][0]
                    game_on_next_turn["board_state"][6][0] = None

                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response())

            if side == "black":
                if position_in_play:
                    game = select_black_piece(game=game, row=1, col=1)

                # two pieces at once (and they're not a king and rook)
                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    game_on_next_turn["board_state"][1][2] = game_on_next_turn["board_state"][1][1]
                    game_on_next_turn["board_state"][1][1] = None
                    game_on_next_turn["board_state"][2][7] = game_on_next_turn["board_state"][1][7]
                    game_on_next_turn["board_state"][1][7] = None
                    
                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response(), player=False)

                # more than two pieces at once
                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    game_on_next_turn["board_state"][1][2] = game_on_next_turn["board_state"][1][1]
                    game_on_next_turn["board_state"][1][1] = None
                    game_on_next_turn["board_state"][0][1] = game_on_next_turn["board_state"][0][0]
                    game_on_next_turn["board_state"][0][0] = None
                    game_on_next_turn["board_state"][2][7] = game_on_next_turn["board_state"][1][7]
                    game_on_next_turn["board_state"][1][7] = None
                    
                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response(), player=False)


def test_invalid_moves_should_not_be_allowed(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn['board_state'] = starting_game['board_state']
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    # white 
    with pytest.raises(HTTPException):
        game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=3, to_col=7)
    
    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=5, to_col=7)

    # black
    with pytest.raises(HTTPException):
        game = select_and_move_black_piece(game=game, from_row=1, from_col=7, to_row=4, to_col=7)

    
def test_that_two_turns_are_not_allowed_from_the_same_side(game):
    # test that when the turn check is enabled that two turns are not allowed from the same side
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][2][0] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][6][0] = [{"type": "white_pawn"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)

    with pytest.raises(HTTPException):
        game = select_white_piece(game=game, row=5, col=0)

    with pytest.raises(HTTPException):
        game = move_white_piece(game=game, from_row=5, from_col=0, to_row=4, to_col=0)

    game = select_and_move_black_piece(game=game, from_row=2, from_col=0, to_row=3, to_col=0)

    with pytest.raises(HTTPException):
        game = select_black_piece(game=game, row=3, col=0)

    with pytest.raises(HTTPException):
        game = move_black_piece(game=game, from_row=3, from_col=0, to_row=4, to_col=0)