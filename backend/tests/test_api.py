import copy
from fastapi import HTTPException, Response
import pytest
import time

from mocks.empty_game import empty_game
from mocks.starting_game import starting_game
import src.api as api
from src.utils import clear_game


def select_white_piece(game, row, col):
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [row, col]
    game_state = api.GameState(**game_on_next_turn)
    updated_game = api.update_game_state(game["id"], game_state, Response())
    return updated_game

def select_black_piece(game, row, col):
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [row, col]
    game_state = api.GameState(**game_on_next_turn)
    updated_game = api.update_game_state(game["id"], game_state, Response(), player=False)
    return updated_game

def move_white_piece(game, from_row, from_col, to_row, to_col):
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][to_row][to_col] = game_on_next_turn["board_state"][from_row][from_col]
    game_on_next_turn["board_state"][from_row][from_col] = None
    game_state = api.GameState(**game_on_next_turn)
    updated_game = api.update_game_state(game["id"], game_state, Response())
    return updated_game

def move_black_piece(game, from_row, from_col, to_row, to_col):
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][to_row][to_col] = game_on_next_turn["board_state"][from_row][from_col]
    game_on_next_turn["board_state"][from_row][from_col] = None
    game_state = api.GameState(**game_on_next_turn)
    updated_game = api.update_game_state(game["id"], game_state, Response(), player=False)
    return updated_game

def select_and_move_white_piece(game, from_row, from_col, to_row, to_col):
    game = select_white_piece(game, from_row, from_col)
    return move_white_piece(game, from_row, from_col, to_row, to_col)


def select_and_move_black_piece(game, from_row, from_col, to_row, to_col):
    game = select_black_piece(game, from_row, from_col)
    return move_black_piece(game, from_row, from_col, to_row, to_col)


@pytest.fixture
def game():
    game = api.create_game()
    yield game
    result = api.delete_game(game["id"])
    time.sleep(5)
    assert result.get("message") == "Success"
    assert "not found" in api.retrieve_game_state(game["id"], Response()).get("message")


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


