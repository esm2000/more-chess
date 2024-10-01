import copy
from fastapi import HTTPException, Response
import pytest

from mocks.empty_game import empty_game
import src.api as api
from src.utility import clear_game


@pytest.fixture
def game():
    game = api.create_game()
    yield game
    result = api.delete_game(game["id"])
    assert result.get("message") == "Success"
    assert "not found" in api.retrieve_game_state(game["id"], Response()).get("message")


def test_game_created(game):
    for key in [
        "id",
        "turn_count",
        "position_in_play",
        "board_state",
        "possible_moves",
        "possible_captures",
        "captured_pieces",
        "graveyard",
        "sword_in_the_stone_position",
        "capture_point_advantage",
        "player_victory",
        "player_defeat",
        "gold_count",
    ]:
        assert key in game
    assert game["turn_count"] == 0
    assert game["position_in_play"] == [None, None]
    pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for i, black_piece in enumerate(game["board_state"][0]):
        assert "black" in black_piece[0]["type"]
        assert pieces[i] in black_piece[0]["type"]
    for i, black_piece in enumerate(game["board_state"][1]):
        if i == 3:
            continue
        assert "black" in black_piece[0]["type"]
        assert "pawn" in black_piece[0]["type"]
    for row in [2, 3, 4, 5]:
        for col in range(8):
            if row == 2 and col == 3:
                assert "black" in black_piece[0]["type"]
                assert "pawn" in black_piece[0]["type"]
            else:
                assert game["board_state"][row][col] is None
    pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    pieces += ["pawn"] * 8
    for i, white_piece in enumerate(game["board_state"][7] + game["board_state"][6]):
        assert "white" in white_piece[0]["type"]
        assert pieces[i] in white_piece[0]["type"]
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0
    assert len(game["captured_pieces"]["white"]) == 0
    assert len(game["captured_pieces"]["black"]) == 0
    assert len(game["graveyard"]) == 0
    assert (
        not game["sword_in_the_stone_position"]
        and not game["capture_point_advantage"]
        and not game["player_victory"]
        and not game["player_defeat"]
        and not game["gold_count"]["white"]
        and not game["gold_count"]["black"]
    )


