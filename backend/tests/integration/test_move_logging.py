import copy
from fastapi import Response

import src.api as api
from src.database import mongo_client
from tests.test_utils import (
    select_white_piece,
    select_and_move_white_piece,
    select_and_move_black_piece,
)


def test_move_history_accumulates(game):
    game_id = game["id"]

    # Turn 1: white pawn a2 -> a3 (row 6, col 0 -> row 5, col 0)
    game = select_and_move_white_piece(game, 6, 0, 5, 0)

    # Turn 2: black pawn a7 -> a6 (row 1, col 0 -> row 2, col 0)
    game = select_and_move_black_piece(game, 1, 0, 2, 0)

    # Turn 3: white pawn b2 -> b3 (row 6, col 1 -> row 5, col 1)
    game = select_and_move_white_piece(game, 6, 1, 5, 1)

    # Query move logs
    move_logs = list(
        mongo_client["game_db"]["game_moves"]
        .find({"game_id": game_id})
        .sort("turn", 1)
    )

    # Should have 3 move log entries (one per move that moves a piece)
    assert len(move_logs) == 3

    # Verify structure and content of each entry
    for entry in move_logs:
        assert "game_id" in entry
        assert "turn" in entry
        assert "side" in entry
        assert "moved_pieces" in entry
        assert "captured_pieces" in entry
        assert "timestamp" in entry
        assert entry["game_id"] == game_id

    # Sides alternate white/black/white
    assert move_logs[0]["side"] == "white"
    assert move_logs[1]["side"] == "black"
    assert move_logs[2]["side"] == "white"

    # Turn numbers increment
    assert move_logs[0]["turn"] < move_logs[1]["turn"]
    assert move_logs[1]["turn"] < move_logs[2]["turn"]

    # Verify moved_pieces content
    # White pawn a2->a3
    assert len(move_logs[0]["moved_pieces"]) == 1
    assert "pawn" in move_logs[0]["moved_pieces"][0]["piece_type"]
    assert move_logs[0]["moved_pieces"][0]["from"] == [6, 0]
    assert move_logs[0]["moved_pieces"][0]["to"] == [5, 0]

    # Black pawn a7->a6
    assert len(move_logs[1]["moved_pieces"]) == 1
    assert "pawn" in move_logs[1]["moved_pieces"][0]["piece_type"]
    assert move_logs[1]["moved_pieces"][0]["from"] == [1, 0]
    assert move_logs[1]["moved_pieces"][0]["to"] == [2, 0]

    # White pawn b2->b3
    assert len(move_logs[2]["moved_pieces"]) == 1
    assert "pawn" in move_logs[2]["moved_pieces"][0]["piece_type"]
    assert move_logs[2]["moved_pieces"][0]["from"] == [6, 1]
    assert move_logs[2]["moved_pieces"][0]["to"] == [5, 1]


def test_capture_logged_in_captured_pieces(game):
    game_id = game["id"]

    # White pawn d2->d4
    game = select_and_move_white_piece(game, 6, 3, 4, 3)
    # Black pawn e7->e5
    game = select_and_move_black_piece(game, 1, 4, 3, 4)

    # White pawn d4 captures black pawn on e5: select piece first
    game = select_white_piece(game, 4, 3)

    # Manually construct the capture move
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][4] = game_on_next_turn["board_state"][4][3]
    game_on_next_turn["board_state"][4][3] = None
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_state = api.GameStateRequest(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    move_logs = list(
        mongo_client["game_db"]["game_moves"]
        .find({"game_id": game_id})
        .sort("turn", 1)
    )

    # The capture move (last entry) should have the captured piece in captured_pieces
    capture_entry = move_logs[-1]
    assert "black_pawn" in capture_entry["captured_pieces"]["white"]
