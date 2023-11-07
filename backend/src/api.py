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
    MONSTER_INFO,
    carry_out_neutral_monster_attacks,
    determine_pieces_that_have_moved,
    get_piece_value,
    is_neutral_monster_spawned,
    spawn_neutral_monsters,
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


@router.put("/game/{id}", status_code=200)
def update_game_state(id, state: GameState, response: Response, player = True):
    new_game_state = dict(state)
    old_game_state = retrieve_game_state(id, response)

    # validate whether the new game state is valid
    # and return status code 500 if it isn't
    try:
        moved_pieces = determine_pieces_that_have_moved(new_game_state["board_state"], old_game_state["board_state"])
    except Exception as e:
        if "More than one" in str(e):
            raise HTTPException(status_code=400, detail=INVALID_GAME_STATE_ERROR_MESSAGE)
        raise e
            
    # moved_pieces = [ 
    #   {
    #       "piece": "",
    #       "side": "",
    #       "previous_position": [],
    #       "current_position": []
    #   },
    #   ...
    # }

    # TODO: iterate through moved pieces to check to see if a bishop has moved from its previous position and hasn't been bought 
    # and add energize stacks based on its movement (5 energize stacks for each square moved, 10 energize stacks for each piece captured)

    # TODO: iterate through moved pieces to check to see if bishop is threatening to capture a piece and apply debuff

    # TODO: if any pieces on the board have gained third bishop debuff, retain last player's turn until they've spared or captured it
    is_valid_game_state = True
    move_count_for_white = 0 
    move_count_for_black = 0
    neutral_monster_slain_position = None
    has_a_king_been_captured = False
    has_non_neutral_piece_moved = False
    capture_positions = []
    gold_spent = new_game_state["captured_pieces"].copy()
    for side in gold_spent:
        gold_spent[side] = 0
    # gold_spent = {
    #   "white": 0,
    #   "black": 0
    # }
    is_pawn_exchange = old_game_state["captured_pieces"].copy()

    # remove possible moves from last turn if any 
    new_game_state["possible_moves"] = []
    new_game_state["possible_captures"] = []

    # append to turn count
    if len(moved_pieces) > 0:
        new_game_state["turn_count"] = old_game_state["turn_count"] + 1

    # do not allow for updates to graveyard
    new_game_state["graveyard"] = old_game_state["graveyard"]

    # if more than one pieces for one side has moved and its not a castle, invalidate
    for side in old_game_state["captured_pieces"]:
        count_of_pieces_on_new_state = 0
        has_king_moved = False
        has_rook_moved = False
        is_pawn_exchange[side] = False
        
        for moved_piece in moved_pieces:
            if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is None and moved_piece["previous_position"][0] is not None:
                neutral_monster_slain_position = moved_piece["previous_position"]
            if side != moved_piece["side"]:
                continue

            has_non_neutral_piece_moved = True

            if moved_piece["current_position"][0] is None and "king" in moved_piece["piece"]["type"]:
                has_a_king_been_captured = True
            
            if moved_piece["current_position"][0] is not None:
                count_of_pieces_on_new_state += 1
            if moved_piece["current_position"][0] is None and "pawn" in moved_piece["piece"]["type"]:
                previous_position = moved_piece['previous_position']
                # opposite_side = "white" if side == "black" else "black"
                square_on_current_game_state = new_game_state["board_state"][previous_position[0]][previous_position[1]]
                if square_on_current_game_state and all(side == piece["type"].split("_")[0] for piece in square_on_current_game_state):
                    is_pawn_exchange[side] = True
                    new_game_state["turn_count"] = old_game_state["turn_count"]
            if moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
                if side == "white":
                    move_count_for_white += 1
                else:
                    move_count_for_black += 1

                moves_info = {"possible_moves": [], "possible_captures": []}
                try:
                    # TODO: incorporate other piece types here
                    if "pawn" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_pawn(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    if "knight" in moved_piece["piece"]["type"]:
                        moves_info = moves.get_moves_for_knight(
                            curr_game_state=old_game_state, 
                            prev_game_state=old_game_state.get("previous_state"), 
                            curr_position=moved_piece["previous_position"]
                        )
                    for possible_capture_info in moves_info["possible_captures"]:
                        capture_positions.append(possible_capture_info)
                        
                except Exception as e:
                    logger.error(f"Unable to determine move for {moved_piece['piece']} due to: {e}")
                    is_valid_game_state = False
        # if move(s) are invalid, invalidate
                if moved_piece["current_position"] not in moves_info["possible_moves"]:
                    logger.error(f"Square {moved_piece['previous_position']} to square {moved_piece['current_position']} invalid for {moved_piece['piece']}")
                    is_valid_game_state = False

        # if a piece has spawned without being exchanged for a pawn
        # take note of gold count that is supposed to be spent to obtain it
            if moved_piece["current_position"][0] is not None \
            and moved_piece["previous_position"][0] is None \
            and not any(p['previous_position'] == moved_piece["current_position"] for p in moved_pieces if p["previous_position"][0] is not None):          
                if "queen" in moved_piece["piece"]["type"] or "king" in moved_piece["piece"]["type"]:
                    logger.error(f"A {'queen' if 'queen' in moved_piece['piece']['type'] else 'king'} has been bought")
                    is_valid_game_state = False
                
                gold_spent[side] += get_piece_value(moved_piece["piece"]["type"])

                if gold_spent[side] > old_game_state["gold_count"][side]:
                    logger.error(f"More gold has been spent for {side} than {side} currently has ({gold_spent[side]} gold vs. {old_game_state['gold_count'][side]} gold)")
                    is_valid_game_state = False
        if count_of_pieces_on_new_state > 1:
            for moved_piece in moved_pieces:
                if "king" in moved_piece.get("piece"):
                    has_king_moved = True
                if "rook" in moved_piece.get("piece"):
                    has_rook_moved = True

            if not (has_king_moved and has_rook_moved):
                logger.error("A castle was not detected and more than one piece has moved")
                is_valid_game_state = False

        # if more than one side has pieces that's moved, invalidate 
    if move_count_for_white > 0 and move_count_for_black > 0: 
        logger.error("More than one side have pieces that have moved")
        is_valid_game_state = False

    was_neutral_monster_killed = False
    for moved_piece in moved_pieces:
        # if a neutral monster moves invalidate
        if moved_piece["side"] == "neutral" and moved_piece["current_position"][0] is not None and moved_piece["previous_position"][0] is not None:
            logger.error("A neutral monster has moved")
            is_valid_game_state = False

        if neutral_monster_slain_position:
            if moved_piece["side"] != "neutral" and \
            abs(moved_piece["current_position"][0] - neutral_monster_slain_position[0]) in [0, 1] and \
            abs(moved_piece["current_position"][1] - neutral_monster_slain_position[1]) in [0, 1]:
                was_neutral_monster_killed = True

        # if any piece captured this turn doesn't have a captor, invalidate (keep in mind that adjacent 
        # capturing is possible so positions in moved_pieces shouldn't be relied on as crutch)
        if moved_piece["side"] != "neutral" and moved_piece["current_position"][0] is None:
            captured_piece_accounted_for = False
            for capture_position in capture_positions:
                if capture_position[1] == moved_piece["previous_position"]:
                    captured_piece_accounted_for = True
                    capture_positions.remove(capture_position)
        # if a piece was captured by another piece moving to adjacent square 
        # we need to update captured_pieces with it 
                if capture_position[0] != capture_position[1]:
                    new_game_state["captured_pieces"][side].append(moved_piece["piece"]["type"])
            
            if not captured_piece_accounted_for:
                # check to see if captured piece was next to a neutral monster 
                for monster in MONSTER_INFO:
                    potential_monster_position = old_game_state["board_state"][MONSTER_INFO[monster]["position"][0]][MONSTER_INFO[monster]["position"][1]]
                    if abs(moved_piece["previous_position"][0] - MONSTER_INFO[monster]["position"][0]) in [0, 1] and \
                    abs(moved_piece["previous_position"][1] - MONSTER_INFO[monster]["position"][1]) in [0, 1] and \
                    any(piece["type"] == monster for piece in potential_monster_position):
                    # check to see if neutral monster is also present in previous game
                        turn_count_for_previous_game = old_game_state["turn_count"]
                        turn_count_when_monster_spawned = list(filter(lambda piece: piece["type"] == monster, potential_monster_position))[0]["turn_spawned"]
                        if turn_count_for_previous_game > turn_count_when_monster_spawned:
                            captured_piece_accounted_for = True

                # check to see if a pawn exchange has occurred
                if "pawn" in moved_piece["piece"]["type"] and is_pawn_exchange[moved_piece["side"]]:
                    captured_piece_accounted_for = True
                      
            if not captured_piece_accounted_for:
                logger.error(f"Piece {moved_piece['piece']} on {moved_piece['previous_position']} has disappeared from board without being captured")
                is_valid_game_state = False
        # if a piece is on the same square or adjacent to neutral monsters, they should damage or kill them
        if moved_piece["previous_position"][0] is not None and moved_piece["current_position"][0] is not None:
            for neutral_monster in MONSTER_INFO:
                if is_neutral_monster_spawned(neutral_monster,new_game_state["board_state"]):
                    row_diff = abs(moved_piece["current_position"][0] - MONSTER_INFO[neutral_monster]["position"][0])
                    col_diff = abs(moved_piece["current_position"][1] - MONSTER_INFO[neutral_monster]["position"][1])
                    if row_diff in [-1, 0, 1] and col_diff in [-1, 0, 1]:
                        for i, piece in enumerate(new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]]):
                            if piece.get("type") == neutral_monster:
                                new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]][i]["health"] = piece["health"] - 1
                    
                                if new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]][i]["health"] < 1:
                                    new_game_state["board_state"][MONSTER_INFO[neutral_monster]["position"][0]][MONSTER_INFO[neutral_monster]["position"][1]].pop(i)
                                    new_game_state["captured_pieces"][moved_piece["side"]].append(neutral_monster)

        # if any new pieces in the captured pieces array have not been captured this turn, invalidate
        # (it's imperative that this code section is placed after we've updated captured_pieces)
    captured_pieces_array = new_game_state["captured_pieces"]["white"].copy() + new_game_state["captured_pieces"]["black"].copy() + new_game_state["graveyard"]
    for captured_piece in old_game_state["captured_pieces"]["white"] + old_game_state["captured_pieces"]["black"] + old_game_state["graveyard"]:
        captured_pieces_array.remove(captured_piece)

    for moved_piece in moved_pieces:
        if moved_piece["current_position"][0] is None:
            try:
                captured_pieces_array.remove(moved_piece["piece"]['type'])
            except ValueError as e:
                if not ("pawn" in moved_piece["piece"]["type"] and is_pawn_exchange[moved_piece["side"]]):
                    logger.error(f"Captured piece {moved_piece['piece']['type']} has not been recorded as a captured piece")
                    is_valid_game_state = False
    
    if len(captured_pieces_array) > 0:
        logger.error(f"There are extra captured pieces not accounted for: {captured_pieces_array}")
        is_valid_game_state = False

        # if a neutral monster is killed and a piece has not moved to its position, invalidate 
    if neutral_monster_slain_position and not was_neutral_monster_killed:
        logger.error("A neutral monster disappeared from board without being captured")
        is_valid_game_state = False

        # if any captured piece is a king, invalidate 
    if has_a_king_been_captured:
        logger.error("A king has been captured or has disappeared from board")
        is_valid_game_state = False

    if not is_valid_game_state:
        raise HTTPException(status_code=400, detail=INVALID_GAME_STATE_ERROR_MESSAGE)

    # determine possibleMoves if a position_in_play is not [null, null]
    # and add to new_game_state; 
    if len(moved_pieces) > 0: 
        new_game_state["position_in_play"] = [None, None]
    if new_game_state["position_in_play"][0] is not None: 
        square = new_game_state["board_state"][new_game_state["position_in_play"][0]][new_game_state["position_in_play"][1]]
        piece_in_play = None
        for piece in square:
            if (player and "white" in piece.get('type')) or (not player and "black" in piece.get('type')):
                piece_in_play = piece

        if not piece_in_play:
            error_msg = f"Invalid position_in_play in potential new game state, no piece present ({new_game_state['position_in_play']})"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        if has_non_neutral_piece_moved:
            error_msg = f"Piece in play but pieces have been moved"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        try:
            # TODO: incorporate other piece types here
            if "pawn" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_pawn(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
            if "knight" in piece_in_play["type"]:
                moves_info = moves.get_moves_for_knight(
                    curr_game_state=old_game_state, 
                    prev_game_state=old_game_state.get("previous_state"), 
                    curr_position=new_game_state["position_in_play"]
                )
        except Exception as e:
            logger.error(f"Unable to determine move for {moved_piece['piece']} due to: {e}")
        
        new_game_state["possible_moves"] = moves_info["possible_moves"]
        new_game_state["possible_captures"] = moves_info["possible_captures"]
    
    # figure out capture point advantage, update gold count, and reassign pawn buffs
    piece_values = new_game_state["captured_pieces"].copy()
    for side in piece_values:
        piece_values[side] = 0
    # {
    #   "white": 0,
    #   "black": 0
    # }
    for side in new_game_state["captured_pieces"]:
        for piece in new_game_state["captured_pieces"][side]:
            piece_values[side] += get_piece_value(piece)

        for piece in list(set(new_game_state["captured_pieces"]) - set(old_game_state["captured_pieces"])):
            new_game_state["gold_count"][side] += get_piece_value(piece) * 2

        new_game_state["gold_count"][side] -= gold_spent[side]

    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]
    pawn_buff = capture_point_advantage if capture_point_advantage < 4 else 3 # capped at 3

    if capture_point_advantage == 0: 
        new_game_state["capture_point_advantage"] = None
    else:
        new_game_state["capture_point_advantage"] = [winning_side, capture_point_advantage]


    for row in range(8):
        for col in range(8):
            square = new_game_state["board_state"][row][col]
            if square:
                for i, piece in enumerate(square):
                    if "pawn" in piece.get("type"):
                        if piece.get("side") == winning_side:
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = pawn_buff
                        elif piece.get("side") == losing_side:
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = 0

    # have neutral monsters slay adjacent normal pieces
    if len(moved_pieces) > 0:
        carry_out_neutral_monster_attacks(new_game_state)

    # spawn neutral monsters when appropriate
    spawn_neutral_monsters(new_game_state)


    # TODO: In another script, use endless loop to update games with
    #       odd number turns if its been 6 seconds since the last update 
    #       and there are no pawn exchanges in progress;
    #       sleep for a second at end of loop

    # erase cached previous state in previous game state to manage space efficiency
    previous_state_of_old_game = old_game_state.get("previous_state")
    if previous_state_of_old_game:
        old_game_state.pop("previous_state")
    new_game_state["previous_state"] = old_game_state

    new_game_state["last_updated"] = datetime.datetime.now()
    query = {"_id": ObjectId(id)}
    new_values = {"$set": new_game_state}
    game_database = mongo_client["game_db"]
    game_database["games"].update_one(query, new_values)
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


@router.delete("/game/{id}")
def delete_game(id):
    query = {"_id": ObjectId(id)}
    game_database = mongo_client["game_db"]
    game_database["games"].delete_one(query)
    return {"message": "Success"}