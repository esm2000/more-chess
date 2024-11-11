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
import src.utils as utils

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
    black_defeat: bool
    white_defeat: bool
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
        "neutral_attack_log": {},
        "sword_in_the_stone_position": None,
        "capture_point_advantage": None,
        "black_defeat": False,
        "white_defeat": False,
        "gold_count": {"white": 0, "black": 0},
        "last_updated": datetime.datetime.now(),
        "bishop_special_captures": [],
        "latest_movement": {},
        "queen_reset": False,
        "check": {"white": False, "black": False}
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

    # prevent updates to game once game has ended
    if old_game_state["black_defeat"] or old_game_state["white_defeat"]:
        return old_game_state

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
        # ]
        moved_pieces = utils.determine_pieces_that_have_moved(new_game_state["board_state"], old_game_state["board_state"])
    except Exception as e:
        if "More than one" in str(e):
            raise HTTPException(status_code=400, detail=utils.INVALID_GAME_STATE_ERROR_MESSAGE)
        raise e
    
    is_valid_game_state = True
    capture_positions = []

    # if queen extra turn flag is set, check that proper queen moves
    # otherwise invalidate game and log error    
    if new_game_state.get("queen_reset"):
        is_valid_game_state = utils.verify_queen_reset_turn_is_valid(
            old_game_state,
            new_game_state,
            moved_pieces,
            is_valid_game_state
        )
        
    utils.facilitate_adjacent_capture(old_game_state, new_game_state, moved_pieces)
    utils.apply_bishop_energize_stacks_and_bishop_debuffs(old_game_state, new_game_state, moved_pieces)
    utils.apply_queen_stun(old_game_state, new_game_state, moved_pieces)
    
    # if any pieces on the board have gained third bishop debuff, retain last player's turn until they've spared or captured it 
    # mutates capture_positions
    is_valid_game_state, should_increment_turn_count = utils.handle_pieces_with_full_bishop_debuff_stacks(
        old_game_state,
        new_game_state,
        moved_pieces,
        is_valid_game_state,
        capture_positions
    )

    # if no pieces have moved and the position in play has changed, retain the current turn
    if utils.was_a_new_position_in_play_selected(moved_pieces, old_game_state, new_game_state):
        should_increment_turn_count = False
        is_valid_game_state = utils.does_position_in_play_match_turn(old_game_state, new_game_state) and is_valid_game_state
    
    # (unstackable) if a queen captures or "assists" a piece and is not in danger of being captured, retain last player's turn until they move queen again
    # if queen extra turn flag is set and should increment_turn_count is True 
    if new_game_state["queen_reset"] and should_increment_turn_count:
        # unset flag for new game
        new_game_state["queen_reset"] = False
    else:
        # old_game_state
        # new_game_state
        # moved_pieces
        should_increment_turn_count = utils.reset_queen_turn_on_kill_or_assist(
            old_game_state,
            new_game_state,
            moved_pieces,
            should_increment_turn_count
        )

    utils.clean_possible_moves_and_possible_captures(new_game_state)
    if should_increment_turn_count:
        utils.increment_turn_count(old_game_state, new_game_state, moved_pieces, 1)
    utils.prevent_client_side_updates_to_graveyard(old_game_state, new_game_state)

    # returns values for is_valid_state
    # mutates capture_positions array
    is_valid_game_state = utils.check_to_see_if_more_than_one_piece_has_moved(
        old_game_state, 
        new_game_state, 
        moved_pieces, 
        capture_positions,
        is_valid_game_state
    )
    gold_spent = utils.get_gold_spent(old_game_state, moved_pieces)

    is_pawn_exchange_possible = utils.check_is_pawn_exhange_is_possible(old_game_state, new_game_state, moved_pieces)
    move_count_for_white, move_count_for_black = utils.get_move_counts(moved_pieces)

    is_valid_game_state = utils.invalidate_game_if_more_than_one_side_moved(move_count_for_white, move_count_for_black, is_valid_game_state)
    is_valid_game_state = utils.invalidate_game_if_stunned_piece_moves(moved_pieces, is_valid_game_state)
    # old game's turn count is representative of what side should be moving (even is white, odd is black)
    if not disable_turn_check:
        is_valid_game_state = utils.invalidate_game_if_wrong_side_moves(moved_pieces, is_valid_game_state, old_game_state["turn_count"])
    is_valid_game_state = utils.invalidate_game_if_too_much_gold_is_spent(old_game_state, gold_spent, is_valid_game_state)
    # mutates new_game_state object
    utils.cleanse_stunned_pieces(new_game_state)
    
    is_valid_game_state = utils.invalidate_game_if_monster_has_moved(is_valid_game_state, moved_pieces)
    # mutates capture_positions list
    is_valid_game_state = utils.check_for_disappearing_pieces(
        old_game_state,
        new_game_state,
        moved_pieces, 
        is_valid_game_state, 
        capture_positions, 
        is_pawn_exchange_possible
    )
    # mutates new_game_state object
    utils.clean_bishop_special_captures(new_game_state)
    # mutates new_game_state object
    utils.damage_neutral_monsters(new_game_state, moved_pieces)
    is_valid_game_state = utils.invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array(old_game_state, new_game_state, moved_pieces, is_valid_game_state, is_pawn_exchange_possible)

    # if a neutral monster is killed and a piece has not moved to its position, invalidate 
    if utils.get_neutral_monster_slain_position(moved_pieces) and not utils.is_neutral_monster_killed(moved_pieces):
        logger.error("A neutral monster disappeared from board without being captured")
        is_valid_game_state = False
    
    # if any captured piece is a king, invalidate 
    if utils.is_invalid_king_capture(moved_pieces):
        logger.error("A king has been captured or has disappeared from board")
        is_valid_game_state = False

    # utilize get_unsafe_positions_for_kings() to handle granting and removing check
    # if a king has check protection, exhaust one stack and prevent check for that turn
    utils.manage_check_status(old_game_state, new_game_state)

    # check for checkmate by seeing if the king has anywhere to go
    utils.end_game_on_checkmate(old_game_state, new_game_state)

    # if pieces have moved and player was in check last turn and is in check this turn invalidate game
    is_valid_game_state = utils.invalidate_game_if_player_moves_and_is_in_check(is_valid_game_state, new_game_state, moved_pieces)

    if not is_valid_game_state:
        raise HTTPException(status_code=400, detail=utils.INVALID_GAME_STATE_ERROR_MESSAGE)

    # new game's turn count is representative of what side should be moving next turn (even is white, odd is black)
    if should_increment_turn_count and utils.are_all_non_king_pieces_stunned(new_game_state) and not utils.can_king_move(old_game_state, new_game_state):
        utils.increment_turn_count(old_game_state, new_game_state, moved_pieces, 2)
    
    # figure out capture point advantage, update gold count, and reassign pawn buffs
    # all three functions mutate new_game_state
    utils.update_gold_count(old_game_state, new_game_state, gold_spent)
    utils.update_capture_point_advantage(new_game_state)
    utils.reassign_pawn_buffs(new_game_state)

    # have neutral monsters slay adjacent normal pieces
    if len(moved_pieces) > 0:
        utils.carry_out_neutral_monster_attacks(new_game_state)

    # spawn neutral monsters when appropriate
    utils.spawn_neutral_monsters(new_game_state)
    
    # heal neutral monsters after they've haven't been attacked for 3 turns
    utils.heal_neutral_monsters(old_game_state, new_game_state)

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
    utils.record_moved_pieces_this_turn(new_game_state, moved_pieces)
    
    # if queen extra turn flag is set, find correct queen and set its position as the position_in_play
    reset_position_in_play_queen = True
    if new_game_state["queen_reset"]:
        reset_position_in_play_queen = utils.set_queen_as_position_in_play(old_game_state, new_game_state)

    # if the side whose turn it is next has a king in check, set its king as the position in play
    reset_position_in_play_king = utils.set_next_king_as_position_in_play_if_in_check(old_game_state, new_game_state)

    # determine possibleMoves if a position_in_play is not [null, null]
    # and add to new_game_state 
    reset_position_in_play = reset_position_in_play_queen and reset_position_in_play_king
    utils.determine_possible_moves(old_game_state, new_game_state, moved_pieces, player, reset_position_in_play)

    # handle draw conditions (draws are when both players lose)
    utils.handle_draw_conditions(old_game_state, new_game_state)
    
    # spawn sword in the stone when appropriate
    utils.spawn_sword_in_the_stone(new_game_state)

    # exhaust sword in stone when appropriate
    utils.exhaust_sword_in_the_stone(new_game_state, moved_pieces)

    # TODO: In another script, use endless loop to update games with
    #       odd number turns if its been 6 seconds since the last update 
    #       and there are no pawn exchanges in progress;
    #       sleep for a second at end of loop
    #       PROVIDE EXCEPTION FOR TESTS

    # mutates old_game_state and new_game_state objects
    utils.manage_game_state(old_game_state, new_game_state)

    utils.perform_game_state_update(new_game_state, mongo_client, id)
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