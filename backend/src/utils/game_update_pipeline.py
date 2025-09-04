from fastapi import HTTPException, Response
from src.log import logger
import src.utils as utils


def prepare_game_update(id, state, retrieve_game_state_func):
    new_game_state = dict(state)
    old_game_state = retrieve_game_state_func(id, Response())
    
    # prevent updates to game once game has ended
    if old_game_state["black_defeat"] or old_game_state["white_defeat"]:
        return old_game_state, None, None
    
    # determine moved pieces
    try:
        moved_pieces = utils.determine_pieces_that_have_moved(
            new_game_state["board_state"], old_game_state["board_state"]
        )
    except Exception as e:
        logger.error(f"Unable to determine pieces that have moved: {e}")
        raise HTTPException(status_code=400, detail=utils.INVALID_GAME_STATE_ERROR_MESSAGE)
    
    return old_game_state, new_game_state, moved_pieces


def apply_special_piece_effects(old_game_state, new_game_state, moved_pieces):
    is_valid_game_state = True
    
    # Queen reset validation
    if new_game_state.get("queen_reset"):
        is_valid_game_state = utils.verify_queen_reset_turn_is_valid(
            old_game_state, new_game_state, moved_pieces, is_valid_game_state
        )
    
    # Apply piece effects
    utils.facilitate_adjacent_capture(old_game_state, new_game_state, moved_pieces)
    utils.apply_bishop_energize_stacks_and_bishop_debuffs(old_game_state, new_game_state, moved_pieces)
    utils.apply_queen_stun(old_game_state, new_game_state, moved_pieces)
    
    return is_valid_game_state


def manage_turn_progression(old_game_state, new_game_state, moved_pieces, is_valid_game_state, capture_positions):
    should_increment_turn_count = True
    
    # Bishop debuff stack handling
    is_valid_game_state, should_increment_turn_count = utils.handle_pieces_with_full_bishop_debuff_stacks(
        old_game_state, new_game_state, moved_pieces, is_valid_game_state, capture_positions
    )
    
    # Position in play selection logic
    if utils.was_a_new_position_in_play_selected(moved_pieces, old_game_state, new_game_state) and new_game_state["position_in_play"][0] is not None and new_game_state["position_in_play"][1] is not None:
        should_increment_turn_count = False
        is_valid_game_state = utils.does_position_in_play_match_turn(old_game_state, new_game_state) and is_valid_game_state
    
    # Queen turn logic
    if new_game_state["queen_reset"] and should_increment_turn_count:
        new_game_state["queen_reset"] = False
    else:
        should_increment_turn_count = utils.reset_queen_turn_on_kill_or_assist(
            old_game_state, new_game_state, moved_pieces, should_increment_turn_count
        )
    
    # Clean and increment
    utils.clean_possible_moves_and_possible_captures(new_game_state)
    if should_increment_turn_count:
        utils.increment_turn_count(old_game_state, new_game_state, moved_pieces, 1)
    utils.prevent_client_side_updates_to_graveyard(old_game_state, new_game_state)
    
    return is_valid_game_state, should_increment_turn_count


def validate_moves_and_pieces(old_game_state, new_game_state, moved_pieces, capture_positions, is_valid_game_state):
    # Core move validation
    is_valid_game_state = utils.check_to_see_if_more_than_one_piece_has_moved(
        old_game_state, new_game_state, moved_pieces, capture_positions, is_valid_game_state
    )
    
    # Update castle log and validate gold
    utils.update_castle_log(new_game_state, moved_pieces)
    gold_spent = utils.get_gold_spent(moved_pieces)
    
    # Move count validation
    move_count_for_white, move_count_for_black = utils.get_move_counts(moved_pieces)
    is_valid_game_state = utils.invalidate_game_if_more_than_one_side_moved(
        move_count_for_white, move_count_for_black, is_valid_game_state
    )
    
    # Other validations
    is_valid_game_state = utils.invalidate_game_if_stunned_piece_moves(moved_pieces, is_valid_game_state)
    is_valid_game_state = utils.invalidate_game_if_wrong_side_moves(
        moved_pieces, is_valid_game_state, old_game_state["turn_count"]
    )
    is_valid_game_state = utils.invalidate_game_if_too_much_gold_is_spent(
        old_game_state, gold_spent, is_valid_game_state
    )
    is_valid_game_state = utils.invalidate_game_if_monster_has_moved(is_valid_game_state, moved_pieces)
    
    utils.cleanse_stunned_pieces(new_game_state)
    
    return is_valid_game_state, gold_spent


