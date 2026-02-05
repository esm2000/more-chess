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


def test_capture_point_advantage_calculation(game):
    piece_values = {
        "pawn": 1,
        "knight": 3,
        "bishop": 3,
        "rook": 5,
        "queen": 9
    }

    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        for piece_type in piece_values:
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)
            
            game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]
            game_on_next_turn["board_state"][1][0] = [{"type": f"{side}_{piece_type}"}]

            game_on_next_turn["board_state"][7][7] = [{"type": f"{opposite_side}_king"}]

            game_on_next_turn["turn_count"] = 2 if side == "white" else 1

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            if side == "white":
                game = select_white_piece(game, row=1, col=0)
            else:
                game = select_black_piece(game, row=1, col=0)

            # the king is worth no points so the capture point advantage is cut in half when caulcating average piece value
            assert game["capture_point_advantage"] == [side, piece_values[piece_type] / 2]


def test_capture_point_advantage_calculation_tie(game):
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"

        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)
        
        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king"}]
        game_on_next_turn["board_state"][1][0] = [{"type": f"{side}_pawn"}]

        game_on_next_turn["board_state"][7][7] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][6][7] = [{"type": f"{opposite_side}_pawn"}]

        game_on_next_turn["turn_count"] = 2 if side == "white" else 1

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            game = select_white_piece(game, row=1, col=0)
        else:
            game = select_black_piece(game, row=1, col=0)

        assert game["capture_point_advantage"] is None

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
        game_on_next_turn["captured_pieces"][side].append(f"{opposite_side}_pawn")

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
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][4][7] = [{"type": f"{side}_rook", "dragon_buff": 5}]
        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king", "dragon_buff": 5}]

        game_on_next_turn["board_state"][7][0] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][5][5] = [{"type": f"{opposite_side}_pawn"}]
        game_on_next_turn["board_state"][4][4] = [{"type": f"{opposite_side}_pawn"}]

        game_on_next_turn["turn_count"] = 44 if side == "white" else 45

        game_on_next_turn["neutral_buff_log"][side]["dragon"]["stacks"] = 5
        game_on_next_turn["neutral_buff_log"][side]["dragon"]["stacks"] = 43 if side == "white" else 44

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        assert not game["neutral_buff_log"][side]["board_herald"]
        assert not game["neutral_buff_log"][side]["baron_nashor"]

        assert game["neutral_buff_log"][opposite_side]["dragon"]["stacks"] == 0
        assert game["neutral_buff_log"][opposite_side]["dragon"]["turn"] == 0
        assert not game["neutral_buff_log"][opposite_side]["board_herald"]
        assert not game["neutral_buff_log"][opposite_side]["baron_nashor"]

        if side == "white":
            game = select_and_move_white_piece(game, from_row=4, from_col=7, to_row=4, to_col=5)
        else:
            game = select_and_move_black_piece(game, from_row=4, from_col=7, to_row=4, to_col=5)
            
        assert not game["board_state"][7][0][0].get("marked_for_death", False)
        assert game["board_state"][5][5][0].get("marked_for_death", False)
        assert game["board_state"][4][4][0].get("marked_for_death", False)

        assert game["turn_count"] == 45 if side == "white" else 46

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][4].pop()
        game_on_next_turn["captured_pieces"][side].append(f"{opposite_side}_pawn")
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), side == "white")

        assert not game["board_state"][7][0][0].get("marked_for_death", False)
        assert not game["board_state"][5][5][0].get("marked_for_death", False)
        
        assert game["turn_count"] == 45 if side == "white" else 46

        assert game["captured_pieces"][side] == [f"{opposite_side}_pawn"]

        if side == "white":
            game=select_and_move_black_piece(game, from_row=5, from_col=5, to_row=6, to_col=5)
        else:
            game=select_and_move_white_piece(game, from_row=7, from_col=0, to_row=7, to_col=1)
        
        assert game["turn_count"] == 46 if side == "white" else 47


