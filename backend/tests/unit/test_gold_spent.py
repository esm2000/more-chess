import copy
from src.utils.validation import get_gold_spent
from src.utils.game_scoring import update_gold_count


def _make_moved_piece(piece_type, side, previous_position, current_position):
    return {
        "piece": {"type": piece_type},
        "side": side,
        "previous_position": previous_position,
        "current_position": current_position,
    }


def test_gold_spent_for_spawned_pawn():
    moved_pieces = [
        _make_moved_piece("white_pawn", "white", [None, None], [5, 4]),
    ]
    gold_spent = get_gold_spent(moved_pieces)
    assert gold_spent == {"white": 2, "black": 0}


def test_gold_spent_for_spawned_knight():
    moved_pieces = [
        _make_moved_piece("white_knight", "white", [None, None], [5, 4]),
    ]
    gold_spent = get_gold_spent(moved_pieces)
    assert gold_spent == {"white": 6, "black": 0}


def test_gold_spent_for_spawned_bishop():
    moved_pieces = [
        _make_moved_piece("white_bishop", "white", [None, None], [5, 4]),
    ]
    gold_spent = get_gold_spent(moved_pieces)
    assert gold_spent == {"white": 6, "black": 0}


def test_gold_spent_for_spawned_rook():
    moved_pieces = [
        _make_moved_piece("white_rook", "white", [None, None], [5, 4]),
    ]
    gold_spent = get_gold_spent(moved_pieces)
    assert gold_spent == {"white": 10, "black": 0}


def test_gold_spent_for_spawned_queen():
    moved_pieces = [
        _make_moved_piece("white_queen", "white", [None, None], [5, 4]),
    ]
    gold_spent = get_gold_spent(moved_pieces)
    assert gold_spent == {"white": 18, "black": 0}


def test_no_gold_spent_for_normal_move():
    moved_pieces = [
        _make_moved_piece("white_pawn", "white", [6, 4], [5, 4]),
    ]
    gold_spent = get_gold_spent(moved_pieces)
    assert gold_spent == {"white": 0, "black": 0}


def test_no_gold_spent_when_no_pieces_moved():
    gold_spent = get_gold_spent([])
    assert gold_spent == {"white": 0, "black": 0}


def _make_game_state(captured_pieces, gold_count):
    return {
        "captured_pieces": captured_pieces,
        "gold_count": copy.deepcopy(gold_count),
    }


def test_capture_gives_1_gold_for_pawn():
    old = _make_game_state({"white": [], "black": []}, {"white": 0, "black": 0})
    new = _make_game_state({"white": ["black_pawn"], "black": []}, {"white": 0, "black": 0})
    update_gold_count(old, new, {"white": 0, "black": 0})
    assert new["gold_count"] == {"white": 1, "black": 0}


def test_capture_gives_1_gold_for_queen():
    old = _make_game_state({"white": [], "black": []}, {"white": 0, "black": 0})
    new = _make_game_state({"white": ["black_queen"], "black": []}, {"white": 0, "black": 0})
    update_gold_count(old, new, {"white": 0, "black": 0})
    assert new["gold_count"] == {"white": 1, "black": 0}


def test_capture_gives_1_gold_for_rook():
    old = _make_game_state({"white": [], "black": []}, {"white": 0, "black": 0})
    new = _make_game_state({"white": ["black_rook"], "black": []}, {"white": 0, "black": 0})
    update_gold_count(old, new, {"white": 0, "black": 0})
    assert new["gold_count"] == {"white": 1, "black": 0}


def test_multiple_captures_give_1_gold_each():
    old = _make_game_state({"white": [], "black": []}, {"white": 0, "black": 0})
    new = _make_game_state({"white": ["black_pawn", "black_knight"], "black": []}, {"white": 0, "black": 0})
    update_gold_count(old, new, {"white": 0, "black": 0})
    assert new["gold_count"] == {"white": 2, "black": 0}


def test_capture_gold_and_shop_deduction_combined():
    old = _make_game_state({"white": [], "black": []}, {"white": 5, "black": 0})
    new = _make_game_state({"white": ["black_pawn"], "black": []}, {"white": 5, "black": 0})
    update_gold_count(old, new, {"white": 2, "black": 0})
    assert new["gold_count"] == {"white": 4, "black": 0}  # 5 + 1 capture - 2 shop
