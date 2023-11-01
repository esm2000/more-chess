import copy
from fastapi import HTTPException, Response
import pytest

from mocks.empty_game import empty_game
import src.api as api
# for debugging
from src.logging import logger

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
    # TODO: implement a locking mechanism to prevent AI from making move on unit test game

    # white piece selection and movement
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [6, 0]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
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
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["board_state"][5][0][0]["type"] == "white_pawn"
    assert game["board_state"][6][0] is None
    assert game["turn_count"] == 1
    assert len(game["possible_moves"]) == 0
    assert len(game["possible_captures"]) == 0

    # black piece selection and movement
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["position_in_play"] = [1, 0]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response(), player=False)
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
    game = api.update_game_state(game["id"], game_state, Response())

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
    game = api.update_game_state(game["id"], game_state, Response())

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
    game = api.update_game_state(game["id"], game_state, Response())

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
        game = api.update_game_state(game["id"], game_state, Response())

            # black
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][2][3] = game_on_next_turn["board_state"][1][3]
        game_on_next_turn["board_state"][1][3] = None
        game_on_next_turn["board_state"][2][4] = game_on_next_turn["board_state"][1][4]
        game_on_next_turn["board_state"][1][4] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

        # TODO: different piece types

    # invalid moves should not be allowed
        # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][5] = game_on_next_turn["board_state"][6][5]
        game_on_next_turn["board_state"][6][5] = None
        game_on_next_turn["turn_count"] += 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

        # black 
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][5] = game_on_next_turn["board_state"][1][5]
        game_on_next_turn["board_state"][1][5] = None
        game_on_next_turn["turn_count"] += 1
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    # buying pieces with not enough gold should not be allowed
        # white
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "white_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())
        
        # black
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][5][6] = [{"type": "black_pawn", "pawn_buff": 0}]
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    # buying a king or queen should not be allowed
    for side in ["white", "black"]:
        for piece in ["queen", "king"]:
            with pytest.raises(HTTPException):
                game_on_next_turn = copy.deepcopy(game)
                game_on_next_turn["board_state"][5][6] = [{"type": f"{side}_{piece}"}]
                game_state = api.GameState(**game_on_next_turn)
                game = api.update_game_state(game["id"], game_state, Response())

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
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["white"] == 11
    assert game["turn_count"] == 36

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][5][7] = [{"type": "white_knight"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["white"] == 8
    assert game["turn_count"] == 37

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][4] = [{"type": "white_bishop"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["white"] == 5
    assert game["turn_count"] == 38

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][3] = [{"type": "white_rook"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["white"] == 0
    assert game["turn_count"] == 39

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][4] = [{"type": "black_pawn", "pawn_buff": 0}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["black"] == 11
    assert game["turn_count"] == 40

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][2][5] = [{"type": "black_knight"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["black"] == 8
    assert game["turn_count"] == 41

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][4] = [{"type": "black_bishop"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["black"] == 5
    assert game["turn_count"] == 42

    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][3] = [{"type": "black_rook"}]
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())

    assert game["gold_count"]["black"] == 0
    assert game["turn_count"] == 43

    # assert that neutral monsters can't move
    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][4][7]
        game_on_next_turn["board_state"][4][7] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    with pytest.raises(HTTPException):
        game_on_next_turn = copy.deepcopy(game)
        game_on_next_turn["board_state"][3][1] = game_on_next_turn["board_state"][3][0]
        game_on_next_turn["board_state"][3][0] = None
        game_state = api.GameState(**game_on_next_turn)
        game = api.update_game_state(game["id"], game_state, Response())

    # assert that additional captured pieces can't be added from nowhere
    for side in ["white", "black"]:
        with pytest.raises(HTTPException):
            game_on_next_turn = copy.deepcopy(game)
            game_on_next_turn["captured_pieces"][side].append(f"{'white' if side == 'black' else 'black'}_pawn")
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())

    # assert that neutral monsters can be hurt
        # white
    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][6][7][0])
    game_on_next_turn["board_state"][6][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 5
    assert neutral_monster_health_before - neutral_monster_health == 1

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][6] = game_on_next_turn["board_state"][6][6]
    game_on_next_turn["board_state"][6][6] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 4
    assert neutral_monster_health_before - neutral_monster_health == 1

    # black

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][3][7] = game_on_next_turn["board_state"][1][7]
    game_on_next_turn["board_state"][1][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
    neutral_monster_health = game["board_state"][4][7][0]["health"]

    assert neutral_monster_health_before == 3
    assert neutral_monster_health_before - neutral_monster_health == 1

    neutral_monster_health_before = game["board_state"][4][7][0]["health"]
    game_on_next_turn = copy.deepcopy(game)
    game_on_next_turn["board_state"][4][7].append(game_on_next_turn["board_state"][3][7][0])
    game_on_next_turn["board_state"][3][7] = None
    game_state = api.GameState(**game_on_next_turn)
    game = api.update_game_state(game["id"], game_state, Response())
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
                game = api.update_game_state(game["id"], game_state, Response())
                if not i:
                    assert game["board_state"][3][4][0]["type"] == "white_pawn"
                    assert game["board_state"][4][3] is None
                    assert game["turn_count"] == 1
                    assert game["capture_point_advantage"] == ["white", piece_values[piece_type]]
                else:
                    assert game["board_state"][4][3][0]["type"] == "black_pawn"
                    assert game["board_state"][3][4] is None
                    assert game["turn_count"] == 1
                    assert game["capture_point_advantage"] == ["black", piece_values[piece_type]]
        # assert that kings can't be captured
            else:
                with pytest.raises(HTTPException):
                    game = api.update_game_state(game["id"], game_state, Response())

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
            game = api.update_game_state(game["id"], game_state, Response())
            
            turn_count_for_pawn_exchange_initiation = game["turn_count"]
            game_on_next_turn = copy.deepcopy(game)
            if not i:
                game_on_next_turn["board_state"][0][3] = [{"type": f"white_{piece_type}"}]
            else:
                game_on_next_turn["board_state"][7][3] = [{"type": f"black_{piece_type}"}]
            game_state = api.GameState(**game_on_next_turn)
            game = api.update_game_state(game["id"], game_state, Response())
            turn_count_for_end_of_pawn_exhange = game["turn_count"]

            assert turn_count_for_pawn_exchange_initiation == turn_count_for_end_of_pawn_exhange
            assert len(game["board_state"][0 if not i else 7][3]) == 1
            assert game["board_state"][0 if not i else 7][3][0]["type"] == f"{'white' if not i else 'black'}_{piece_type}"
            assert game["previous_state"]["board_state"][0 if not i else 7][3][0]["type"] == f"{'white' if not i else 'black'}_pawn"