# TODO: currently broken as its being split up
def test_alter_game(game):
    # invalid moves should not be allowed
        # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][5] = game_on_next_turn["board_state"][6][5]
        game_on_next_turn["board_state"][6][5] = None
        game_on_next_turn["turn_count"] += 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

        # black
        # TODO: change turn so that we fail for the right reasons
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][5] = game_on_next_turn["board_state"][1][5]
        game_on_next_turn["board_state"][1][5] = None
        game_on_next_turn["turn_count"] += 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)

    # buying pieces with not enough gold should not be allowed
        # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "white_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
        
        # black
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "black_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)

    # buying a king or queen should not be allowed
    for side in ["white", "black"]:
        for piece in ["queen", "king"]:
            with pytest.raises(HTTPException):
                game_on_next_turn = copy.deepcopy(game)
                game_on_next_turn["board_state"][5][6] = [{"type": f"{side}_{piece}"}]
                game_state = api.GameState(**game_on_next_turn)
                game = api.update_game_state(game["id"], game_state, Response(), player=side=="white", disable_turn_check=True)

    # buying pieces
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["gold_count"] = {
        "white": 12,
        "black": 12
    }
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][6] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 11
    assert game["turn_count"] == 36

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][7] = [{"type": "white_knight"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 8
    assert game["turn_count"] == 37

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][4] = [{"type": "white_bishop"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 5
    assert game["turn_count"] == 38

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][3] = [{"type": "white_rook"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 0
    assert game["turn_count"] == 39

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)

    assert game["gold_count"]["black"] == 11
    assert game["turn_count"] == 40

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][5] = [{"type": "black_knight"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)

    assert game["gold_count"]["black"] == 8
    assert game["turn_count"] == 41

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][4] = [{"type": "black_bishop"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)

    assert game["gold_count"]["black"] == 5
    assert game["turn_count"] == 42

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_rook"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)

    assert game["gold_count"]["black"] == 0
    assert game["turn_count"] == 43

    # assert that neutral monsters can't move
    for is_player in [True, False]:
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][4][7]
            game_on_next_turn["board_state"][4][7] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=is_player, disable_turn_check=True)

        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][3][1] = game_on_next_turn["board_state"][3][0]
            game_on_next_turn["board_state"][3][0] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=is_player, disable_turn_check=True)

    # assert that additional captured pieces can't be added from nowhere
    for side in ["white", "black"]:
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["captured_pieces"][side].append(f"{'white' if side == 'black' else 'black'}_pawn")
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white", disable_turn_check=True)

    # assert that neutral monsters can be hurt
        # white
    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][6][7][0])
    game_on_next_turn["board_state"][6][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 5
    assert neutral_monster_health_before - neutral_monster_health == 1

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][6][6]
    game_on_next_turn["board_state"][6][6] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 4
    assert neutral_monster_health_before - neutral_monster_health == 1

        # black

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][7] = game_on_next_turn["board_state"][1][7]
    game_on_next_turn["board_state"][1][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 3
    assert neutral_monster_health_before - neutral_monster_health == 1

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][3][7][0])
    game_on_next_turn["board_state"][3][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 2
    assert neutral_monster_health_before - neutral_monster_health == 1

    # assert that capture point advantage is calculated right
    piece_values = {
        "pawn": 1,
        "knight": 3,
        "bishop": 3,
        "rook": 5,
        "queen": 9, 
        "king": None
    }

    for side in ["white", "black"]:
        for piece_type in piece_values:
            game_on_next_turn = copy.deepcopy(game)
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["turn_count"] = 0
            game_on_next_turn["board_state"] = copy.deepcopy(empty_game["board_state"])
            game_on_next_turn["board_state"][3][4] = [{"type": f"black_{piece_type}"}] if side == "white" else [{"type": "black_pawn", "pawn_buff": 0}]
            game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn", "pawn_buff": 0}] if side == "white" else [{"type": f"white_{piece_type}"}]
            if piece_type == "bishop":
                game_on_next_turn["board_state"][3 if side == "white" else 4][4 if side == "white" else 3][0]["energize_stacks"] = 0
            if piece_type != "king":
                game_on_next_turn["board_state"][7][2] = [{"type": f"white_king"}]
                game_on_next_turn["board_state"][0][5] = [{"type": f"black_king"}]
            game_on_next_turn["graveyard"] = []
            game_on_next_turn["gold_count"] = {
                "white": 0,
                "black": 0
            }
            game_on_next_turn["captured_pieces"] = {"white": [], "black": []}
            del game_on_next_turn["previous_state"]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
            game_on_next_turn = copy.deepcopy(game)
            if side == "white":
                game_on_next_turn["board_state"][3][4] = game_on_next_turn["board_state"][4][3]
                game_on_next_turn["board_state"][4][3] = None
                game_on_next_turn["captured_pieces"]["white"].append(f"black_{piece_type}")
            else:
                game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][4]
                game_on_next_turn["board_state"][3][4] = None
                game_on_next_turn["captured_pieces"]["black"].append(f"white_{piece_type}")
            game_state = api.GameState(**game_on_next_turn)
            if piece_type != "king":
                game = api.update_game_state(game["id"], game_state, Response(), player=side=="white", disable_turn_check=True)
                if side == "white":
                    assert game["board_state"][3][4][0]["type"] == "white_pawn"
                    assert game["board_state"][4][3] is None
                    # none of black's pieces are left so its turn is skipped
                    assert game["turn_count"] == 1
                    assert game["capture_point_advantage"] == ["white", piece_values[piece_type]]
                else:
                    assert game["board_state"][4][3][0]["type"] == "black_pawn"
                    assert game["board_state"][3][4] is None
                    assert game["turn_count"] == 1
                    assert game["capture_point_advantage"] == ["black", piece_values[piece_type]]
        # assert that kings can't be captured
            else:
                with pytest.raises(HTTPException):
                    game = api.update_game_state(game["id"], game_state, Response(), player=side=="white", disable_turn_check=True)
    # validate pawn exchange
            if piece_type == "pawn":
                continue
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)
            if side == "white":
                game_on_next_turn["board_state"][1][3] = [{"type": "white_pawn", "pawn_buff": 0}] 
                game_on_next_turn["board_state"][3][4] = [{"type": f"black_king"}]
                game_on_next_turn["board_state"][7][2] = [{"type": f"white_king"}]
            else:
                game_on_next_turn["board_state"][6][3] = [{"type": "black_pawn", "pawn_buff": 0}] 
                game_on_next_turn["board_state"][3][4] = [{"type": f"white_king"}]
                game_on_next_turn["board_state"][0][5] = [{"type": f"black_king"}]
        
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            game_on_next_turn = copy.deepcopy(game)
            if side == "white":
                game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][1][3]
                game_on_next_turn["board_state"][1][3] = None
            else:
                game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][6][3]
                game_on_next_turn["board_state"][6][3] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white", disable_turn_check=True)

            turn_count_for_pawn_exchange_initiation = game["turn_count"]
            game_on_next_turn = copy.deepcopy(game)
            if side == "white":
                game_on_next_turn["board_state"][0][3] = [{"type": f"white_{piece_type}"}]
            else:
                game_on_next_turn["board_state"][7][3] = [{"type": f"black_{piece_type}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white", disable_turn_check=True)
            turn_count_for_end_of_pawn_exhange = game["turn_count"]

            assert turn_count_for_pawn_exchange_initiation == turn_count_for_end_of_pawn_exhange
            assert len(game["board_state"][0 if side=="white"else 7][3] or []) == 1
            assert game["board_state"][0 if side=="white" else 7][3][0]["type"] == f"{side}_{piece_type}"
            assert game["previous_state"]["board_state"][0 if side=="white" else 7][3][0]["type"] == f"{side}_pawn"


def test_bishop_energize_stacks(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    
    game_on_next_turn["board_state"][3][3] = [{"type": "white_bishop", "energize_stacks": 0}]
    game_on_next_turn["board_state"][1][1] = [{"type": "black_pawn", "pawn_buff": 0}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_white_piece(game=game, row=3, col=3)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][1] = [{"type": "white_bishop", "energize_stacks": 0}]
    game_on_next_turn["board_state"][3][3] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["board_state"][1][1][0]["energize_stacks"] == 20


def test_bishop_debuff_application(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][0][0] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][0][6] = [{"type": "black_pawn", "bishop_debuff": 1}]
    game_on_next_turn["board_state"][6][6] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 3}]
    game_on_next_turn["board_state"][5][1] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_white_piece(game=game, row=5, col=1)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][1] = None 
    game_on_next_turn["board_state"][3][3] = [{"type": "white_bishop", "energize_stacks": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["board_state"][0][0][0].get("bishop_debuff") == 1
    assert game["board_state"][0][6][0].get("bishop_debuff") == 2
    assert game["board_state"][6][6][0].get("bishop_debuff") == 3
    assert game["board_state"][6][0][0].get("bishop_debuff") == 3


def test_adjacent_capture_of_bishop(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "white_knight"}]
    game_on_next_turn["board_state"][4][5] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][5][5] = [{"type": "black_bishop", "energize_stacks": 0}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_white_piece(game=game, row=3, col=3)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = None 
    game_on_next_turn["board_state"][4][5] = [{"type": "white_knight"}]
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["board_state"][5][5] is None
    assert sorted(game["captured_pieces"]["white"]) == sorted(["black_bishop", "black_pawn"])


def test_queen_stun(game):
    # make sure queen stuns when expected to 
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [4, 7]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=7, to_row=4, to_col=3)

    assert game["board_state"][3][3][0]["type"] == "black_pawn"
    assert game["board_state"][3][3][0]["is_stunned"]

    # make sure queen doesn't stun when not expected to
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=7, to_row=4, to_col=6)

    assert game["board_state"][3][3][0]["type"] == "black_pawn"
    assert not game["board_state"][3][3][0].get("is_stunned", False)

    # make sure queen is able to apply stun after it captures a piece,
    # opponent moves, and queen moves but doesn't capture a piece
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][0] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][3][7] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [3, 7]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][7] = None
    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    game_on_next_turn[ "captured_pieces"] = {"white": ["black_pawn"], "black": []}
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][0] = None
    game_on_next_turn["board_state"][2][0] = [{"type": "black_pawn"}]
    game_state = api.GameState(**game_on_next_turn)
    game_on_next_turn["previous_state"] = copy.deepcopy(game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=3, from_col=3, to_row=3, to_col=0)

    assert game["board_state"][2][0][0]["type"] == "black_pawn"
    assert game["board_state"][2][0][0].get("is_stunned", False) 
    
    # ensure that the player can't move when stunned
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "white_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "black_queen"}]
    game_on_next_turn["turn_count"] = 1
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_black_piece(game=game, from_row=4, from_col=7, to_row=4, to_col=4)

    with pytest.raises(Exception):
        # should fail due to the stunned piece being the only piece on white's side, causing a turn skip
        game = select_white_piece(game=game, row=3, col=3)

    with pytest.raises(Exception):
        # should fail due to piece being stunned
        game = move_white_piece(game=game, from_row=3, from_col=3, to_row=2, to_col=3)


