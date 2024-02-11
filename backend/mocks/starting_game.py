import datetime


starting_game = {
    "turn_count": 0,
    "position_in_play": [None, None],
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
    "board_state": [
        [
            [{"type": "black_rook"}],
            [{"type": "black_knight"}],
            [{"type": "black_bishop", "energize_stacks": 0}],
            [{"type": "black_queen"}],
            [{"type": "black_king"}],
            [{"type": "black_bishop", "energize_stacks": 0}],
            [{"type": "black_knight"}],
            [{"type": "black_rook"}],
        ],
        [
            [{"type": "black_pawn", "pawn_buff": 0}], 
            [{"type": "black_pawn", "pawn_buff": 0}],
            [{"type": "black_pawn", "pawn_buff": 0}],
            None,
            [{"type": "black_pawn", "pawn_buff": 0}],
            [{"type": "black_pawn", "pawn_buff": 0}],
            [{"type": "black_pawn", "pawn_buff": 0}],
            [{"type": "black_pawn", "pawn_buff": 0}]
        ],
        [
            None,
            None,
            None,
            [{"type": "black_pawn", "pawn_buff": 0}],
            None,
            None,
            None,
            None
        ],
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [[{"type": "white_pawn", "pawn_buff": 0}]] * 8,
        [
            [{"type": "white_rook"}],
            [{"type": "white_knight"}],
            [{"type": "white_bishop", "energize_stacks": 0}],
            [{"type": "white_queen"}],
            [{"type": "white_king"}],
            [{"type": "white_bishop", "energize_stacks": 0}],
            [{"type": "white_knight"}],
            [{"type": "white_rook"}],
        ]
    ]
}