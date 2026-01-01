import copy
from fastapi import HTTPException, Response
import pytest

import src.api as api
from src.utils.game_state import clear_game
from tests.test_utils import (
    select_white_piece, select_black_piece, 
    move_white_piece, move_black_piece, 
    select_and_move_white_piece, select_and_move_black_piece
)


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
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["position_in_play"] = [0, 0]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][1][0] = game_on_next_turn["board_state"][0][0]
            game_on_next_turn["board_state"][0][0] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())
            if side == "white":
                game = select_and_move_white_piece(game=game, from_row=0, from_col=0, to_row=1, to_col=0)
            else:
                game = select_and_move_black_piece(game=game, from_row=0, from_col=0, to_row=1, to_col=0)

        if side == "white":
            game = select_white_piece(game=game, row=0, col=7)
        else:
            game = select_black_piece(game=game, row=0, col=7)

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

        if opposite_side == "white":
            game = select_and_move_white_piece(game=game, from_row=2, from_col=0, to_row=1, to_col=1)
        else:
            game = select_and_move_black_piece(game=game, from_row=2, from_col=0, to_row=1, to_col=1)

        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game["position_in_play"] == [0, 0]
        assert game["possible_moves"] == [[1, 1]]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        if side == "white":
            game = select_white_piece(game=game, row=0, col=0)
        else:
            game = select_black_piece(game=game, row=0, col=0)

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

        if opposite_side == "white":
            game = select_and_move_white_piece(game=game, from_row=2, from_col=2, to_row=2, to_col=0)
        else:
            game = select_and_move_black_piece(game=game, from_row=2, from_col=2, to_row=2, to_col=0)

        assert game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]

        last_turn = game["turn_count"]
        board_of_last_turn = game["board_state"]

        if side == "white":
            game = select_and_move_white_piece(game=game, from_row=0, from_col=0, to_row=1, to_col=0)
        else:
            game = select_and_move_black_piece(game=game, from_row=0, from_col=0, to_row=1, to_col=0)

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

        if opposite_side == "white":
            game = select_and_move_white_piece(game=game, from_row=2, from_col=2, to_row=2, to_col=0)
        else:
            game = select_and_move_black_piece(game=game, from_row=2, from_col=2, to_row=2, to_col=0)

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

        if side == "white":
            game = select_white_piece(game=game, row=0, col=0)
        else:
            game = select_black_piece(game=game, row=0, col=0)

        with pytest.raises(HTTPException):
            if side == "white":
                game = move_white_piece(game=game, from_row=0, from_col=0, to_row=0, to_col=1)
            else:
                game = move_black_piece(game=game, from_row=0, from_col=0, to_row=0, to_col=1)



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

        if side == "white":
            game = select_white_piece(game=game, row=3, col=2)
        else:
            game = select_black_piece(game=game, row=3, col=2)
        
        with pytest.raises(HTTPException):
            if side == "white":
                game = move_white_piece(game=game, from_row=3, from_col=2, to_row=3, to_col=3)
            else:
                game = move_black_piece(game=game, from_row=3, from_col=2, to_row=3, to_col=3)


def test_king_in_check_from_pawn_with_board_herald_buff(game):
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        if side == "white":
            game_on_next_turn["board_state"][3][0] = [{"type": f"{opposite_side}_king"}]
            game_on_next_turn["board_state"][1][7] = [{"type": f"{opposite_side}_pawn"}]

            game_on_next_turn["board_state"][4][0] = [{"type": f"{side}_pawn"}]
            game_on_next_turn["board_state"][7][0] = [{"type": f"{side}_rook", "board_herald_buff": True}]
            game_on_next_turn["board_state"][7][7] = [{"type": f"{side}_king"}]

        else:
            game_on_next_turn["board_state"][4][0] = [{"type": f"{opposite_side}_king"}]
            game_on_next_turn["board_state"][6][7] = [{"type": f"{opposite_side}_pawn"}]

            game_on_next_turn["board_state"][3][0] = [{"type": f"{side}_pawn"}]
            game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_rook", "board_herald_buff": True}]
            game_on_next_turn["board_state"][0][7] = [{"type": f"{side}_king"}]

        game_on_next_turn["turn_count"] = 0 if side == "white" else 1
        game_on_next_turn["neutral_buff_log"][side]["board_herald"] = True
        
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            game = select_and_move_white_piece(game=game, from_row=7, from_col=0, to_row=5, to_col=0)
        else:
            game = select_and_move_black_piece(game=game, from_row=0, from_col=0, to_row=2, to_col=0)

        assert game["check"][opposite_side] and not game["check"][side]
        assert not game[f"{side}_defeat"] and not game[f"{opposite_side}_defeat"]


def test_king_in_check_from_pawn_with_baron_nashor_buff(game):
    pass


def test_that_a_user_can_surrender_a_piece_while_in_check(game):
    pass