def test_stun_cleanse(game):
    # ensure that stuns cleanse after a player moves for their next turn
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "white_pawn"}]
    game_on_next_turn["board_state"][3][2] = [{"type": "white_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "black_queen"}]
    game_on_next_turn["turn_count"] = 1
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_black_piece(game=game, from_row=4, from_col=7, to_row=4, to_col=4)

    game = select_and_move_white_piece(game=game, from_row=3, from_col=2, to_row=2, to_col=2)

    game = select_and_move_black_piece(game=game, from_row=4, from_col=4, to_row=4, to_col=5)

    assert game["board_state"][3][3][0]["type"] == "white_pawn"
    assert not game["board_state"][3][3][0].get("is_stunned", False) 


def test_full_bishop_debuff_capture(game):
    # test the capturing mechanism for pieces with full bishop debuff stacks
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=2, to_row=5, to_col=1)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    
    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_on_next_turn["board_state"][6][0] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [6, 0],
        "type": "black_pawn"
    })
    game_on_next_turn["gold_count"]["white"] += 2
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 10
    assert not game["board_state"][6][0]
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_pawn"]
    assert game["bishop_special_captures"] == []


def test_bishop_debuff_double_stack_prevention(game):
    # bishops can be captured by landing on a square diagonally adjacent to it
    # there can be a weird scenario that can lead to double the bishop debuffs 
    # being applied to enemy bishops

    # example situation: 
        # black bishop, posiiton [0, 5]
        # black non-king piece, position [1, 4]
        # black non-king piece, position [1, 6]
        # white bishop, moves to position [2, 5]
        # there can be a bug where the black bishop incorrectly gets two bishop stacks instead of one
    
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][0][5] = [{"type": "black_bishop", "energize_stacks": 0}]
    game_on_next_turn["board_state"][1][4] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_on_next_turn["board_state"][1][6] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_on_next_turn["board_state"][3][4] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=3, from_col=4, to_row=2, to_col=5)

    assert game["board_state"][0][5][0].get("bishop_debuff", 0) == 1
 

