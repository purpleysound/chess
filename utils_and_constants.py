import enum

DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class GameState(enum.Enum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    DRAW = 3

STATE_TO_STR = {
    GameState.ONGOING: "ongoing",
    GameState.WHITE_WINS: "white wins",
    GameState.BLACK_WINS: "black wins",
    GameState.DRAW: "draw"
}

preferences = {

}

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

def notation_to_pos(notation: str) -> tuple[int, int]:
    """converts algebraic notation to coordinates"""
    return (ord(notation[0]) - 96, int(notation[1]))
