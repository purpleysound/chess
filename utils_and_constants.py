import enum
import pickle

DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class GameState(enum.Enum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    DRAW = 3
    WHITE_TURN = 4
    BLACK_TURN = 5

STATE_TO_STR = {
    GameState.ONGOING: "Ongoing",
    GameState.WHITE_WINS: "White Wins!",
    GameState.BLACK_WINS: "Black Wins!",
    GameState.DRAW: "It's a Draw!",
    GameState.WHITE_TURN: "White's Turn",
    GameState.BLACK_TURN: "Black's Turn"
}

ENDED_STATES = {GameState.WHITE_WINS, GameState.BLACK_WINS, GameState.DRAW}

class Prefs:
    BACKGROUND_COLOUR = 0
    CONTRASTING_COLOUR = 1
    MOVE_INDICATOR_COLOUR = 2
    DEFAULT_ENGINE_DEPTH = 3
    FONT_SIZE = 4
    MINIMUM_ENGINE_TIME = 5
    PIECE_IMAGES = 6
    BOARD_IMAGE = 7

# DEFAULT_PREFERENCES = {
#     Prefs.BACKGROUND_COLOUR: (64, 64, 64),
#     Prefs.CONTRASTING_COLOUR: (192, 192, 192),
#     Prefs.MOVE_INDICATOR_COLOUR: (32, 196, 32),
#     Prefs.DEFAULT_ENGINE_DEPTH: 3,
#     Prefs.FONT_SIZE: 28,
#     Prefs.MINIMUM_ENGINE_TIME: 1,
#     Prefs.PIECE_IMAGES: {
#         # keys are piece: int
#         8: "images/wP.svg",
#         9: "images/wN.svg",
#         10: "images/wB.svg",
#         11: "images/wR.svg",
#         12: "images/wQ.svg",
#         13: "images/wK.svg",
#         0: "images/bP.svg",
#         1: "images/bN.svg",
#         2: "images/bB.svg",
#         3: "images/bR.svg",
#         4: "images/bQ.svg",
#         5: "images/bK.svg"
#     },
#     Prefs.BOARD_IMAGE: "images/board.png"
# }

with open("default_preferences.pkl", "rb") as f:
    DEFAULT_PREFERENCES = pickle.load(f)

with open("preferences.pkl", "rb") as f:
    preferences = pickle.load(f)

def vector_add(t1: tuple, t2: tuple) -> tuple:
    """add two tuples together"""
    return tuple(sum(i) for i in zip(t1, t2))

def scalar_mult(t: tuple, s: int) -> tuple:
    """multiply a tuple by a scalar"""
    return tuple(i * s for i in t)

def indices_to_pos(index: int, jndex: int) -> tuple[int, int]:
    """converts indices to coordinates"""
    return (jndex + 1, index + 1)

def pos_to_indices(coords: tuple[int, int]) -> tuple[int, int]:
    """converts coordinates to indices"""
    return (coords[1] - 1, coords[0] - 1)

def pos_to_notation(coords: tuple[int, int]) -> str:
    """converts coordinates to algebraic notation"""
    return f"{chr(coords[0] + 96)}{coords[1]}"

def pos_move_to_uci(move: tuple[tuple[int, int], tuple[int, int]]) -> str:
    """converts a move in coordinates to UCI notation"""
    return f"{pos_to_notation(move[0])}{pos_to_notation(move[1])}"

def uci_to_pos_move(move: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """converts a move in UCI notation to coordinates"""
    return (notation_to_pos(move[:2]), notation_to_pos(move[2:]))

def notation_to_pos(notation: str) -> tuple[int, int]:
    """converts algebraic notation to coordinates"""
    return (ord(notation[0]) - 96, int(notation[1]))
