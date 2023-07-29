from game import Game
import piece
import json
import time
import random
from functools import lru_cache
import threading

with open("openings/opening_values_d3.json", "r") as f:
    OPENING_VALUES: dict[str, int] = json.load(f)

OPENING_VARIATION = 1.05  # values below 1.05 are too random and above 1.1 are too consistant
nodes_counted = 0

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
    piece_type, piece_colour = piece.get_piece_attrs(p)
    value = piece_values[piece_type]
    if not piece_colour:
        value += piece_square_tables[piece_type][i][j]
        return -value
    else:
        value += piece_square_tables[piece_type][7 - i][j]
        return value

@lru_cache(maxsize=65536)
def base_evaluation(game: Game):
    global nodes_counted
    nodes_counted += 1
    evaluation = 0
    for i, rank in enumerate(game.board):
        for j, item in enumerate(rank):
            if item is not None:
                evaluation += get_piece_value(item, i, j)
    return evaluation

def move_ordering_key(move: tuple[tuple[int, int], tuple[int, int]], game: Game) -> int:
    start, end = move
    start_piece = game.get_piece_from_pos(start)
    assert start_piece is not None
    end_piece = game.get_piece_from_pos(end)
    if end_piece is not None:
        return piece_values[piece.get_piece_type(end_piece)] - piece_values[piece.get_piece_type(start_piece)]
    else:
        return 0

def minimax(game: Game, depth: int, alpha: int, beta: int) -> tuple[int, tuple[tuple[int, int], tuple[int, int]] | None]:
    if depth == 0 or game.king_taken():
        return base_evaluation(game), None
    
    legal_moves = game.get_legal_moves()
    legal_moves.sort(key=lambda move: move_ordering_key(move, game), reverse=True)

    if game.white_move:
        best_score = int(-1e10)
        best_move = None
        for move in legal_moves:
            game_copy = game.copy()
            start_number = game_copy.get_number_of_pieces()
            game_copy.make_move(*move)
            end_number = game_copy.get_number_of_pieces()
            if start_number != end_number and depth == 1:
                decrement = 0
            else:
                decrement = 1
            value, nested_move = minimax(game_copy, depth - decrement, alpha, beta)
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
        for move in legal_moves:
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
    global nodes_counted
    nodes_counted = 0
    t0 = time.time()
    
    legal_openings = []
    if random.randint(1, 3) != 1:
        for move in game.get_legal_moves():
            game_copy = game.copy()
            game_copy.make_move(*move)
            fen = game_copy.get_truncated_fen()
            if fen in OPENING_VALUES:
                legal_openings.append((OPENING_VALUES[fen], move))
    if len(legal_openings) > 0:
        weights = [(x[0])+881 for x in legal_openings]  # 880 is the lowest opening value
        if not game.white_move:
            weights = [1/x for x in weights]
        moves = [x[1] for x in legal_openings]
        move = random.choices(moves, weights)[0]
        for opening in legal_openings:
            if opening[1] == move:
                print(f"Opening found in {time.time() - t0} seconds")
                return opening[0], move

    value, move = minimax(game, depth, int(-1e10), int(1e10))
    print(f"{nodes_counted} nodes counted in {time.time() - t0} seconds")
    return value, move
    

class Engine:
    def __init__(self, game_copy: Game):
        self.game = game_copy
        self.depth = 2
        self.best_move = None
        self.evaluation = 0
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    
    def run(self):
        while True:
            if self.running:
                self.evaluation, self.best_move = minimax(self.game, self.depth, int(-1e10), int(1e10))
                self.depth += 1

    

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