def test_full_bishop_debuff_adjacent_application(game):
    # test the capturing mechanism still works when a piece is in danger from being
    # captured adjacently 
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 0}]
    game_on_next_turn["board_state"][7][1] = [{"type": "black_knight", "bishop_debuff": 2}]

    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 95}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=2, to_row=5, to_col=1)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 1
    
    assert game["board_state"][7][1][0]["bishop_debuff"] == 3

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_knight")
    game_on_next_turn["board_state"][7][1] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [7, 1],
        "type": "black_knight"
    })
    game_on_next_turn["gold_count"]["white"] += 6
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    assert not game["board_state"][7][1]
    assert game["board_state"][6][0][0]["type"] == "black_pawn"
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_knight"]
    assert game["bishop_special_captures"] == []


def test_full_bishop_debuff_spare(game):
    # test the ability for pieces with full bishop debuff stacks to be spared
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=2, to_row=5, to_col=1)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][6][0][0]["bishop_debuff"] = 0
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 0
    assert game["board_state"][6][0][0]["type"] == "black_pawn"
    assert game["board_state"][6][0][0]["bishop_debuff"] == 0
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["bishop_special_captures"] == []


def test_multiple_full_bishop_debuffs(game):
    # ensure that game can handle multiple pieces with full bishop debuff stacks well
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][6][2] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=2, to_row=5, to_col=1)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    assert game["board_state"][6][2][0]["bishop_debuff"] == 3
    assert game["board_state"][2][4][0]["bishop_debuff"] == 3

    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_on_next_turn["board_state"][6][0] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [6, 0],
        "type": "black_pawn"
    })
    game_on_next_turn["gold_count"]["white"] += 2
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 10
    assert not game["board_state"][6][0]
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_pawn"]
    assert game["bishop_special_captures"] == []

    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_on_next_turn["board_state"][6][2] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [6, 2],
        "type": "black_pawn"
    })
    game_on_next_turn["gold_count"]["white"] += 2
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 10
    assert not game["board_state"][6][2]
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_pawn", "black_pawn"]
    assert game["bishop_special_captures"] == []

    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][4][0]["bishop_debuff"] = 0
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 0
    assert game["board_state"][2][4][0]["type"] == "black_pawn"
    assert game["board_state"][2][4][0]["bishop_debuff"] == 0
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["bishop_special_captures"] == []


def test_full_bishop_debuff_stacks_prevent_other_moves(game):
    # ensure that game prevent other moves from either side when full bishop debuff stacks are present
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game = select_and_move_white_piece(game=game, from_row=4, from_col=2, to_row=5, to_col=1)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    
    with pytest.raises(HTTPException):
        game = move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)


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
    