def handle_pawn_exchanges(old_game_state, new_game_state, moved_pieces, is_valid_game_state):
    is_pawn_exchange_required_this_turn, is_valid_game_state = utils.check_if_pawn_exchange_is_required(
        old_game_state, new_game_state, moved_pieces, is_valid_game_state
    )
    is_pawn_exchange_possibly_being_carried_out = utils.check_if_pawn_exhange_is_possibly_being_carried_out(
        old_game_state, new_game_state, moved_pieces
    )
    
    should_increment_turn_count_for_pawn_exchange = utils.should_turn_count_be_incremented_for_pawn_exchange(
        old_game_state, is_pawn_exchange_possibly_being_carried_out
    )
    
    if should_increment_turn_count_for_pawn_exchange:
        utils.increment_turn_count(old_game_state, new_game_state, moved_pieces, 1)
    
    if not should_increment_turn_count_for_pawn_exchange and is_pawn_exchange_required_this_turn:
        utils.reset_turn_count(old_game_state, new_game_state)
    
    return is_pawn_exchange_required_this_turn, is_pawn_exchange_possibly_being_carried_out


def handle_captures_and_combat(old_game_state, new_game_state, moved_pieces, is_valid_game_state, 
                               capture_positions, is_pawn_exchange_possibly_being_carried_out):
    # Check for disappearing pieces
    is_valid_game_state = utils.check_for_disappearing_pieces(
        old_game_state, new_game_state, moved_pieces, is_valid_game_state, 
        capture_positions, is_pawn_exchange_possibly_being_carried_out
    )
    
    # Clean bishop special captures and damage monsters
    utils.clean_bishop_special_captures(new_game_state)
    utils.damage_neutral_monsters(new_game_state, moved_pieces, capture_positions)
    
    # Validate captures
    is_valid_game_state = utils.invalidate_game_when_unexplained_pieces_are_in_captured_pieces_array(
        old_game_state, new_game_state, moved_pieces, is_valid_game_state, is_pawn_exchange_possibly_being_carried_out
    )
    
    # Neutral monster validation
    if utils.get_neutral_monster_slain_positions(moved_pieces) and not utils.is_neutral_monster_killed(moved_pieces):
        logger.error("A neutral monster disappeared from board without being captured")
        is_valid_game_state = False
    
    # Conditionally grants neutral monster buffs
    is_valid_game_state = utils.handle_neutral_monster_buffs(moved_pieces, capture_positions, new_game_state, is_valid_game_state)

    # King capture validation
    if utils.is_invalid_king_capture(moved_pieces):
        logger.error("A king has been captured or has disappeared from board")
        is_valid_game_state = False
    
    return is_valid_game_state


def update_game_metrics(old_game_state, new_game_state, moved_pieces, gold_spent):
    utils.update_gold_count(old_game_state, new_game_state, gold_spent)
    utils.update_capture_point_advantage(new_game_state)
    utils.reassign_pawn_buffs(new_game_state)
    
    # Neutral monster attacks
    if len(moved_pieces) > 0:
        utils.carry_out_neutral_monster_attacks(new_game_state)
    
    utils.spawn_neutral_monsters(new_game_state)


def handle_endgame_conditions(old_game_state, new_game_state, moved_pieces, is_valid_game_state, should_increment_turn_count):
    # Check and checkmate logic
    utils.manage_check_status(old_game_state, new_game_state)
    utils.end_game_on_checkmate(old_game_state, new_game_state)
    
    # Validate check escape
    is_valid_game_state = utils.invalidate_game_if_player_moves_and_is_in_check(
        is_valid_game_state, old_game_state, new_game_state, moved_pieces
    )
    
    if not is_valid_game_state:
        raise HTTPException(status_code=400, detail=utils.INVALID_GAME_STATE_ERROR_MESSAGE)
    
    # Handle stunned piece special case
    if should_increment_turn_count and utils.are_all_non_king_pieces_stunned(new_game_state) and not utils.can_king_move(old_game_state, new_game_state):
        utils.increment_turn_count(old_game_state, new_game_state, moved_pieces, 2)
    
    # Heal monsters
    utils.heal_neutral_monsters(old_game_state, new_game_state)
    
    return is_valid_game_state


def finalize_game_state(old_game_state, new_game_state, moved_pieces, player, is_pawn_exchange_required_this_turn, mongo_client, id):
    # Record movement
    utils.record_moved_pieces_this_turn(new_game_state, moved_pieces)
    
    # Position in play logic
    reset_position_in_play_queen = True
    if new_game_state["queen_reset"]:
        reset_position_in_play_queen = utils.set_queen_as_position_in_play(old_game_state, new_game_state)
    
    reset_position_in_play_king = utils.set_next_king_as_position_in_play_if_in_check(old_game_state, new_game_state)
    
    # Determine possible moves
    reset_position_in_play = reset_position_in_play_queen and reset_position_in_play_king
    utils.determine_possible_moves(old_game_state, new_game_state, moved_pieces, player, reset_position_in_play, is_pawn_exchange_required_this_turn)
    
    # Handle draws and special items
    utils.handle_draw_conditions(old_game_state, new_game_state)
    utils.spawn_sword_in_the_stone(old_game_state, new_game_state)
    utils.exhaust_sword_in_the_stone(new_game_state, moved_pieces)
    
    # Final management and persistence
    utils.manage_game_state(old_game_state, new_game_state)
    utils.perform_game_state_update(new_game_state, mongo_client, id)