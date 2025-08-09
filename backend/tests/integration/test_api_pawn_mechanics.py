import copy
from fastapi import HTTPException, Response
import pytest

import src.api as api
from src.utils import clear_game
from tests.test_utils import (
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
        
            game_state = api.GameState(**game_on_next_turn)
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
                game_state = api.GameState(**game_on_next_turn)
                game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
                turn_count_for_end_of_pawn_exhange = game["turn_count"]

                assert turn_count_for_end_of_pawn_exhange == turn_count_for_pawn_exchange_initiation + 1
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
                    game_state = api.GameState(**game_on_next_turn)
                    game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")