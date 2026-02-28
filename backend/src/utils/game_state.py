import copy
import datetime

from bson.objectid import ObjectId
from fastapi import Response

import src.api as api
from mocks.empty_game import empty_game


# used to reset game state during integration testing
def clear_game(game):
    game_on_next_turn = copy.deepcopy(game)
    for key in empty_game:
        game_on_next_turn[key] = copy.deepcopy(empty_game[key])
    
    game_on_next_turn["previous_state"] = copy.deepcopy(game_on_next_turn)

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    return game


def increment_turn_count(old_game_state, new_game_state, moved_pieces, number_of_turns):
    if len(moved_pieces) > 0:
        new_game_state["turn_count"] = old_game_state["turn_count"] + number_of_turns

def reset_turn_count(old_game_state, new_game_state):
    new_game_state["turn_count"] = old_game_state["turn_count"] 


# erase cached previous state in previous game state to manage space efficiency
# save old game state under new game state's previous state
def manage_game_state(old_game_state, new_game_state):
    previous_state_of_old_game = old_game_state.get("previous_state")
    if previous_state_of_old_game:
        old_game_state.pop("previous_state")
    new_game_state["previous_state"] = old_game_state


def perform_game_state_update(new_game_state, mongo_client, game_id):
    new_game_state["last_updated"] = datetime.datetime.now()
    query = {"_id": ObjectId(game_id)}
    new_values = {"$set": new_game_state}
    game_database = mongo_client["game_db"]
    game_database["games"].update_one(query, new_values)


# clean game possible moves and possible captures from last game state
# remove possible moves from last turn if any 
def clean_possible_moves_and_possible_captures(new_game_state):
    new_game_state["possible_moves"] = []
    new_game_state["possible_captures"] = []


# do not allow for updates to graveyard
def prevent_client_side_updates_to_graveyard(old_game_state, new_game_state):
    new_game_state["graveyard"] = old_game_state["graveyard"]


def record_moved_pieces_this_turn(new_game_state, moved_pieces):
    def is_captured_or_spawned(moved_pieces_entry):
        return moved_pieces_entry["previous_position"][0] is None \
        or  moved_pieces_entry["current_position"][0] is None
    filtered_moved_pieces = [entry for entry in moved_pieces if not is_captured_or_spawned(entry)]

    # in theory filtered_moved_pieces should only have one moved piece
    # except when performing castling but this behavior is checked elsewhere
    
    if filtered_moved_pieces:
        new_game_state["latest_movement"] = {
            "turn_count": new_game_state["turn_count"],
            "record": filtered_moved_pieces
        }
    
    # keep the previous record if there are no new moved pieces
    # to faciliate record keeping for granting bishop energize stacks
    # to bishops that perform special captures with their debuff