import pytest
import time
from fastapi import Response
import src.api as api


@pytest.fixture
def game():
    game = api.create_game()
    yield game
    result = api.delete_game(game["id"])
    time.sleep(5)
    assert result.get("message") == "Success"
    assert "not found" in api.retrieve_game_state(game["id"], Response()).get("message")