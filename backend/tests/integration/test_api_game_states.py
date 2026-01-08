import copy
from fastapi import HTTPException, Response
import pytest

import src.api as api
from src.utils.game_state import clear_game
from tests.test_utils import (
    select_white_piece, select_black_piece, 
    select_and_move_white_piece, select_and_move_black_piece
)


def test_capture_point_advantage_calculation(game):
    # TODO: UPDATE TO FOLLOW RULES
    pass
    # piece_values = {
    #     "pawn": 1,
    #     "knight": 3,
    #     "bishop": 3,
    #     "rook": 5,
    #     "queen": 9, 
    #     "king": None
    # }

    # for side in ["white", "black"]:
    #     for piece_type in piece_values:
    #         game = clear_game(game)

    #         game_on_next_turn = copy.deepcopy(game)
    #         game_on_next_turn["turn_count"] = 0
    #         game_on_next_turn["board_state"][3][4] = [{"type": f"black_{piece_type}"}] if side == "white" else [{"type": "black_pawn", "pawn_buff": 0}]
    #         game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn", "pawn_buff": 0}] if side == "white" else [{"type": f"white_{piece_type}"}]
    #         if piece_type == "bishop":
    #             game_on_next_turn["board_state"][3 if side == "white" else 4][4 if side == "white" else 3][0]["energize_stacks"] = 0
    #         if piece_type != "king":
    #             game_on_next_turn["board_state"][7][2] = [{"type": f"white_king"}]
    #             game_on_next_turn["board_state"][0][5] = [{"type": f"black_king"}]
    #         if side == "black":
    #             game_on_next_turn["turn_count"] = 1
    #         game_state = api.GameState(**game_on_next_turn)
    #         game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
            
    #         game_on_next_turn = copy.deepcopy(game)
    #         if side == "white":
    #             game_on_next_turn["board_state"][3][4] = game_on_next_turn["board_state"][4][3]
    #             game_on_next_turn["board_state"][4][3] = None
    #             game_on_next_turn["captured_pieces"]["white"].append(f"black_{piece_type}")
    #         else:
    #             game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][4]
    #             game_on_next_turn["board_state"][3][4] = None
    #             game_on_next_turn["captured_pieces"]["black"].append(f"white_{piece_type}")
    #         game_state = api.GameState(**game_on_next_turn)
    #         if piece_type != "king":
    #             game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")
    #             if side == "white":
    #                 assert game["board_state"][3][4][0]["type"] == "white_pawn"
    #                 assert game["board_state"][4][3] is None
    #                 # none of black's pieces are left so its turn is skipped
    #                 assert game["turn_count"] == 1
    #                 assert game["capture_point_advantage"] == ["white", piece_values[piece_type]]
    #             else:
    #                 assert game["board_state"][4][3][0]["type"] == "black_pawn"
    #                 assert game["board_state"][3][4] is None
    #                 assert game["turn_count"] == 2
    #                 assert game["capture_point_advantage"] == ["black", piece_values[piece_type]]
    

def test_king_cannot_be_captured(game):
    for side in ["white", "black"]:
        game = clear_game(game)

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["turn_count"] = 0
        game_on_next_turn["board_state"][3][4] = [{"type": f"black_king"}] if side == "white" else [{"type": "black_pawn", "pawn_buff": 0}]
        game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn", "pawn_buff": 0}] if side == "white" else [{"type": f"white_king"}]

        if side == "black":
            game_on_next_turn["turn_count"] = 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
        
        game_on_next_turn = copy.deepcopy(game)
        if side == "white":
            game_on_next_turn["board_state"][3][4] = game_on_next_turn["board_state"][4][3]
            game_on_next_turn["board_state"][4][3] = None
            game_on_next_turn["captured_pieces"]["white"].append(f"black_king")
        else:
            game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][4]
            game_on_next_turn["board_state"][3][4] = None
            game_on_next_turn["captured_pieces"]["black"].append(f"white_king")
        game_state = api.GameState(**game_on_next_turn)
        
        with pytest.raises(HTTPException):
            game = api.update_game_state(game["id"], game_state, Response(), player=side=="white")

def test_additional_captured_pieces_cannot_be_added_from_nowhere(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
        
    game_on_next_turn['board_state'][0][0] = [{"type": "black_king"}]
    game_on_next_turn['board_state'][7][7] = [{"type": "white_king"}]
    game_on_next_turn['board_state'][6][0] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_on_next_turn['board_state'][1][0] = [{"type": "black_pawn", "pawn_buff": 0}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
    
    game = select_and_move_white_piece(game=game, from_row=6, from_col=0, to_row=5, to_col=0)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["captured_pieces"]["black"].append(f"white_pawn")
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), player=False)


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

        if side == "white":
            game = select_white_piece(game=game, row=0, col=0)
        else:
            game = select_black_piece(game=game, row=0, col=0)
        
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

        if opposite_side == "white":
            game = select_and_move_white_piece(game=game, from_row=7, from_col=7, to_row=7, to_col=1)
        else:
            game = select_and_move_black_piece(game=game, from_row=7, from_col=7, to_row=7, to_col=1)


        assert not game["check"][f"{side}"] and not game["check"][f"{opposite_side}"]
        assert game[f"{side}_defeat"] and game[f"{opposite_side}_defeat"]

def test_five_dragon_stacks_and_death_mark_capture_flow_with_multiple_pieces_marked(game):
    # test getting the stacks, marking pieces for death, selecting piece for death
    # ensure turn rotation goes as expected
    # ensure that surrendered piece is reflected in the captured_pieces array
    pass

def test_five_dragon_stacks_and_death_mark_capture_flow_with_single_piece_marked(game):
    pass

def test_that_not_choosing_a_piece_to_die_invalidates_game_state(game):
    pass

def test_that_surrendering_a_marked_for_death_piece_while_all_pieces_are_stunned(game):
    # surrendering should be allowed but turn should be skipped after
    pass

def test_queen_with_five_dragon_stacks_turn_reset_interaction(game):
    # flow
        # turn 1 - queen with five dragon stacks fulfills necessary requirements for a turn reset while marking pieces for death
        # turn 2 - queen goes again while marking more pieces for death

    # should we allow the turn reset to be temporarily suspended to allow for surrendering another piece every additional turn?
    # should we allow the turn reset to take precedence and only one surrender has to be made?

    # not sure what the curren timplementation leads to... or if it has bugs...
    pass