def test_skip_one_turn_if_all_non_king_pieces_are_stunned(game):
    # test that when all non-king pieces are stunned that a turn is skipped (with turn check enabled)
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][2][2] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][6][7] = [{"type": "white_queen"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    
    assert game["turn_count"] == 0

    game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=2, to_col=3)

    assert game["turn_count"] == 2
    assert game["board_state"][2][2][0].get("is_stunned", False)
    assert game["board_state"][2][4][0].get("is_stunned", False)

    with pytest.raises(HTTPException):
        game = select_black_piece(game=game, row=2, col=2)

    with pytest.raises(HTTPException):
        game = move_black_piece(game=game, from_row=2, from_col=2, to_row=3, to_col=2)

    game = select_and_move_white_piece(game=game, from_row=2, from_col=3, to_row=6, to_col=7)

    assert game["turn_count"] == 3
    assert not game["board_state"][2][2][0].get("is_stunned", False)
    assert not game["board_state"][2][4][0].get("is_stunned", False)


def test_queen_kill_reset(game):
    # test that a queen is able to go again after getting a kill
    # and that queen is automatically in play upon gaining reset
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][1][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["turn_count"] == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [3, 3]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=True)
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][3] = game_on_next_turn["board_state"][3][3]
    game_on_next_turn["board_state"][3][3] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["position_in_play"] == [1, 3]
    assert game["queen_reset"]
    assert game["turn_count"] == 0

    game = move_white_piece(game=game, from_row=1, from_col=3, to_row=4, to_col=0)

    assert not game["queen_reset"]
    assert game["turn_count"] == 1
    

def test_queen_assist_reset(game):
    # test that a queen is able to go again after getting a assist
    # and that queen is automatically in play upon gaining reset
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][1][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    game_on_next_turn["board_state"][1][2] = [{"type": "white_rook"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["turn_count"] == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [1, 2]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][3] = game_on_next_turn["board_state"][1][2]
    game_on_next_turn["board_state"][1][2] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["position_in_play"] == [3, 3]
    assert game["queen_reset"]
    assert game["turn_count"] == 0

    game = move_white_piece(game=game, from_row=3, from_col=3, to_row=4, to_col=3)

    assert not game["queen_reset"]
    assert game["turn_count"] == 1


def test_queen_turn_reset_limitations(game):
    # test that a turn reset with a queen does not enable other non-queen pieces to move and that the turn reset doesn't stack
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][1][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    game_on_next_turn["board_state"][1][2] = [{"type": "white_rook"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["turn_count"] == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [1, 2]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][3] = game_on_next_turn["board_state"][1][2]
    game_on_next_turn["board_state"][1][2] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["position_in_play"] == [3, 3]
    assert game["queen_reset"]
    assert game["turn_count"] == 0

    with pytest.raises(HTTPException):
        game = select_black_piece(game=game, row=1, col=3)
    
    with pytest.raises(HTTPException):
        game = move_black_piece(game=game, from_row=1, from_col=3, to_row=1, to_col=4)

    game = move_white_piece(game=game, from_row=3, from_col=3, to_row=4, to_col=3)

    assert not game["queen_reset"]
    assert game["turn_count"] == 1

    with pytest.raises(HTTPException):
        game = move_white_piece(game=game, from_row=4, from_col=3, to_row=5, to_col=3)

    game = move_black_piece(game=game, from_row=1, from_col=7, to_row=2, to_col=7)

    assert not game["queen_reset"]
    assert game["turn_count"] == 2


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


def test_sword_in_the_stone_spawn(game):
    # run a test 25 times and see that the sword in the stone spawns in a suitable location every time
    locations = {}
    for _ in range(5):
        for turn in [9, 19, 29, 39, 49]:
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
            game_on_next_turn["board_state"][3][4] = [{"type": "white_pawn"}]
            game_on_next_turn["turn_count"] = turn

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
            
            game = select_and_move_black_piece(game=game, from_row=3, from_col=3, to_row=4, to_col=3)

            if tuple(game["sword_in_the_stone_position"]) in locations:
                locations[tuple(game["sword_in_the_stone_position"])] += 1
            else:
                locations[tuple(game["sword_in_the_stone_position"])] = 1

            assert game["turn_count"] == turn + 1
            assert game["sword_in_the_stone_position"] is not None

    for location in locations:
        assert locations[location] < 13
    assert (4, 3) not in locations
    assert (3, 4) not in locations


def test_sword_in_the_stone_retrieval(game):
    # test that both kings can retrieve the sword in the stone and its accompanying buff
    for retrieval_side in ["white", "black"]:
        opposite_side = "white" if retrieval_side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][0] = [{"type": "black_pawn"}]
        game_on_next_turn["board_state"][3][3] = [{"type": f"{retrieval_side}_king"}]
        game_on_next_turn["board_state"][3][6] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["turn_count"] = 12 if retrieval_side == "white" else 11
        game_on_next_turn["sword_in_the_stone_position"] = [3, 4]

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
        
        if retrieval_side == "white":
            game = select_and_move_white_piece(game=game, from_row=3, from_col=3, to_row=3, to_col=4)
        else:
            game = select_and_move_black_piece(game=game, from_row=3, from_col=3, to_row=3, to_col=4)

        assert game["sword_in_the_stone_position"] is None
        assert game["board_state"][3][4][0]["check_protection"] == 1


def test_sword_in_the_stone_stacks(game):
    # test that the sword in the stone appropiately stacks
    for retrieval_side in ["white", "black"]:
        opposite_side = "white" if retrieval_side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][0] = [{"type": "black_pawn"}]
        game_on_next_turn["board_state"][3][3] = [{"type": f"{retrieval_side}_king", "check_protection": 1}]
        game_on_next_turn["board_state"][3][6] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["turn_count"] = 12 if retrieval_side == "white" else 11
        game_on_next_turn["sword_in_the_stone_position"] = [3, 4]

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if retrieval_side == "white":
            game = select_and_move_white_piece(game=game, from_row=3, from_col=3, to_row=3, to_col=4)
        else:
            game = select_and_move_black_piece(game=game, from_row=3, from_col=3, to_row=3, to_col=4)

        assert game["sword_in_the_stone_position"] is None
        assert game["board_state"][3][4][0]["check_protection"] == 2


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


def test_check(game):
    # test that king can be checked and that the only valid move is to get out of check
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][7][0] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][0][1] = [{"type": f"{side}_rook"}]

        game_on_next_turn["board_state"][5][2] = [{"type": f"{opposite_side}_rook"}]
        game_on_next_turn["board_state"][3][6] = [{"type": f"{opposite_side}_king"}]

        game_on_next_turn["turn_count"] = 1 if side == "white" else 0

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if opposite_side == "white":
            game = select_and_move_white_piece(game=game, from_row=5, from_col=2, to_row=7, to_col=2)
        else:
            game = select_and_move_black_piece(game=game, from_row=5, from_col=2, to_row=7, to_col=2)
        
        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [7, 0]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        # must get out of check
        with pytest.raises(HTTPException):
            if side == "white":
                game = move_white_piece(game=game, from_row=7, from_col=0, to_row=7, to_col=1)
            else:
                game = move_black_piece(game=game, from_row=7, from_col=0, to_row=7, to_col=1)
        
        if side == "white":
            game = move_white_piece(game=game, from_row=7, from_col=0, to_row=6, to_col=0)
        else:
            game = move_black_piece(game=game, from_row=7, from_col=0, to_row=6, to_col=0)

        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [None, None]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]