def test_five_dragon_stacks_and_death_mark_capture_flow_with_single_piece_marked(game):
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][4][7] = [{"type": f"{side}_rook", "dragon_buff": 5}]
        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king", "dragon_buff": 5}]

        game_on_next_turn["board_state"][7][0] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][5][5] = [{"type": f"{opposite_side}_pawn"}]

        game_on_next_turn["turn_count"] = 44 if side == "white" else 45

        game_on_next_turn["neutral_buff_log"][side]["dragon"]["stacks"] = 5
        game_on_next_turn["neutral_buff_log"][side]["dragon"]["stacks"] = 43 if side == "white" else 44

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        assert not game["neutral_buff_log"][side]["board_herald"]
        assert not game["neutral_buff_log"][side]["baron_nashor"]

        assert game["neutral_buff_log"][opposite_side]["dragon"]["stacks"] == 0
        assert game["neutral_buff_log"][opposite_side]["dragon"]["turn"] == 0
        assert not game["neutral_buff_log"][opposite_side]["board_herald"]
        assert not game["neutral_buff_log"][opposite_side]["baron_nashor"]

        if side == "white":
            game = select_and_move_white_piece(game, from_row=4, from_col=7, to_row=4, to_col=5)
        else:
            game = select_and_move_black_piece(game, from_row=4, from_col=7, to_row=4, to_col=5)
            
        assert not game["board_state"][7][0][0].get("marked_for_death", False)
        assert game["board_state"][5][5][0].get("marked_for_death", False)

        assert game["turn_count"] == 45 if side == "white" else 46

        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][5].pop()
        game_on_next_turn["captured_pieces"][side].append(f"{opposite_side}_pawn")
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), side == "white")

        assert not game["board_state"][7][0][0].get("marked_for_death", False)
        
        assert game["turn_count"] == 45 if side == "white" else 46

        assert game["captured_pieces"][side] == [f"{opposite_side}_pawn"]

        if side == "white":
            game=select_and_move_black_piece(game, from_row=7, from_col=0, to_row=7, to_col=1)
        else:
            game=select_and_move_white_piece(game, from_row=7, from_col=0, to_row=7, to_col=1)
        
        assert game["turn_count"] == 46 if side == "white" else 47


def test_that_not_choosing_a_piece_to_die_invalidates_game_state(game):
    for side in ["white", "black"]:
        opposite_side = "white" if side == "black" else "black"
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][4][7] = [{"type": f"{side}_rook", "dragon_buff": 5}]
        game_on_next_turn["board_state"][0][0] = [{"type": f"{side}_king", "dragon_buff": 5}]

        game_on_next_turn["board_state"][7][0] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][5][5] = [{"type": f"{opposite_side}_pawn"}]
        game_on_next_turn["board_state"][4][4] = [{"type": f"{opposite_side}_pawn"}]

        game_on_next_turn["turn_count"] = 44 if side == "white" else 45

        game_on_next_turn["neutral_buff_log"][side]["dragon"]["stacks"] = 5
        game_on_next_turn["neutral_buff_log"][side]["dragon"]["stacks"] = 43 if side == "white" else 44

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        assert not game["neutral_buff_log"][side]["board_herald"]
        assert not game["neutral_buff_log"][side]["baron_nashor"]

        assert game["neutral_buff_log"][opposite_side]["dragon"]["stacks"] == 0
        assert game["neutral_buff_log"][opposite_side]["dragon"]["turn"] == 0
        assert not game["neutral_buff_log"][opposite_side]["board_herald"]
        assert not game["neutral_buff_log"][opposite_side]["baron_nashor"]

        if side == "white":
            game = select_and_move_white_piece(game, from_row=4, from_col=7, to_row=4, to_col=5)
        else:
            game = select_and_move_black_piece(game, from_row=4, from_col=7, to_row=4, to_col=5)
            
        assert not game["board_state"][7][0][0].get("marked_for_death", False)
        assert game["board_state"][5][5][0].get("marked_for_death", False)
        assert game["board_state"][4][4][0].get("marked_for_death", False)

        assert game["turn_count"] == 45 if side == "white" else 46
        
        with pytest.raises(HTTPException):
            if side == "white":
                game = select_and_move_black_piece(game, from_row=4, from_col=4, to_row=5, to_col=4)
            else:
                game = select_and_move_white_piece(game, from_row=4, from_col=4, to_row=5, to_col=4)


