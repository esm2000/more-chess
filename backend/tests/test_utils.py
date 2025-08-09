import copy
from fastapi import Response

import src.api as api

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