def test_alter_game(game):
    # white piece selection and movement
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [6, 0]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    game_on_previous_turn = game_on_next_turn

    assert game["board_state"] == game_on_previous_turn["board_state"]
    assert game["position_in_play"] == [6, 0]
    assert game["turn_count"] == game_on_previous_turn["turn_count"]
    assert sorted(game["possible_moves"]) == sorted([[5, 0], [4, 0]])
    assert len(game["possible_captures"]) == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][0] = game_on_next_turn["board_state"][6][0]
    game_on_next_turn["board_state"][6][0] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][5][0][0]["type"] == "white_pawn"
    assert game["board_state"][6][0] is None
    assert game["turn_count"] == 1
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0

    # black piece selection and movement
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [1, 0]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False, disable_turn_check=True)
    game_on_previous_turn = game_on_next_turn

    assert game["board_state"] == game_on_previous_turn["board_state"]
    assert game["position_in_play"] == [1, 0]
    assert game["turn_count"] == game_on_previous_turn["turn_count"]
    assert sorted(game["possible_moves"]) == sorted([[2, 0], [3, 0]])
    assert len(game["possible_captures"]) == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][0] = game_on_next_turn["board_state"][1][0]
    game_on_next_turn["board_state"][1][0] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][2][0][0]["type"] == "black_pawn"
    assert game["board_state"][1][0] is None
    assert game["turn_count"] == 2
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0

    # cache removal
    assert game["turn_count"] == 2
    assert not game["previous_state"].get("previous_state")

    # spawn monsters
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 9
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][1] = game_on_next_turn["board_state"][6][1]
    game_on_next_turn["board_state"][6][1] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][4][7][0]["type"] == "neutral_dragon"
    assert game["board_state"][3][0][0]["type"] == "neutral_board_herald"

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["turn_count"] = 34
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][2] = game_on_next_turn["board_state"][6][2]
    game_on_next_turn["board_state"][6][2] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][3][0][0]["type"] == "neutral_baron_nashor"

    # moving more than one piece should not be allowed 
        # same piece types
            # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][3] = game_on_next_turn["board_state"][6][3]
        game_on_next_turn["board_state"][6][3] = None
        game_on_next_turn["board_state"][5][4] = game_on_next_turn["board_state"][6][4]
        game_on_next_turn["board_state"][6][4] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

            # black
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][2][3] = game_on_next_turn["board_state"][1][3]
        game_on_next_turn["board_state"][1][3] = None
        game_on_next_turn["board_state"][2][4] = game_on_next_turn["board_state"][1][4]
        game_on_next_turn["board_state"][1][4] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

        # TODO: different piece types

    # invalid moves should not be allowed
        # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][5] = game_on_next_turn["board_state"][6][5]
        game_on_next_turn["board_state"][6][5] = None
        game_on_next_turn["turn_count"] += 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

        # black 
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][5] = game_on_next_turn["board_state"][1][5]
        game_on_next_turn["board_state"][1][5] = None
        game_on_next_turn["turn_count"] += 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    # buying pieces with not enough gold should not be allowed
        # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "white_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
        
        # black
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "black_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    # buying a king or queen should not be allowed
    for side in ["white", "black"]:
        for piece in ["queen", "king"]:
            with pytest.raises(HTTPException):
                game_on_next_turn = copy.deepcopy(game)
                game_on_next_turn["board_state"][5][6] = [{"type": f"{side}_{piece}"}]
                game_state = api.GameState(**game_on_next_turn)
                game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    # buying pieces
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["gold_count"] = {
        "white": 12,
        "black": 12
    }
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][6] = [{"type": "white_pawn", "pawn_buff": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 11
    assert game["turn_count"] == 36

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][7] = [{"type": "white_knight"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 8
    assert game["turn_count"] == 37

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][4] = [{"type": "white_bishop"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 5
    assert game["turn_count"] == 38

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][3] = [{"type": "white_rook"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["white"] == 0
    assert game["turn_count"] == 39

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["black"] == 11
    assert game["turn_count"] == 40

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][5] = [{"type": "black_knight"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["black"] == 8
    assert game["turn_count"] == 41

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][4] = [{"type": "black_bishop"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["black"] == 5
    assert game["turn_count"] == 42

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_rook"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["gold_count"]["black"] == 0
    assert game["turn_count"] == 43

    # assert that neutral monsters can't move
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][4][7]
        game_on_next_turn["board_state"][4][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][1] = game_on_next_turn["board_state"][3][0]
        game_on_next_turn["board_state"][3][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    # assert that additional captured pieces can't be added from nowhere
    for side in ["white", "black"]:
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["captured_pieces"][side].append(f"{'white' if side == 'black' else 'black'}_pawn")
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    # assert that neutral monsters can be hurt
        # white
    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][6][7][0])
    game_on_next_turn["board_state"][6][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 5
    assert neutral_monster_health_before - neutral_monster_health == 1

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][6][6]
    game_on_next_turn["board_state"][6][6] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 4
    assert neutral_monster_health_before - neutral_monster_health == 1

    # black

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][7] = game_on_next_turn["board_state"][1][7]
    game_on_next_turn["board_state"][1][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 3
    assert neutral_monster_health_before - neutral_monster_health == 1

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][3][7][0])
    game_on_next_turn["board_state"][3][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 2
    assert neutral_monster_health_before - neutral_monster_health == 1

    # assert that capture point advantage is calculated right
    piece_values = {
        "pawn": 1,
        "knight": 3,
        "bishop": 3,
        "rook": 5,
        "queen": 9, 
        "king": None
    }

    for i in [0, 1]:
        for piece_type in piece_values:
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["turn_count"] = 0
            game_on_next_turn["board_state"] = copy.deepcopy(empty_game["board_state"])
            game_on_next_turn["board_state"][3][4] = [{"type": f"black_{piece_type}"}] if not i else [{"type": "black_pawn", "pawn_buff": 0}]
            game_on_next_turn["board_state"][4][3] = [{"type": "white_pawn", "pawn_buff": 0}] if not i else [{"type": f"white_{piece_type}"}]
            if piece_type == "bishop":
                game_on_next_turn["board_state"][3 if not i else 4][4 if not i else 3][0]["energize_stacks"] = 0
            game_on_next_turn["graveyard"] = []
            game_on_next_turn["gold_count"] = {
                "white": 0,
                "black": 0
            }
            game_on_next_turn["captured_pieces"] = {"white": [], "black": []}
            del game_on_next_turn["previous_state"]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
            game_on_next_turn = copy.deepcopy(game)
            if not i:
                game_on_next_turn["board_state"][3][4] = game_on_next_turn["board_state"][4][3]
                game_on_next_turn["board_state"][4][3] = None
                game_on_next_turn["captured_pieces"]["white"].append(f"black_{piece_type}")
            else:
                game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][4]
                game_on_next_turn["board_state"][3][4] = None
                game_on_next_turn["captured_pieces"]["black"].append(f"white_{piece_type}")
            game_state = api.GameState(**game_on_next_turn)
            if piece_type != "king":
                game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
                if not i:
                    assert game["board_state"][3][4][0]["type"] == "white_pawn"
                    assert game["board_state"][4][3] is None
                    # none of black's pieces are left so its turn is skipped
                    assert game["turn_count"] == 2
                    assert game["capture_point_advantage"] == ["white", piece_values[piece_type]]
                else:
                    assert game["board_state"][4][3][0]["type"] == "black_pawn"
                    assert game["board_state"][3][4] is None
                    assert game["turn_count"] == 1
                    assert game["capture_point_advantage"] == ["black", piece_values[piece_type]]
        # assert that kings can't be captured
            else:
                with pytest.raises(HTTPException):
                    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    # validate pawn exchange
            if piece_type == "pawn":
                continue
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["turn_count"] = 0
            game_on_next_turn["board_state"] = copy.deepcopy(empty_game["board_state"])
            if not i:
                game_on_next_turn["board_state"][1][3] = [{"type": "white_pawn", "pawn_buff": 0}] 
                game_on_next_turn["board_state"][3][4] = [{"type": f"black_king"}]
            else:
                game_on_next_turn["board_state"][6][3] = [{"type": "black_pawn", "pawn_buff": 0}] 
                game_on_next_turn["board_state"][3][4] = [{"type": f"white_king"}]
            game_on_next_turn["graveyard"] = []
            game_on_next_turn["gold_count"] = {
                "white": 0,
                "black": 0
            }
            game_on_next_turn["captured_pieces"] = {"white": [], "black": []}
            del game_on_next_turn["previous_state"]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            game_on_next_turn = copy.deepcopy(game)
            if not i:
                game_on_next_turn["board_state"][0][3] = game_on_next_turn["board_state"][1][3]
                game_on_next_turn["board_state"][1][3] = None
            else:
                game_on_next_turn["board_state"][7][3] = game_on_next_turn["board_state"][6][3]
                game_on_next_turn["board_state"][6][3] = None
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
            
            turn_count_for_pawn_exchange_initiation = game["turn_count"]
            game_on_next_turn = copy.deepcopy(game)
            if not i:
                game_on_next_turn["board_state"][0][3] = [{"type": f"white_{piece_type}"}]
            else:
                game_on_next_turn["board_state"][7][3] = [{"type": f"black_{piece_type}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
            turn_count_for_end_of_pawn_exhange = game["turn_count"]

            assert turn_count_for_pawn_exchange_initiation == turn_count_for_end_of_pawn_exhange
            assert len(game["board_state"][0 if not i else 7][3]) == 1
            assert game["board_state"][0 if not i else 7][3][0]["type"] == f"{'white' if not i else 'black'}_{piece_type}"
            assert game["previous_state"]["board_state"][0 if not i else 7][3][0]["type"] == f"{'white' if not i else 'black'}_pawn"


def test_bishop_energize_stacks(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    
    game_on_next_turn["board_state"][3][3] = [{"type": "white_bishop", "energize_stacks": 0}]
    game_on_next_turn["board_state"][1][1] = [{"type": "black_pawn", "pawn_buff": 0}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][1] = [{"type": "white_bishop", "energize_stacks": 0}]
    game_on_next_turn["board_state"][3][3] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][1][1][0]["energize_stacks"] == 20


def test_bishop_debuff_application(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][0][0] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][0][6] = [{"type": "black_pawn", "bishop_debuff": 1}]
    game_on_next_turn["board_state"][6][6] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 3}]
    game_on_next_turn["board_state"][5][1] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][1] = None 
    game_on_next_turn["board_state"][3][3] = [{"type": "white_bishop", "energize_stacks": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][0][0][0].get("bishop_debuff") == 1
    assert game["board_state"][0][6][0].get("bishop_debuff") == 2
    assert game["board_state"][6][6][0].get("bishop_debuff") == 3
    assert game["board_state"][6][0][0].get("bishop_debuff") == 3


def test_adjacent_capture_of_bishop(game):
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "white_knight"}]
    game_on_next_turn["board_state"][4][5] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][5][5] = [{"type": "black_bishop", "energize_stacks": 0}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = None 
    game_on_next_turn["board_state"][4][5] = [{"type": "white_knight"}]
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][5][5] is None
    assert sorted(game["captured_pieces"]["white"]) == sorted(["black_bishop", "black_pawn"])