def test_check_protection_against_check(game):
    # test that check protection works against check
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][7][0] = [{"type": f"{side}_king", "check_protection": 1}]
        game_on_next_turn["board_state"][0][1] = [{"type": f"{side}_rook"}]

        game_on_next_turn["board_state"][5][2] = [{"type": f"{opposite_side}_rook"}]
        game_on_next_turn["board_state"][3][6] = [{"type": f"{opposite_side}_king"}]

        game_on_next_turn["turn_count"] = 1 if side=="white" else 0

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if opposite_side == "white":
            game = move_white_piece(game=game, from_row=5, from_col=2, to_row=7, to_col=2)
        else:
            game = move_black_piece(game=game, from_row=5, from_col=2, to_row=7, to_col=2)

        assert not game["check"][f"white"] and not game["check"][f"black"]
        assert game["position_in_play"] == [None, None]
        assert not game["white_defeat"] and not game["black_defeat"]
        assert not game["board_state"][7][0][0].get("check_protection", 0) 


def test_check_and_needs_a_non_king_piece_to_get_it_out_of_check_through_block(game):
    # test that when king is in check and can't move anywhere to get out of check
    # but another piece of the same side can save it, the game doesn't improperly end

    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        # also ensure that saving that piece is the only valid move
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][1][2] = [{"type": f"{side}_rook"}]

        game_on_next_turn["board_state"][3][3] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][2][1] = [{"type": f"{opposite_side}_rook"}]
        game_on_next_turn["board_state"][7][5] = [{"type": f"{opposite_side}_queen"}]

        game_on_next_turn["turn_count"] = 1 if side == "white" else 2

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if opposite_side == "white":
            game = select_and_move_white_piece(game=game, from_row=7, from_col=5, to_row=7, to_col=0)
        else:
            game = select_and_move_black_piece(game=game, from_row=7, from_col=5, to_row=7, to_col=0)

        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [0, 0]
        assert game["possible_moves"] == []
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        # must get out of check
        with pytest.raises(HTTPException):
            game = move_white_piece(game=game, from_row=0, from_col=0, to_row=1, to_col=0)

        if side == "white":
            game = select_and_move_white_piece(game=game, from_row=1, from_col=2, to_row=1, to_col=0)
        else:
            game = select_and_move_black_piece(game=game, from_row=1, from_col=2, to_row=1, to_col=0)


        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [None, None]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

