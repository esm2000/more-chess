"""Gold economy, capture point advantage, and pawn buff assignment."""

from src.types import GameState, GoldSpent
from .board_analysis import get_piece_value


def get_average_piece_value_for_each_side(new_game_state: GameState) -> dict[str, float]:
    """Return average piece value per side, excluding neutral monsters."""
    piece_values = {"white": 0, "black": 0}
    piece_counts = {"white": 0, "black": 0}

    for row in range(len(new_game_state['board_state'])):
        for col in range(len(new_game_state['board_state'])):
            square = new_game_state["board_state"][row][col] or []
            for piece in square:
                piece_type = piece.get("type", "")
                for side in ["white", "black"]:
                    if side in piece_type:
                        piece_values[side] += get_piece_value(piece_type)
                        piece_counts[side] += 1
                        break

    return {
        side: piece_values[side] / piece_counts[side] if piece_counts[side] > 0 else 0
        for side in ["white", "black"]
    }


def update_gold_count(old_game_state: GameState, new_game_state: GameState, gold_spent: GoldSpent) -> None:
    """Award gold for captures and deduct gold spent on purchases."""
    def list_difference(list1: list[str], list2: list[str]) -> list[str]:
        result = list1[:]
        for item in list2:
            if item in result:
                result.remove(item)
        return result

    for side in new_game_state["captured_pieces"]:
        for piece in list_difference(new_game_state["captured_pieces"][side], old_game_state["captured_pieces"][side]):
            new_game_state["gold_count"][side] += 1

        new_game_state["gold_count"][side] -= gold_spent[side]


def update_capture_point_advantage(new_game_state: GameState) -> None:
    """Recalculate capture_point_advantage from current piece values."""
    piece_values = get_average_piece_value_for_each_side(new_game_state)
    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]

    if capture_point_advantage == 0:
        new_game_state["capture_point_advantage"] = None
    else:
        new_game_state["capture_point_advantage"] = [winning_side, capture_point_advantage]


def reassign_pawn_buffs(new_game_state: GameState) -> None:
    """Recalculate and assign pawn_buff values based on current piece value advantage."""
    piece_values = get_average_piece_value_for_each_side(new_game_state)
    winning_side = max(piece_values, key=piece_values.get)
    losing_side = min(piece_values, key=piece_values.get)
    capture_point_advantage = piece_values[winning_side] - piece_values[losing_side]
    pawn_buff = capture_point_advantage if capture_point_advantage < 4 else 3 # capped at 3
    for row in range(8):
        for col in range(8):
            square = new_game_state["board_state"][row][col]
            if square:
                for i, piece in enumerate(square):
                    if "pawn" in piece.get("type", ""):
                        if winning_side in piece.get("type", ""):
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = pawn_buff
                        elif losing_side in piece.get("type", ""):
                            new_game_state["board_state"][row][col][i]["pawn_buff"] = 0
