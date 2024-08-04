from bson.objectid import ObjectId
import datetime
from fastapi import APIRouter, HTTPException, Response
import logging
from pydantic import BaseModel, Extra
from typing import Union

from mocks.starting_game import starting_game
import src.moves as moves
from src.database import mongo_client
from src.logging import logger
from src.utility import (
    INVALID_GAME_STATE_ERROR_MESSAGE,
    increment_turn_count,
    apply_bishop_energize_stacks_and_bishop_debuffs,
    apply_queen_stun,
    carry_out_neutral_monster_attacks,
    check_for_disappearing_pieces,
    check_is_pawn_exhange_is_possible,
    check_to_see_if_more_than_one_piece_has_moved,
    clean_possible_moves_and_possible_captures,
    cleanse_stunned_pieces,
    damage_neutral_monsters,
    determine_pieces_that_have_moved,
    determine_possible_moves,
    get_gold_spent,
    get_move_counts,
    invalidate_game_if_monster_has_moved,
    invalidate_game_if_more_than_one_side_moved,
    invalidate_game_if_stunned_piece_moves,
    invalidate_game_if_too_much_gold_is_spent,
    invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array,
    is_invalid_king_capture,
    is_neutral_monster_killed,
    facilitate_adjacent_capture,
    get_neutral_monster_slain_position,
    manage_game_state,
    perform_game_state_update,
    prevent_client_side_updates_to_graveyard,
    reassign_pawn_buffs,
    spawn_neutral_monsters,
    update_capture_point_advantage,
    update_gold_count
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


@router.delete("/game/{id}")
def delete_game(id):
    query = {"_id": ObjectId(id)}
    game_database = mongo_client["game_db"]
    game_database["games"].delete_one(query)
    return {"message": "Success"}


@router.put("/game/{id}", status_code=200)
def update_game_state(id, state: GameState, response: Response, player = True):
    new_game_state = dict(state)
    old_game_state = retrieve_game_state(id, response)

    # TODO: skip a player's turn if all his piece's are stunned (use turn count parity to decide who's turn it is)

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

    facilitate_adjacent_capture(old_game_state, new_game_state, moved_pieces)
    apply_bishop_energize_stacks_and_bishop_debuffs(old_game_state, new_game_state, moved_pieces)
    apply_queen_stun(old_game_state, new_game_state, moved_pieces)
    is_valid_game_state = True
    capture_positions = []

    should_increment_turn_count = True
    pieces_with_three_bishop_stacks_this_turn = get_pieces_with_three_bishop_stacks_from_state(new_game_state)
    pieces_with_three_bishop_stacks_last_turn = get_pieces_with_three_bishop_stacks_from_state(old_game_state)
    # [
    #   {
    #       "piece": <piece dictionary>,
    #       "position": [i, j]
    #   }
    # ]

    def get_pieces_with_three_bishop_stacks_from_state(game_state):
        output = []
        # [
        #   {
        #       "piece": <piece dictionary>,
        #       "position": [i, j]
        #   }
        # ]
        for i, row in enumerate(game_state["board_state"]):
            for j, square in enumerate(row):
                if square:
                    for piece in square:
                        if piece.get("bishop_debuff", 0) == 3:
                            output.append({
                                "piece": piece.copy(), "position": [i, j]
                            })
        return output
    
    
    def did_piece_get_full_bishop_debuffs_this_turn(old_game_state, new_piece_info):
        row = new_piece_info["position"][0]
        col = new_piece_info["position"][1]
        square = old_game_state["board_state"][row][col]
        if not square:
            return False
        for piece in square:
            if piece["type"] == new_piece_info["piece"]["type"] and \
            new_piece_info["piece"].get("bishop_debuff") >= 2:
                return True
        return False
    
    def did_piece_get_spared_this_turn_from_special_bishop_capture(new_game_state, old_piece_info):
        row = old_piece_info["position"][0]
        col = old_piece_info["position"][1]
        square = new_game_state["board_state"][row][col]
        if not square:
            return False
        
        for piece in square:
            if piece["type"] == old_piece_info["piece"]["type"] and piece.get("bishop_debuff", 0) == 0:
                return True
        return False

        # TODO: if any pieces on the board have gained third bishop debuff, retain last player's turn until they've spared or captured it
        # scenario 1 - (can be any) pieces on the board have third bishop debuff and did not have all three last turn 
        #            - or they had all three last turn but another piece with a third bishop debuff was dealt with instead
        #            - turn count is not being incremented
    if any([did_piece_get_full_bishop_debuffs_this_turn(old_game_state, piece_info) for piece_info in pieces_with_three_bishop_stacks_this_turn]):
        should_increment_turn_count = False
        # scenario 2 - illegal move is attempted instead of dealing with bishop debuffs
        #            - search through moved pieces and invalidate game state if any pieces moved (valid old position and new position) if there's any third bishop buff active in old_game_state
    elif pieces_with_three_bishop_stacks_last_turn and \
    len([moved_piece for moved_piece in moved_pieces if moved_piece["previous_position"][0] is not None and moved_piece["current_position"][1] is not None]) > 0:
        logger.error("Illegal move was attempted instead of dealing with full bishop debuff stacks")
        is_valid_game_state = False
        # scenario 3 - a piece that had third bishop debuff in the previous game state has no debuffs present in the current game state
        #            - player spared piece
        #            - turn count is being incremented
        #            - (technically allow sparing of multiple pieces since this isn't game breaking behavior)
    elif all([did_piece_get_spared_this_turn_from_special_bishop_capture(new_game_state, piece_info) for piece_info in pieces_with_three_bishop_stacks_last_turn]):
        should_increment_turn_count = True
        # scenario 4 - there is a piece in the moved_pieces array that shows that a piece was captured (via bishop debuffs)
        #            - player captured piece and game has to ensure that state is not invalidated later on 
        #              by appending captured piece's position to capture_positions
        #            - turn count is being incremented
        # scenario 5 - catch all - more than one side has 3 bishop debuffs 
        #            - invalidate game
        # add unit tests for these five scenarios
    # TODO: if a queen captures or "assists" a piece and is not in danger of being captured, retain last player's turn until they move queen again

    clean_possible_moves_and_possible_captures(new_game_state)
    if should_increment_turn_count:
        increment_turn_count(old_game_state, new_game_state, moved_pieces)
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
    is_valid_game_state = invalidate_game_if_too_much_gold_is_spent(old_game_state, gold_spent, is_valid_game_state)
    # mutates new_game_state object
    cleanse_stunned_pieces(new_game_state, move_count_for_white)
    
    # TODO: before capture_positions is altered in this for loop,
    # ensure that if a piece moved to a specific positions, all pieces that are supposed to be eliminated from that move are eliminated
    # since its possible to capture more than one piece a turn
    # (add the captured pieces to moved_pieces array, so that the captured_pieces object can be properly updated (lines 295-296))
    
    is_valid_game_state = invalidate_game_if_monster_has_moved(is_valid_game_state, moved_pieces)
    # mutates capture_positions list
    is_valid_game_state = check_for_disappearing_pieces(
        old_game_state, 
        moved_pieces, 
        is_valid_game_state, 
        capture_positions, 
        is_pawn_exchange_possible
    )
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


    # TODO: In another script, use endless loop to update games with
    #       odd number turns if its been 6 seconds since the last update 
    #       and there are no pawn exchanges in progress;
    #       sleep for a second at end of loop

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