# TODO: FINISH REFACTORING
def test_check_and_needs_a_non_king_piece_to_get_it_out_of_check_through_capture(game):
    # test that when king is in check and can't move anywhere to get out of check
    # but another piece of the same side can save it, the game doesn't improperly end

    # also ensure that saving that piece is the only valid move white can make
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        # also ensure that saving that piece is the only valid move
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][1][2] = [{"type": f"{side}_rook"}]
        game_on_next_turn["board_state"][0][7] = [{"type": f"{side}_bishop", "energize_stacks": 0}]

        game_on_next_turn["board_state"][3][3] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][2][1] = [{"type": f"{opposite_side}_rook"}]
        game_on_next_turn["board_state"][7][5] = [{"type": f"{opposite_side}_queen"}]

        game_on_next_turn["turn_count"] = 1 if side == "white" else 2

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [7, 5]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][0] = game_on_next_turn["board_state"][7][5]
        game_on_next_turn["board_state"][7][5] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [0, 0]
        assert game["possible_moves"] == []
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        # must get out of check
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["position_in_play"] = [0, 0]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][1][0] = game_on_next_turn["board_state"][0][0]
            game_on_next_turn["board_state"][0][0] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [0, 7]
        game_state = api.GameState(**game_on_next_turn)

        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        assert game["position_in_play"] == [0, 7]

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][0] = game_on_next_turn["board_state"][0][7]
        game_on_next_turn["board_state"][0][7] = None
        game_on_next_turn["captured_pieces"][side].append(f"{opposite_side}_queen")

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [None, None]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]
        assert game["captured_pieces"][side] == [f"{opposite_side}_queen"]


def test_check_and_needs_a_king_piece_to_get_out_of_check_through_capture(game):
    # test that when a king is in check and it's only move to get out is through capture, that it can get out of check
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][1][0] = [{"type": f"{side}_pawn"}]
        game_on_next_turn["board_state"][0][1] = [{"type": f"{side}_pawn"}]

        game_on_next_turn["board_state"][7][7] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][2][0] = [{"type": f"{opposite_side}_bishop"}]

        game_on_next_turn["turn_count"] = 1 if side == "white" else 2

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [2, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][1] = game_on_next_turn["board_state"][2][0]
        game_on_next_turn["board_state"][2][0] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [0, 0]
        assert game["possible_moves"] == [[1, 1]]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [0, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][1] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None
        game_on_next_turn["captured_pieces"][side].append(f"{opposite_side}_bishop")

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [None, None]
        assert game["possible_moves"] == []
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]


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

        if side == "black":
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["position_in_play"] = [7, 3]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

            game_on_next_turn = copy.deepcopy(game)
        
            game_on_next_turn["board_state"][7][4] = game_on_next_turn["board_state"][7][3]
            game_on_next_turn["board_state"][7][3] = None

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [5, 7]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        # must get out of check
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            
            game_on_next_turn["board_state"][5][6] = game_on_next_turn["board_state"][5][7]
            game_on_next_turn["board_state"][5][7] = None

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
            
        game_on_next_turn["board_state"][6][7] = game_on_next_turn["board_state"][5][7]
        game_on_next_turn["board_state"][5][7] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]
        assert all(["king" in piece.get("type") for piece in game["board_state"][6][7]])
        assert not game["check"][side] and not game["check"][opposite_side]


def test_checkmate(game):
    # test checkmate results in loss and that the game cannot be altered afterwards
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]

        game_on_next_turn["board_state"][2][7] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][6][1] = [{"type": f"{opposite_side}_queen"}]
        game_on_next_turn["board_state"][2][2] = [{"type": f"{opposite_side}_rook"}]

        game_on_next_turn["turn_count"] = 1 if side == "white" else 2

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [2, 2]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][2][0] = game_on_next_turn["board_state"][2][2]
        game_on_next_turn["board_state"][2][2] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        last_turn = game["turn_count"]
        board_of_last_turn = game["board_state"]

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [0, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][0] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        assert last_turn == game["turn_count"]
        assert board_of_last_turn == game["board_state"]


