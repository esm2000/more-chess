from bson.objectid import ObjectId
import datetime
from fastapi import APIRouter, HTTPException, Response
import logging
from pydantic import BaseModel, Extra
from typing import Union

from mocks.starting_game import starting_game
# prevents circular import
import src.moves as moves 
from src.database import mongo_client
from src.logging import logger
from src.utility import (
    INVALID_GAME_STATE_ERROR_MESSAGE,
    are_all_non_king_pieces_stunned,
    apply_bishop_energize_stacks_and_bishop_debuffs,
    apply_queen_stun,
    can_king_move,
    carry_out_neutral_monster_attacks,
    check_for_disappearing_pieces,
    check_is_pawn_exhange_is_possible,
    check_to_see_if_more_than_one_piece_has_moved,
    clean_possible_moves_and_possible_captures,
    clean_bishop_special_captures,
    cleanse_stunned_pieces,
    does_position_in_play_match_turn,
    damage_neutral_monsters,
    determine_pieces_that_have_moved,
    determine_possible_moves,
    get_gold_spent,
    get_move_counts,
    handle_pieces_with_full_bishop_debuff_stacks,
    increment_turn_count,
    invalidate_game_if_monster_has_moved,
    invalidate_game_if_more_than_one_side_moved,
    invalidate_game_if_stunned_piece_moves,
    invalidate_game_if_too_much_gold_is_spent,
    invalidate_game_if_wrong_side_moves,
    invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array,
    is_invalid_king_capture,
    is_neutral_monster_killed,
    facilitate_adjacent_capture,
    get_neutral_monster_slain_position,
    manage_game_state,
    perform_game_state_update,
    prevent_client_side_updates_to_graveyard,
    reassign_pawn_buffs,
    record_moved_pieces_this_turn,
    reset_queen_turn_on_kill_or_assist,
    set_queen_as_position_in_play,
    spawn_neutral_monsters,
    update_capture_point_advantage,
    update_gold_count,
    verify_queen_reset_turn_is_valid,
    was_a_new_position_in_play_selected
)

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
    bishop_special_captures: list
    latest_movement: dict
    queen_reset: bool


