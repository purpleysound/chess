from game import Game
import piece
import json
import math

with open("openings/opening_values_d3.json", "r") as f:
    OPENING_VALUES = json.load(f)

piece_values = {
    piece.PAWN: 100,
    piece.KNIGHT: 320,
    piece.BISHOP: 330,
    piece.ROOK: 500,
    piece.QUEEN: 900,
    piece.KING: 20000
}
piece_square_tables = {
    piece.PAWN: [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    piece.KNIGHT: [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ],
    piece.BISHOP: [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ],
    piece.ROOK: [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0, 0, 0, 5, 5, 0, 0, 0]
    ],
    piece.QUEEN: [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ],
    piece.KING: [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]
    ]
}

def get_piece_value(p: int, i: int, j: int):
    piece_type, piece_colour, _ = piece.get_piece_attrs(p)
    value = piece_values[piece_type]
    if not piece_colour:
        value += piece_square_tables[piece_type][i][j]
        return -value
    else:
        value += piece_square_tables[piece_type][7 - i][j]
        return value

def base_evaluation(game: Game):
    evaluation = 0
    for i, rank in enumerate(game.board):
        for j, item in enumerate(rank):
            if item is not None:
                evaluation += get_piece_value(item, i, j)
    return evaluation

def minimax(game: Game, depth: int, alpha: int, beta: int) -> tuple[int, tuple[tuple[int, int], tuple[int, int]] | None]:
    if depth == 0 or game.king_taken():
        return base_evaluation(game), None
    
    if game.white_move:
        best_score = int(-1e10)
        best_move = None
        for move in game.get_legal_moves():
            game_copy = game.copy()
            game_copy.make_move(*move)
            value, nested_move = minimax(game_copy, depth - 1, alpha, beta)
            if value > best_score:
                best_score = value
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = int(1e10)
        best_move = None
        for move in game.get_legal_moves():
            game_copy = game.copy()
            game_copy.make_move(*move)
            value, nested_move = minimax(game_copy, depth - 1, alpha, beta)
            if value < best_score:
                best_score = value
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
    
def get_value_and_best_move(game: Game, depth: int) -> tuple[int, tuple[tuple[int, int], tuple[int, int]] | None]:
    value, move = minimax(game, depth, int(-1e10), int(1e10))
    return value, move
    

# if __name__ == "__main__":
#     from openings import opening_explorer
#     import json
#     import time
#     d = 0
#     while True:
#         t0 = time.time()
#         opening_values = {}
#         for fen in opening_explorer.FENs:
#             opening_values[fen] = get_value_and_best_move(Game(fen), d)[0]
#         with open(f"openings/opening_values_d{str(d)}.json", "w") as f:
#             json.dump(opening_values, f, indent=4)
#         print(time.time() - t0)
#         d += 1