def test_queen_stun(game):
    # make sure queen stuns when expected to 
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7] = None
    game_on_next_turn["board_state"][4][3] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][3][3][0]["type"] == "black_pawn"
    assert game["board_state"][3][3][0]["is_stunned"]

    # make sure queen doesn't stun when not expected to
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7] = None
    game_on_next_turn["board_state"][4][6] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][3][3][0]["type"] == "black_pawn"
    assert not game["board_state"][3][3][0].get("is_stunned", False)

    # make sure queen is able to apply stun after it captures a piece,
    # opponent moves, and queen moves but doesn't capture a piece
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][0] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][3][7] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][7] = None
    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    game_on_next_turn[ "captured_pieces"] = {"white": ["black_pawn"], "black": []}
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][0] = None
    game_on_next_turn["board_state"][2][0] = [{"type": "black_pawn"}]
    game_state = api.GameState(**game_on_next_turn)
    game_on_next_turn["previous_state"] = copy.deepcopy(game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = None
    game_on_next_turn["board_state"][3][0] = [{"type": "white_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][2][0][0]["type"] == "black_pawn"
    assert game["board_state"][2][0][0].get("is_stunned", False) 
    
    # ensure that the player can't move when stunned
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "white_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "black_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7] = None
    game_on_next_turn["board_state"][4][4] = [{"type": "black_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = None
    game_on_next_turn["board_state"][2][3] = [{"type": "white_pawn"}]
    game_state = api.GameState(**game_on_next_turn)
    with pytest.raises(Exception):
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)


def test_stun_cleanse(game):
    # ensure that stuns cleanse after a player moves for their next turn
    game = clear_game(game)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "white_pawn"}]
    game_on_next_turn["board_state"][3][2] = [{"type": "white_pawn"}]
    game_on_next_turn["board_state"][4][7] = [{"type": "black_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7] = None
    game_on_next_turn["board_state"][4][4] = [{"type": "black_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][2] = None
    game_on_next_turn["board_state"][2][2] = [{"type": "white_pawn"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][4] = None
    game_on_next_turn["board_state"][4][5] = [{"type": "black_queen"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][3][3][0]["type"] == "white_pawn"
    assert not game["board_state"][3][3][0].get("is_stunned", False) 


def test_full_bishop_debuff_capture(game):
    # test the capturing mechanism for pieces with full bishop debuff stacks
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][5][1] = game_on_next_turn["board_state"][4][2]
    game_on_next_turn["board_state"][4][2] = None
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    
    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_on_next_turn["board_state"][6][0] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [6, 0],
        "type": "black_pawn"
    })
    game_on_next_turn["gold_count"]["white"] += 2
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 10
    assert not game["board_state"][6][0]
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_pawn"]
    assert game["bishop_special_captures"] == []


def test_bishop_debuff_double_stack_prevention(game):
    # bishops can be captured by landing on a square diagonally adjacent to it
    # there can be a weird scenario that can lead to double the bishop debuffs 
    # being applied to enemy bishops

    # example situation: 
        # black bishop, posiiton [0, 5]
        # black non-king piece, position [1, 4]
        # black non-king piece, position [1, 6]
        # white bishop, moves to position [2, 5]
        # there can be a bug where the black bishop incorrectly gets two bishop stacks instead of one
    
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][0][5] = [{"type": "black_bishop", "energize_stacks": 0}]
    game_on_next_turn["board_state"][1][4] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_on_next_turn["board_state"][1][6] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_on_next_turn["board_state"][3][4] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][2][5] = game_on_next_turn["board_state"][3][4]
    game_on_next_turn["board_state"][3][4] = None
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][0][5][0].get("bishop_debuff", 0) == 1
 
def test_full_bishop_debuff_adjacent_application(game):
    # test the capturing mechanism still works when a piece is in danger from being
    # captured adjacently 
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 0}]
    game_on_next_turn["board_state"][7][1] = [{"type": "black_knight", "bishop_debuff": 2}]

    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 95}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][5][1] = game_on_next_turn["board_state"][4][2]
    game_on_next_turn["board_state"][4][2] = None
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 1
    
    assert game["board_state"][7][1][0]["bishop_debuff"] == 3
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_knight")
    game_on_next_turn["board_state"][7][1] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [7, 1],
        "type": "black_knight"
    })
    game_on_next_turn["gold_count"]["white"] += 6
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    
    assert not game["board_state"][7][1]
    assert game["board_state"][6][0][0]["type"] == "black_pawn"
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_knight"]
    assert game["bishop_special_captures"] == []


