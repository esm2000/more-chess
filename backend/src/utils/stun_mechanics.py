"""Stun tracking and cleansing for pieces stunned by queen abilities."""

from src.types import GameState


def cleanse_stunned_pieces(new_game_state: GameState) -> None:
    """Remove stun from pieces whose stun duration has expired."""
    for row in new_game_state["board_state"]:
        for square in row:
            if square:
                for piece in square:
                    if piece.get("is_stunned", False) and piece.get("turn_stunned_for", 0) < new_game_state["turn_count"]:
                        del piece['is_stunned']
