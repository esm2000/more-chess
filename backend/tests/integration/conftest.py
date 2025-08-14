import pytest
import time
from fastapi import Response
import src.api as api


@pytest.fixture
def game():
    game = api.create_game()
    yield game
    
    result = api.delete_game(game["id"])
    assert result.get("message") == "Success"
    
    # Poll until game is actually deleted (max 10 seconds)
    max_wait = 10
    poll_interval = 0.1
    elapsed = 0
    
    while elapsed < max_wait:
        response = api.retrieve_game_state(game["id"], Response())
        if "not found" in response.get("message", ""):
            break  # Game successfully deleted
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    # Final assertion to ensure game was deleted
    assert "not found" in api.retrieve_game_state(game["id"], Response()).get("message", "")