def test_full_bishop_debuff_spare(game):
    # test the ability for pieces with full bishop debuff stacks to be spared
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][5][1] = game_on_next_turn["board_state"][4][2]
    game_on_next_turn["board_state"][4][2] = None
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][6][0][0]["bishop_debuff"] = 0
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 0
    assert game["board_state"][6][0][0]["type"] == "black_pawn"
    assert game["board_state"][6][0][0]["bishop_debuff"] == 0
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["bishop_special_captures"] == []


def test_multiple_full_bishop_debuffs(game):
    # ensure that game can handle multiple pieces with full bishop debuff stacks well
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][6][2] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][5][1] = game_on_next_turn["board_state"][4][2]
    game_on_next_turn["board_state"][4][2] = None
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    assert game["board_state"][6][2][0]["bishop_debuff"] == 3
    assert game["board_state"][2][4][0]["bishop_debuff"] == 3

    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_on_next_turn["board_state"][6][0] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [6, 0],
        "type": "black_pawn"
    })
    game_on_next_turn["gold_count"]["white"] += 2
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 10
    assert not game["board_state"][6][0]
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_pawn"]
    assert game["bishop_special_captures"] == []

    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["captured_pieces"]["white"].append("black_pawn")
    game_on_next_turn["board_state"][6][2] = []
    game_on_next_turn["bishop_special_captures"].append({
        "position": [6, 2],
        "type": "black_pawn"
    })
    game_on_next_turn["gold_count"]["white"] += 2
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 10
    assert not game["board_state"][6][2]
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["captured_pieces"]["white"] == ["black_pawn", "black_pawn"]
    assert game["bishop_special_captures"] == []

    original_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][4][0]["bishop_debuff"] = 0
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)
    
    current_energize_stack_value = game["board_state"][5][1][0]["energize_stacks"]
    energize_stack_difference = current_energize_stack_value - original_energize_stack_value

    assert energize_stack_difference == 0
    assert game["board_state"][2][4][0]["type"] == "black_pawn"
    assert game["board_state"][2][4][0]["bishop_debuff"] == 0
    assert game["board_state"][5][1][0]["type"] == "white_bishop"
    assert game["bishop_special_captures"] == []


