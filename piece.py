from utils_and_constants import *

PAWN = 0b00000
KNIGHT = 0b00001
BISHOP = 0b00010
ROOK = 0b00011
QUEEN = 0b00100
KING = 0b00101

WHITE = 0b01000
BLACK = 0b00000

MOVED = 0b10000
NOT_MOVED = 0b00000

def generate_piece(piece: int, white: bool, moved: bool = False) -> int:
    return piece + (WHITE if white else BLACK) + (MOVED if moved else NOT_MOVED)

def get_piece_attrs(piece: int) -> tuple[int, bool, bool]:
    """return piece, white, moved"""
    return piece & 0b00111, bool(piece & 0b01000), bool(piece & 0b10000)

def update_moved_bit(piece: int) -> int:
    return piece | MOVED
