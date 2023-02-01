from fastapi import Response
import pytest
import src.api as api


@pytest.fixture
def game():
    game = api.create_game()
    yield game
    result = api.delete_game(game["id"])
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
        "sword_in_the_stone_position",
        "capture_point_advantage",
        "player_victory",
        "player_defeat",
        "gold_count",
    ]:
        assert key in game
    assert game["turn_count"] == 0
    assert game["position_in_play"] == [None, None]
    pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "king", "rook"]
    pieces += ["pawn"] * 8
    for i, black_piece in enumerate(game["board_state"][0] + game["board_state"][1]):
        assert "black" in black_piece[0]["type"]
        assert pieces[i] in black_piece[0]["type"]
    for row in [2, 3, 4, 5]:
        for col in range(8):
            assert game["board_state"][row][col] is None
    for i, white_piece in enumerate(game["board_state"][7] + game["board_state"][6]):
        assert "white" in white_piece[0]["type"]
        assert pieces[i] in white_piece[0]["type"]
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0
    assert len(game["captured_pieces"]["white"]) == 0
    assert len(game["captured_pieces"]["black"]) == 0
    assert (
        not game["sword_in_the_stone_position"]
        and not game["capture_point_advantage"]
        and not game["player_victory"]
        and not game["player_defeat"]
        and not game["gold_count"]["white"]
        and not game["gold_count"]["black"]
    )


def test_alter_game(game):
    game_on_next_turn = game.copy()
    game_on_next_turn["board_state"][5][0] = game_on_next_turn["board_state"][6][0]
    game_on_next_turn["board_state"][6][0] = None
    game_on_next_turn["turn_count"] += 1

    game_on_next_turn.pop("id")
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["board_state"][5][0][0]["type"] == "white_pawn"
    assert game["board_state"][6][0] is None
    assert game["turn_count"] == 1