def test_full_bishop_debuff_stacks_prevent_other_moves(game):
    # ensure that game prevent other moves from either side when full bishop debuff stacks are present
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][6][0] = [{"type": "black_pawn", "bishop_debuff": 2}]
    game_on_next_turn["board_state"][4][2] = [{"type": "white_bishop", "energize_stacks": 0}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][5][1] = game_on_next_turn["board_state"][4][2]
    game_on_next_turn["board_state"][4][2] = None
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

    assert game["board_state"][6][0][0]["bishop_debuff"] == 3
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][0] = game_on_next_turn["board_state"][6][0]
    game_on_next_turn["board_state"][6][0] = None

    game_state = api.GameState(**game_on_next_turn)
    with pytest.raises(HTTPException):
        game = api.update_game_state(game["id"], game_state, Response(), disable_turn_check=True)

def test_that_two_turns_are_not_allowed_from_the_same_side(game):
    # test that when the turn check is enabled that two turns are not allowed from the same side
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][2][0] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][6][0] = [{"type": "white_pawn"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [6, 0]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][0] = game_on_next_turn["board_state"][6][0]
    game_on_next_turn["board_state"][6][0] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [5, 0]

    game_state = api.GameState(**game_on_next_turn)
    with pytest.raises(HTTPException):
        game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][0] = game_on_next_turn["board_state"][5][0]
    game_on_next_turn["board_state"][5][0] = None

    game_state = api.GameState(**game_on_next_turn)
    with pytest.raises(HTTPException):
        game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][0] = game_on_next_turn["board_state"][2][0]
    game_on_next_turn["board_state"][2][0] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][0] = game_on_next_turn["board_state"][3][0]
    game_on_next_turn["board_state"][3][0] = None

    game_state = api.GameState(**game_on_next_turn)
    with pytest.raises(HTTPException):
        game = api.update_game_state(game["id"], game_state, Response())
    

