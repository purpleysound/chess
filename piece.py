from utils_and_constants import *

PAWN = 0b00000
KNIGHT = 0b00001
BISHOP = 0b00010
ROOK = 0b00011
QUEEN = 0b00100
KING = 0b00101

WHITE = 0b01000
BLACK = 0b00000

def generate_piece(piece: int, white: bool) -> int:
    return piece + (WHITE if white else BLACK)

def get_piece_attrs(piece: int) -> tuple[int, bool]:
    """return piece, white"""
    return piece & 0b00111, bool(piece & 0b01000)

def get_piece_type(piece: int) -> int:
    return piece & 0b00111

def get_piece_colour(piece: int) -> bool:
    return bool(piece & 0b01000)
