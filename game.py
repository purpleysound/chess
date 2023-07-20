from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from utils_and_constants import *

DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
w_or_b = {"w": True, "b": False}
letter_to_class = {"p": Pawn, "n": Knight, "b": Bishop, "r": Rook, "q": Queen, "k": King}

class Game:
    def __init__(self, fen: str = DEFAULT_FEN):
        fboard, fmove, fcastling, fEn_passant, fhalf_move, ffull_move = fen.split(" ")
        self.board: list[list[Piece | None]] = self.board_from_fen(fboard)  # starts in bottom left in rows, going up
        self.half_moves_count = int(fhalf_move)
        self.full_moves_count = int(ffull_move)
        self.white_move = w_or_b[fmove]
        self.en_passant_square: str = fEn_passant  # Might want to update this to tuple form in future
        self.castling_rights = ["K" in fcastling, "Q" in fcastling, "k" in fcastling, "q" in fcastling]
        self.past_fens: list[str] = [self.get_fen()]

    def board_from_fen(self, fboard: str) -> list[list[Piece | None]]:
        board: list[list[Piece | None]] = []
        for rank in fboard.split("/"):#
            row = []
            for file in rank:
                if file in "12345678":
                    for _ in range(int(file)):
                        row.append(None)
                else:
                    white = file.isupper()
                    pos = (len(row) + 1, 8 - len(board))
                    row.append(letter_to_class[file.lower()](pos, white))
            board.append(row)

        board = board[::-1]  # fens go top down, we want bottom up
        return board
                    
    
    def get_fen(self) -> str:
        """return fen string of current game state"""
        return DEFAULT_FEN  # Implement later
    