def test_skip_one_turn_if_all_non_king_pieces_are_stunned(game):
    # test that when all non-king pieces are stunned that a turn is skipped (with turn check enabled)
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][2][2] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][6][3] = [{"type": "white_queen"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())
    
    assert game["turn_count"] == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][3] = game_on_next_turn["board_state"][6][3]
    game_on_next_turn["board_state"][6][3] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["turn_count"] == 2
    assert game["board_state"][2][2][0].get("is_stunned", False)
    assert game["board_state"][2][4][0].get("is_stunned", False)

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][2] = game_on_next_turn["board_state"][2][2]
        game_on_next_turn["board_state"][2][2] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][6][3] = game_on_next_turn["board_state"][2][3]
    game_on_next_turn["board_state"][2][3] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["turn_count"] == 3
    assert not game["board_state"][2][2][0].get("is_stunned", False)
    assert not game["board_state"][2][4][0].get("is_stunned", False)


def test_queen_kill_reset(game):
    # test that a queen is able to go again after getting a kill
    # and that queen is automatically in play upon gaining reset
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][1][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["turn_count"] == 0
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][3] = game_on_next_turn["board_state"][3][3]
    game_on_next_turn["board_state"][3][3] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["position_in_play"] == [1, 3]
    assert game["queen_reset"]
    assert game["turn_count"] == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][0] = game_on_next_turn["board_state"][1][3]
    game_on_next_turn["board_state"][1][3] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert not game["queen_reset"]
    assert game["turn_count"] == 1


def test_queen_assist_reset(game):
    # test that a queen is able to go again after getting a assist
    # and that queen is automatically in play upon gaining reset
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][1][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    game_on_next_turn["board_state"][1][2] = [{"type": "white_rook"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["turn_count"] == 0
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][3] = game_on_next_turn["board_state"][1][2]
    game_on_next_turn["board_state"][1][2] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["position_in_play"] == [3, 3]
    assert game["queen_reset"]
    assert game["turn_count"] == 0

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][3]
    game_on_next_turn["board_state"][3][3] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert not game["queen_reset"]
    assert game["turn_count"] == 1


def test_queen_turn_reset_limitations(game):
    # test that a turn reset with a queen does not enable other non-queen pieces to move and that the turn reset doesn't stack
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][1][3] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][7] = [{"type": "black_pawn"}]

    game_on_next_turn["board_state"][3][3] = [{"type": "white_queen"}]
    game_on_next_turn["board_state"][1][2] = [{"type": "white_rook"}]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    assert game["turn_count"] == 0
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][1][3] = game_on_next_turn["board_state"][1][2]
    game_on_next_turn["board_state"][1][2] = None
    game_on_next_turn["captured_pieces"]["white"].append(f"black_pawn")

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["position_in_play"] == [3, 3]
    assert game["queen_reset"]
    assert game["turn_count"] == 0

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["position_in_play"] = [1, 3]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
    
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][1][4] = game_on_next_turn["board_state"][1][3]
        game_on_next_turn["board_state"][1][3] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][3]
    game_on_next_turn["board_state"][3][3] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert not game["queen_reset"]
    assert game["turn_count"] == 1

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][3] = game_on_next_turn["board_state"][4][3]
        game_on_next_turn["board_state"][4][3] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
    
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][7] = game_on_next_turn["board_state"][1][7]
    game_on_next_turn["board_state"][1][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert not game["queen_reset"]
    assert game["turn_count"] == 2


def test_neutral_monster_captures_after_spawning_on_any_non_king_piece(game):
    # neutral monster should automatically send non-king pieces to the graveyard
    game = clear_game(game)
    game_on_next_turn = copy.deepcopy(game)

    game_on_next_turn["board_state"][3][7] = [{"type": "black_pawn"}]
    game_on_next_turn["board_state"][1][1] = [{"type": "black_king"}]
    game_on_next_turn["board_state"][7][1] = [{"type": "white_king"}]
 
    game_on_next_turn["turn_count"] = 9
    assert not game["graveyard"]

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7] = game_on_next_turn["board_state"][3][7]
    game_on_next_turn["board_state"][3][7] = None

    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["turn_count"] == 10
    assert game["board_state"][4][7][0].get("type") == "neutral_dragon"
    assert "black_pawn" in game["graveyard"] 