def test_check_protection_against_checkmate(game):
    # test that check protection works against checkmate
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king", "check_protection": 1}]

        game_on_next_turn["board_state"][2][7] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][2][2] = [{"type": f"{opposite_side}_rook"}]

        game_on_next_turn["turn_count"] = 1 if side == "white" else 2

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [2, 2]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][2][0] = game_on_next_turn["board_state"][2][2]
        game_on_next_turn["board_state"][2][2] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]


def test_king_cant_put_itself_in_check(game):
    # test that king can't move and put itself into check
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]

        game_on_next_turn["board_state"][2][7] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][6][1] = [{"type": f"{opposite_side}_queen"}]

        game_on_next_turn["turn_count"] = 2 if side == "white" else 1

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [0, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][0][1] = game_on_next_turn["board_state"][0][0]
            game_on_next_turn["board_state"][0][0] = None

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")


def test_king_cant_get_close_to_king(game):
    # test that king can't move next to another king
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        # one other piece is needed to not trigger a stalemate/draw
        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_bishop"}]
        game_on_next_turn["board_state"][3][2] = [{"type": f"{side}_king"}]

        game_on_next_turn["board_state"][3][4] = [{"type": f"{opposite_side}_king"}]

        game_on_next_turn["turn_count"] = 2 if side == "white" else 1

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [3, 2]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
        
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][3][3] = game_on_next_turn["board_state"][3][2]
            game_on_next_turn["board_state"][3][2] = None

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")


def test_game_ends_when_monster_spawns_on_top_of_king(game):
    # test that the game ends when a monster spawns on top of a king
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][4][7] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][7][7] = [{"type": f"{opposite_side}_king"}]
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
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
    
        assert game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]
        assert all(["king" not in piece.get("type") for piece in game["board_state"][4][7]])
        assert any([piece.get("type") == "neutral_dragon" for piece in game["board_state"][4][7]])


def test_draw_with_only_kings(game):
    # test that the game ends in a draw when only kings are left
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]

        game_on_next_turn["board_state"][7][7] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][0][1] = [{"type": f"{opposite_side}_pawn"}]

        game_on_next_turn["turn_count"] = 2 if side == "white" else 1

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [0, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][0][1] = game_on_next_turn["board_state"][0][0]
        game_on_next_turn["board_state"][0][0] = None
        game_on_next_turn["captured_pieces"]["white"].append(f"{opposite_side}_pawn")

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game[f"{side}_defeat"] and game[f"{opposite_side}_defeat"]


def test_draw_with_no_possible_moves(game):
    # test that the game ends in a draw when a player has no possible safe moves to make
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]

        game_on_next_turn["board_state"][1][7] = [{"type": f"{opposite_side}_rook"}]
        game_on_next_turn["board_state"][7][7] = [{"type": f"{opposite_side}_rook"}]
        game_on_next_turn["board_state"][6][6] = [{"type": f"{opposite_side}_king"}]

        game_on_next_turn["turn_count"] = 71 if side == "white" else 70

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [7, 7]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][7][1] = game_on_next_turn["board_state"][7][7]
        game_on_next_turn["board_state"][7][7] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=opposite_side=="white")

        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game[f"{side}_defeat"] and game[f"{opposite_side}_defeat"]


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

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [7, 0]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][6][0] = game_on_next_turn["board_state"][7][0]
        game_on_next_turn["board_state"][7][0] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

        if test_case == "slay":
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][4][7][0]["health"] = 2
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [1, 7]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        white_rook = game_on_next_turn["board_state"][1][7][0]
        game_on_next_turn["board_state"][4][7].append(white_rook)
        game_on_next_turn["board_state"][1][7] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response()) ###
        
        assert len(game["board_state"][4][7]) == 2
        assert game["board_state"][4][7][0].get("health", -1) == (4 if test_case == "damage" else 1)

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [7, 7]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)

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


def test_same_gaem_state_not_allowed():
    pass


# TODO: split test_alter_game() into several test cases (piece selection and movement is enough for original function)
    # create tests for the scenarios described above
    # ensure that proper piece selection is checked

# TODO:     # change API behavior to force a fail when a piece attempts to buy pieces not on its turn or move not on its turn...
# prevent buying of pieces when it's not a side's turn (will break the testcase for it)

# TODO: remove disable_turn_check argument

# TODO: add helperFunction to faciliate selecting pieces (side + position) (AI can help refactor code)
# TODO: add helperFunction to facilitate moving pieces (side + starting position + ending position) (AI can help refactor code)