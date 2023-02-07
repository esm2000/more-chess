from bson.objectid import ObjectId
import datetime
from fastapi import APIRouter, Response
from pydantic import BaseModel, Extra
from typing import Union

from src.database import mongo_client


router = APIRouter(prefix="/api")


class GameState(BaseModel, extra=Extra.allow):
    turn_count: int
    position_in_play: list
    board_state: list
    possible_moves: list
    possible_captures: list
    captured_pieces: dict
    sword_in_the_stone_position: Union[list, None]
    capture_point_advantage: Union[list, None]
    player_victory: bool
    player_defeat: bool
    gold_count: dict


@router.post("/game", status_code=201)
def create_game():
    game_state = {
        "turn_count": 0,
        "position_in_play": [None, None],
        "board_state": [
            [
                [{"type": "black_rook"}],
                [{"type": "black_knight"}],
                [{"type": "black_bishop", "energize_stacks": 0}],
                [{"type": "black_queen"}],
                [{"type": "black_king"}],
                [{"type": "black_bishop", "energize_stacks": 0}],
                [{"type": "black_knight"}],
                [{"type": "black_rook"}],
            ],
            [[{"type": "black_pawn", "pawn_buff": 0}]] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [[{"type": "white_pawn", "pawn_buff": 0}]] * 8,
            [
                [{"type": "white_rook"}],
                [{"type": "white_knight"}],
                [{"type": "white_bishop", "energize_stacks": 0}],
                [{"type": "white_queen"}],
                [{"type": "white_king"}],
                [{"type": "white_bishop", "energize_stacks": 0}],
                [{"type": "white_knight"}],
                [{"type": "white_rook"}],
            ],
        ],
        "possible_moves": [],
        "possible_captures": [],
        "captured_pieces": {"white": [], "black": []},
        "sword_in_the_stone_position": None,
        "capture_point_advantage": None,
        "player_victory": False,
        "player_defeat": False,
        "gold_count": {"white": 0, "black": 0},
        "last_updated": datetime.datetime.now()
    }
    game_database = mongo_client["game_db"]
    game_database["games"].insert_one(game_state)
    game_state["id"] = str(game_state.pop("_id"))
    return game_state


@router.get("/game/{id}", status_code=200)
def retrieve_game_state(id, response: Response):
    game_database = mongo_client["game_db"]
    game_state = game_database["games"].find_one({"_id": ObjectId(id)})
    if not game_state:
        response.status_code = 404
        return {"message": "Game not found"}
    game_state["id"] = str(game_state.pop("_id"))
    return game_state


@router.put("/game/{id}", status_code=200)
def update_game_state(id, state: GameState, response: Response):
    new_game_state = dict(state)

    # TODO: add method to validate whether the new game state is valid
    #       and return status code 500 if it isn't

    # TODO: In another script, use endless loop to update games with
    #       odd number turns if its been 6 seconds since the last update;
    #       sleep for a second at end of loop

    # TODO: determine possibleMoves if a position_in_play is not [null, null]
    #       and add to new_game_state

    new_game_state["last_updated"] = datetime.datetime.now()
    query = {"_id": ObjectId(id)}
    new_values = {"$set": new_game_state}
    game_database = mongo_client["game_db"]
    game_database["games"].update_one(query, new_values)
    return retrieve_game_state(id, response)


@router.delete("/game/{id}")
def delete_game(id):
    query = {"_id": ObjectId(id)}
    game_database = mongo_client["game_db"]
    game_database["games"].delete_one(query)
    return {"message": "Success"}