def test_neutral_monster_ends_game_after_spawning_on_king(game):
    # neutral monster should automatically send non-king pieces to the graveyard
    for side in ["white", "black"]:
        game = clear_game(game)
        game_on_next_turn = copy.deepcopy(game)

        if side == "black":
            game_on_next_turn["board_state"][3][7] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][7][1] = [{"type": "white_king"}]
        else:
            game_on_next_turn["board_state"][7][1] = [{"type": "black_king"}]
            game_on_next_turn["board_state"][4][7] = [{"type": "white_king"}]
    
        game_on_next_turn["turn_count"] = 9
        assert not game["graveyard"]

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

        game_on_next_turn = copy.deepcopy(game)
        if side == "black":
            game_on_next_turn["board_state"][4][7] = game_on_next_turn["board_state"][3][7]
            game_on_next_turn["board_state"][3][7] = None
        else:
            game_on_next_turn["board_state"][7][2] = game_on_next_turn["board_state"][7][1]
            game_on_next_turn["board_state"][7][1] = None

        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

        assert game["turn_count"] == 10
        assert (game["board_state"][4][7] or [{}])[0].get("type") == "neutral_dragon"
        if side == "black":
            assert game["player_victory"]
        else:
            assert game["player_defeat"]


def test_sword_in_the_stone_spawn(game):
    # run a test 50 times and see that the sword in the stone spawns in a suitable location every time
    locations = {}
    for i in range(5):
        for turn in [9, 19, 29, 39, 49]:
            game = clear_game(game)
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][3][3] = [{"type": "black_pawn"}]
            game_on_next_turn["board_state"][3][4] = [{"type": "white_pawn"}]
            game_on_next_turn["turn_count"] = turn

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state_no_restrictions(game["id"], game_state, Response())

            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["board_state"][4][3] = game_on_next_turn["board_state"][3][3]
            game_on_next_turn["board_state"][3][3] = None

            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())

            if game["sword_in_the_stone_position"] in locations:
                game["sword_in_the_stone_position"] += 1
            else:
                game["sword_in_the_stone_position"] = 1

            assert game["turn_count"] == turn + 1
            assert game["sword_in_the_stone_position"]
    for location in locations:
        assert locations[location] < 13


def test_sword_in_the_stone_retrieval(game):
    # test that both kings can retrieve the sword in the stone and its accompanying buff
    pass 


def test_sword_in_the_stone_stacks(game):
    # test that the sword in the stone appropiately stacks
    pass


def test_sword_in_the_stone_check_protection(game):
    # test that the sword_in_the_stone protects king from check
    pass


def test_white_check(game):
    # test that white can be checked
    pass


def test_black_check(game):
    # test that black can be checked
    pass

def test_white_in_check_and_needs_a_non_king_piece_to_get_it_out_of_check(game):
    # test that when white king is in check and can't move anywhere to get out of check
    # but another white piece can save it, the game doesn't improperly end

    # also ensure that saving that piece is the only valid move white can make
    pass

def test_black_in_check_and_needs_a_non_king_piece_to_get_it_out_of_check(game):
    # test that when black king is in check and can't move anywhere to get out of check
    # but another black piece can save it, the game doesn't improperly end

    # also ensure that saving that piece is the only valid move black can make
    pass

def test_white_checkmate(game):
    # test that white can be checkmated
    pass

def test_black_checkmate(game):
    # test that black can be checkmated
    pass

def test_king_cant_put_itself_in_check(game):
    # test that king can't move and put itself into check
    pass

def test_king_cant_get_close_to_king(game):
    # test that king can't move next to another king
    pass

def test_game_ends_when_monster_spawns_on_top_of_king(game):
    # test that the game ends when a monster spawns on top of a king
    pass

def test_game_ends_when_king_stays_near_neutral_monster(game):
    # test that the game ends when a king stays near a neutral monster 
    pass

def test_capture_behavior_when_neutral_and_normal_piece_are_on_same_square(game):
    # test both when the neutral monster has over 1hp and when it has 1 hp
    pass