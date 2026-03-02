import copy
from fastapi import HTTPException, Response
import pytest

import src.api as api
from src.utils.game_state import clear_game
from tests.test_utils import (
    select_white_piece, select_black_piece,
    select_and_move_white_piece, select_and_move_black_piece
)


def test_pawn_exchange(game):
    for side in ["white", "black"]:
        for piece_type in ["knight", "bishop", "rook", "queen", "king"]:
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
                game_on_next_turn["turn_count"] = 1
        
            game_state = api.GameStateRequest(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            if side == "white":
                game = select_and_move_white_piece(game=game, from_row=1, from_col=3, to_row=0, to_col=3)
            else:
                game = select_and_move_black_piece(game=game, from_row=6, from_col=3, to_row=7, to_col=3)
                        
            turn_count_for_pawn_exchange_initiation = game["turn_count"]
            assert turn_count_for_pawn_exchange_initiation == 0 if side == "white" else 1

            if piece_type != "king":
                # a non-pawn exchange action should not be allowed in the middle of a pawn exchange
                with pytest.raises(HTTPException):
                    if side == "white":
                        game = select_and_move_white_piece(game=game, from_row=3, from_col=4, to_row=4, to_col=4)
                    else:
                        game = select_and_move_black_piece(game=game, from_row=3, from_col=4, to_row=4, to_col=4)

                # the other side should not be allowed to move in the middle of a pawn exchange
                with pytest.raises(HTTPException):
                    if side == "black":
                        game = select_and_move_white_piece(game=game, from_row=3, from_col=4, to_row=4, to_col=4)
                    else:
                        game = select_and_move_black_piece(game=game, from_row=3, from_col=4, to_row=4, to_col=4)

                game_on_next_turn = copy.deepcopy(game)
                if side == "white":
                    game_on_next_turn["board_state"][0][3] = [{"type": f"white_{piece_type}"}]
                else:
                    game_on_next_turn["board_state"][7][3] = [{"type": f"black_{piece_type}"}]
                game_state = api.GameStateRequest(**game_on_next_turn)
                game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
                turn_count_for_end_of_pawn_exchange = game["turn_count"]

                assert turn_count_for_end_of_pawn_exchange == turn_count_for_pawn_exchange_initiation + 1
                assert len(game["board_state"][0 if side=="white"else 7][3] or []) == 1
                assert game["board_state"][0 if side=="white" else 7][3][0]["type"] == f"{side}_{piece_type}"
                assert game["previous_state"]["board_state"][0 if side=="white" else 7][3][0]["type"] == f"{side}_pawn"
            # pawn exchanges for kings should not be allowed
            else:
                with pytest.raises(HTTPException):
                    game_on_next_turn = copy.deepcopy(game)
                    if side == "white":
                        game_on_next_turn["board_state"][0][3] = [{"type": f"white_{piece_type}"}]
                    else:
                        game_on_next_turn["board_state"][7][3] = [{"type": f"black_{piece_type}"}]
                    game_state = api.GameStateRequest(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")


def test_pawn_forward_capture_available_when_capture_point_advantage_is_at_least_two(game):
    # reassign_pawn_buffs runs before determine_possible_moves in the pipeline,
    # so board composition must produce the right advantage (not explicit pawn_buff)
    # white avg = (0+9+1)/3 = 3.33, black avg = (0+1)/2 = 0.5 → advantage = 2.83 → pawn_buff = 2.83
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        # Positive: winning-side pawn can forward capture enemy pawn ahead
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        if side == "white":
            game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][7][1] = [{"type": "white_queen"}]
            game_on_next_turn["board_state"][5][3] = [{"type": "white_pawn"}]
            game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "black_pawn"}]
            game_on_next_turn["turn_count"] = 0
        else:
            game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][0][5] = [{"type": "black_queen"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "black_pawn"}]
            game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][5][3] = [{"type": "white_pawn"}]
            game_on_next_turn["turn_count"] = 1

        game_state = api.GameStateRequest(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            game = select_white_piece(game, row=5, col=3)
            assert [[4, 3], [4, 3]] in game["possible_captures"]
        else:
            game = select_black_piece(game, row=4, col=3)
            assert [[5, 3], [5, 3]] in game["possible_captures"]

        # Negative: losing-side pawn (pawn_buff=0) cannot forward capture
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        if side == "white":
            # Black has advantage; select losing white pawn
            game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][0][5] = [{"type": "black_queen"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "black_pawn"}]
            game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][5][3] = [{"type": "white_pawn"}]
            game_on_next_turn["turn_count"] = 0
        else:
            # White has advantage; select losing black pawn
            game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][7][1] = [{"type": "white_queen"}]
            game_on_next_turn["board_state"][5][3] = [{"type": "white_pawn"}]
            game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "black_pawn"}]
            game_on_next_turn["turn_count"] = 1

        game_state = api.GameStateRequest(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            game = select_white_piece(game, row=5, col=3)
            assert [[4, 3], [4, 3]] not in game["possible_captures"]
        else:
            game = select_black_piece(game, row=4, col=3)
            assert [[5, 3], [5, 3]] not in game["possible_captures"]


def test_pawn_immunity_when_capture_point_advantage_is_at_least_three(game):
    # Board composition must produce pawn_buff > 1 for immunity (code checks pawn_buff > 1)
    # white avg = (0+9+9+1)/4 = 4.75, black avg = (0+1)/2 = 0.5 → advantage = 4.25 → pawn_buff = 3 (capped)
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        # Pawn immunity: enemy pawn cannot diagonally capture the immune pawn
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        if side == "white":
            game_on_next_turn["board_state"][7][6] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][7][1] = [{"type": "white_queen"}]
            game_on_next_turn["board_state"][6][2] = [{"type": "white_queen"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn"}]
            game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][3][4] = [{"type": "black_pawn"}]
            game_on_next_turn["turn_count"] = 1  # black's turn to select attacking pawn
        else:
            game_on_next_turn["board_state"][0][1] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][0][5] = [{"type": "black_queen"}]
            game_on_next_turn["board_state"][1][6] = [{"type": "black_queen"}]
            game_on_next_turn["board_state"][3][4] = [{"type": "black_pawn"}]
            game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn"}]
            game_on_next_turn["turn_count"] = 0  # white's turn to select attacking pawn

        game_state = api.GameStateRequest(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            game = select_black_piece(game, row=3, col=4)
            assert [[4, 3], [4, 3]] not in game["possible_captures"]
        else:
            game = select_white_piece(game, row=4, col=3)
            assert [[3, 4], [3, 4]] not in game["possible_captures"]

        # Non-pawn (rook) should still be able to capture the immune pawn
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        if side == "white":
            # White has advantage, white pawn at [4][3] is immune, black rook at [4][7] can capture it
            game_on_next_turn["board_state"][7][6] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][7][1] = [{"type": "white_queen"}]
            game_on_next_turn["board_state"][6][2] = [{"type": "white_queen"}]
            game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn"}]
            game_on_next_turn["board_state"][0][0] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][4][7] = [{"type": "black_rook"}]
            game_on_next_turn["turn_count"] = 71  # high turn count for rook range
        else:
            # Black has advantage, black pawn at [3][4] is immune, white rook at [3][0] can capture it
            game_on_next_turn["board_state"][0][1] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][0][5] = [{"type": "black_queen"}]
            game_on_next_turn["board_state"][1][6] = [{"type": "black_queen"}]
            game_on_next_turn["board_state"][3][4] = [{"type": "black_pawn"}]
            game_on_next_turn["board_state"][7][7] = [{"type": "white_king"}]
            game_on_next_turn["board_state"][3][0] = [{"type": "white_rook"}]
            game_on_next_turn["turn_count"] = 70  # high turn count for rook range

        game_state = api.GameStateRequest(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            game = select_black_piece(game, row=4, col=7)
            assert [[4, 3], [4, 3]] in game["possible_captures"]
        else:
            game = select_white_piece(game, row=3, col=0)
            assert [[3, 4], [3, 4]] in game["possible_captures"]