def test_surrendering_a_marked_for_death_piece_while_all_pieces_are_stunned(game):
    # surrendering should be allowed but turn should be skipped after
    for side in ["white"]:
        opposite_side = "white" if side == "black" else "black"
        
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        game_on_next_turn["board_state"][1][0] = [{"type": f"{side}_bishop", "dragon_buff": 5}]
        game_on_next_turn["board_state"][2][0] = [{"type": f"{side}_rook", "dragon_buff": 5}]
        game_on_next_turn["board_state"][6][7] = [{"type": f"{side}_queen", "dragon_buff": 5}]
        game_on_next_turn["board_state"][7][0] = [{"type": f"{side}_king", "dragon_buff": 5}]

        game_on_next_turn["board_state"][0][0] = [{"type": f"{opposite_side}_king"}]
        game_on_next_turn["board_state"][0][1] = [{"type": f"{opposite_side}_pawn"}]
        game_on_next_turn["board_state"][1][1] = [{"type": f"{opposite_side}_pawn"}]

        game_on_next_turn["turn_count"] = 44 if side == "white" else 45

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        if side == "white":
            assert game["turn_count"] == 44
            game = select_and_move_white_piece(game=game, from_row=6, from_col=7, to_row=1, to_col=2)
            assert game["turn_count"] == 45
        else:
            assert game["turn_count"] == 45
            game = select_and_move_black_piece(game=game, from_row=6, from_col=7, to_row=1, to_col=2)
            assert game["turn_count"] == 46
        
        assert not game["board_state"][0][0][0].get("is_stunned", False)
        assert game["board_state"][0][1][0].get("is_stunned", False)
        assert game["board_state"][1][1][0].get("is_stunned", False)

        assert not game["white_defeat"]
        assert not game["black_defeat"]

        assert game["board_state"][0][1][0].get("marked_for_death", False)
        assert game["board_state"][1][1][0].get("marked_for_death", False)

        if side == "white":
            # enemy side moving normally should not be allowed
            with pytest.raises(HTTPException):
                game = select_black_piece(game=game, row=1, col=1)

            with pytest.raises(HTTPException):
                game = move_black_piece(game=game, from_row=1, from_col=1, to_row=2, to_col=1)

            # current side moving normally should not be allowed until an enemy piece is sacrificed
            with pytest.raises(HTTPException):
                game = select_white_piece(game=game, row=7, col=0)
            
            with pytest.raises(HTTPException):
                game = move_white_piece(game=game, from_row=7, from_col=0, to_row=6, to_col=0)

        else:
            # enemy side moving normally should not be allowed
            with pytest.raises(HTTPException):
                game = select_white_piece(game=game, row=1, col=1)

            with pytest.raises(HTTPException):
                game = move_white_piece(game=game, from_row=1, from_col=1, to_row=2, to_col=1)

            # current side moving normally should not be allowed until an enemy piece is sacrificed
            with pytest.raises(HTTPException):
                game = select_black_piece(game=game, row=7, col=0)
            
            with pytest.raises(HTTPException):
                game = move_black_piece(game=game, from_row=7, from_col=0, to_row=6, to_col=0)
        
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][1].pop()
        game_on_next_turn["captured_pieces"][side].append(f"{opposite_side}_pawn")
        game_state = api.GameState(**game_on_next_turn)

        game = api.update_game_state(game["id"], game_state, Response(), side == "white")

        assert game["turn_count"] == 46 if side == "white" else 47

        assert not game["board_state"][0][0][0].get("is_stunned", False)
        assert not game["board_state"][0][1][0].get("is_stunned", False)
        assert not game["board_state"][1][1]

        assert not game["white_defeat"]
        assert not game["black_defeat"]



def test_queen_with_five_dragon_stacks_turn_reset_interaction(game):
    # flow
        # turn 1 - queen with five dragon stacks fulfills necessary requirements for a turn reset while marking pieces for death
        # turn 2 - queen goes again while marking more pieces for death

    # should we allow the turn reset to be temporarily suspended to allow for surrendering another piece every additional turn?
    # should we allow the turn reset to take precedence and only one surrender has to be made?

    # not sure what the curren timplementation leads to... or if it has bugs...
    pass