@router.post("/game", status_code=201)
def create_game():
    game_state = {
        "turn_count": 0,
        "position_in_play": [None, None],
        "board_state": starting_game["board_state"],
        "possible_moves": [],
        "possible_captures": [],
        "captured_pieces": {"white": [], "black": []},
        "graveyard": [],
        "sword_in_the_stone_position": None,
        "capture_point_advantage": None,
        "player_victory": False,
        "player_defeat": False,
        "gold_count": {"white": 0, "black": 0},
        "last_updated": datetime.datetime.now(),
        "bishop_special_captures": [],
        "latest_movement": {},
        "queen_reset": False
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


@router.delete("/game/{id}")
def delete_game(id):
    query = {"_id": ObjectId(id)}
    game_database = mongo_client["game_db"]
    game_database["games"].delete_one(query)
    return {"message": "Success"}


@router.put("/game/{id}", status_code=200)
def update_game_state(id, state: GameState, response: Response, player=True, disable_turn_check=False):
    new_game_state = dict(state)
    old_game_state = retrieve_game_state(id, response)

    # validate whether the new game state is valid
    # and return status code 500 if it isn't
    try:
        # moved_pieces = [ 
        #   {
        #       "piece": {"type": "piece_type", ...},
        #       "side": "",
        #       "previous_position": [],
        #       "current_position": []
        #   },
        #   ...
        # }
        moved_pieces = determine_pieces_that_have_moved(new_game_state["board_state"], old_game_state["board_state"])
    except Exception as e:
        if "More than one" in str(e):
            raise HTTPException(status_code=400, detail=INVALID_GAME_STATE_ERROR_MESSAGE)
        raise e
    
    is_valid_game_state = True
    capture_positions = []

    # if queen extra turn flag is set, check that proper queen moves
    # otherwise invalidate game and log error    
    if new_game_state.get("queen_reset"):
        is_valid_game_state = verify_queen_reset_turn_is_valid(
            old_game_state,
            new_game_state,
            moved_pieces,
            is_valid_game_state
        )
        
    facilitate_adjacent_capture(old_game_state, new_game_state, moved_pieces)
    apply_bishop_energize_stacks_and_bishop_debuffs(old_game_state, new_game_state, moved_pieces)
    apply_queen_stun(old_game_state, new_game_state, moved_pieces)
    
    # if any pieces on the board have gained third bishop debuff, retain last player's turn until they've spared or captured it 
    # mutates capture_positions
    is_valid_game_state, should_increment_turn_count = handle_pieces_with_full_bishop_debuff_stacks(
        old_game_state,
        new_game_state,
        moved_pieces,
        is_valid_game_state,
        capture_positions
    )

    # if no pieces have moved and the position in play has changed, retain the current turn
    if was_a_new_position_in_play_selected(moved_pieces, old_game_state, new_game_state):
        should_increment_turn_count = False
        is_valid_game_state = does_position_in_play_match_turn(old_game_state, new_game_state) and is_valid_game_state
    
    # (unstackable) if a queen captures or "assists" a piece and is not in danger of being captured, retain last player's turn until they move queen again
    # if queen extra turn flag is set and should increment_turn_count is True 
    if new_game_state["queen_reset"] and should_increment_turn_count:
        # unset flag for new game
        new_game_state["queen_reset"] = False
    else:
        # old_game_state
        # new_game_state
        # moved_pieces
        should_increment_turn_count = reset_queen_turn_on_kill_or_assist(
            old_game_state,
            new_game_state,
            moved_pieces,
            should_increment_turn_count
        )

    clean_possible_moves_and_possible_captures(new_game_state)
    if should_increment_turn_count:
        increment_turn_count(old_game_state, new_game_state, moved_pieces, 1)
    prevent_client_side_updates_to_graveyard(old_game_state, new_game_state)

    # returns values for is_valid_state
    # mutates capture_positions array
    is_valid_game_state = check_to_see_if_more_than_one_piece_has_moved(
        old_game_state, 
        new_game_state, 
        moved_pieces, 
        is_valid_game_state, 
        capture_positions
    )
    gold_spent = get_gold_spent(old_game_state, moved_pieces)

    is_pawn_exchange_possible = check_is_pawn_exhange_is_possible(old_game_state, new_game_state, moved_pieces)
    move_count_for_white, move_count_for_black = get_move_counts(moved_pieces)

    is_valid_game_state = invalidate_game_if_more_than_one_side_moved(move_count_for_white, move_count_for_black, is_valid_game_state)
    is_valid_game_state = invalidate_game_if_stunned_piece_moves(moved_pieces, is_valid_game_state)
    # old game's turn count is representative of what side should be moving (even is white, odd is black)
    if not disable_turn_check:
        is_valid_game_state = invalidate_game_if_wrong_side_moves(moved_pieces, is_valid_game_state, old_game_state["turn_count"])
    is_valid_game_state = invalidate_game_if_too_much_gold_is_spent(old_game_state, gold_spent, is_valid_game_state)
    # mutates new_game_state object
    cleanse_stunned_pieces(new_game_state)
    
    is_valid_game_state = invalidate_game_if_monster_has_moved(is_valid_game_state, moved_pieces)
    # mutates capture_positions list
    is_valid_game_state = check_for_disappearing_pieces(
        old_game_state,
        new_game_state,
        moved_pieces, 
        is_valid_game_state, 
        capture_positions, 
        is_pawn_exchange_possible
    )
    # mutates new_game_state object
    clean_bishop_special_captures(new_game_state)
    # mutates new_game_state object
    damage_neutral_monsters(new_game_state, moved_pieces)
    is_valid_game_state = invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array(old_game_state, new_game_state, moved_pieces, is_valid_game_state, is_pawn_exchange_possible)

    # if a neutral monster is killed and a piece has not moved to its position, invalidate 
    if get_neutral_monster_slain_position(moved_pieces) and not is_neutral_monster_killed(moved_pieces):
        logger.error("A neutral monster disappeared from board without being captured")
        is_valid_game_state = False
    
    # if any captured piece is a king, invalidate 
    if is_invalid_king_capture(moved_pieces):
        logger.error("A king has been captured or has disappeared from board")
        is_valid_game_state = False

    if not is_valid_game_state:
        raise HTTPException(status_code=400, detail=INVALID_GAME_STATE_ERROR_MESSAGE)

    # determine possibleMoves if a position_in_play is not [null, null]
    # and add to new_game_state 
    determine_possible_moves(old_game_state, new_game_state, moved_pieces, player)

    # new game's turn count is representative of what side should be moving next turn (even is white, odd is black)
    if should_increment_turn_count and are_all_non_king_pieces_stunned(new_game_state) and not can_king_move(old_game_state, new_game_state):
        increment_turn_count(old_game_state, new_game_state, moved_pieces, 2)
    
    # figure out capture point advantage, update gold count, and reassign pawn buffs
    # all three functions mutate new_game_state
    update_gold_count(old_game_state, new_game_state, gold_spent)
    update_capture_point_advantage(new_game_state)
    reassign_pawn_buffs(new_game_state)

    # have neutral monsters slay adjacent normal pieces
    if len(moved_pieces) > 0:
        carry_out_neutral_monster_attacks(new_game_state)

    # spawn neutral monsters when appropriate
    spawn_neutral_monsters(new_game_state)
    
    # updates gamestate object with any moved pieces and some information 
        # only moved_pieces with a non-null starting and ending positions in a single dictionary 
        # records previous position, current position, piece type, and current turn count
        # allows for proper application of bishop energize stacks after capturing pieces with full bishop debuff stacks

        # latest_movement key in new game state is in format of:
            # {
            #   "turn_count": 40,
            #   "record": moved_pieces # (filtered)
            # }
    # mutates new_game_state
    record_moved_pieces_this_turn(new_game_state, moved_pieces)
    
    # if queen extra turn flag is set, find correct queen and set its position as the position_in_play
    if new_game_state["queen_reset"]:
        set_queen_as_position_in_play(old_game_state, new_game_state)

    # TODO: In another script, use endless loop to update games with
    #       odd number turns if its been 6 seconds since the last update 
    #       and there are no pawn exchanges in progress;
    #       sleep for a second at end of loop
    #       PROVIDE EXCEPTION FOR TESTS

    # mutates old_game_state and new_game_state objects
    manage_game_state(old_game_state, new_game_state)

    perform_game_state_update(new_game_state, mongo_client, id)
    return retrieve_game_state(id, response)


# meant for testing purposes, not to be exposed via API endpoint
def update_game_state_no_restrictions(id, state: GameState, response: Response):
    new_game_state = dict(state)
    new_game_state["last_updated"] = datetime.datetime.now()
    query = {"_id": ObjectId(id)}
    new_values = {"$set": new_game_state}
    game_database = mongo_client["game_db"]
    game_database["games"].update_one(query, new_values)
    return retrieve_game_state(id, response)