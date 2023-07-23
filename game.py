import piece
from utils_and_constants import *

DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
w_or_b = {"w": True, "b": False}
letter_to_class = {"p": piece.PAWN, "n": piece.KNIGHT, "b": piece.BISHOP, "r": piece.ROOK, "q": piece.QUEEN, "k": piece.KING}
piece_to_letter = {piece.PAWN: "p", piece.KNIGHT: "n", piece.BISHOP: "b", piece.ROOK: "r", piece.QUEEN: "q", piece.KING: "k"}

class Game:
    def __init__(self, fen: str = DEFAULT_FEN):
        fboard, fmove, fcastling, fEn_passant, fhalf_move, ffull_move = fen.split(" ")
        self.board: list[list[int | None]] = self.board_from_fen(fboard)  # starts in bottom left in rows, going up
        self.half_moves_count = int(fhalf_move)
        self.full_moves_count = int(ffull_move)
        self.white_move = w_or_b[fmove]
        self.en_passant_square: tuple[int, int] | None = notation_to_pos(fEn_passant) if fEn_passant != "-" else None
        self.castling_rights = ["K" in fcastling, "Q" in fcastling, "k" in fcastling, "q" in fcastling]

    def board_from_fen(self, fboard: str) -> list[list[int | None]]:
        board: list[list[int | None]] = []
        for rank in fboard.split("/"):
            row = []
            for file in rank:
                if file in "12345678":
                    for _ in range(int(file)):
                        row.append(None)
                else:
                    white = file.isupper()
                    row.append(piece.generate_piece(letter_to_class[file.lower()], white))
            board.append(row)

        board = board[::-1]  # fens go top down, we want bottom up
        return board
                    
    
    def get_fen(self) -> str:
        """return fen string of current game state"""
        fen = ""
        blank_count = 0
        for rank in self.board[::-1]:
            for item in rank:
                if item is None:
                    blank_count += 1
                else:
                    if blank_count > 0:
                        fen += str(blank_count)
                        blank_count = 0
                    piece_type, white, moved = piece.get_piece_attrs(item)
                    fen += piece_to_letter[piece_type].upper() if white else piece_to_letter[piece_type]
            if blank_count > 0:
                fen += str(blank_count)
                blank_count = 0
            fen += "/"
        fen = fen[:-1]  # remove last slash
        fen += " "
        fen += "w" if self.white_move else "b"
        fen += " "
        castling = ""
        if self.castling_rights[0]:
            castling += "K"
        if self.castling_rights[1]:
            castling += "Q"
        if self.castling_rights[2]:
            castling += "k"
        if self.castling_rights[3]:
            castling += "q"
        if castling == "":
            castling = "-"
        fen += castling
        fen += " "
        if self.en_passant_square:
            fen += pos_to_notation(self.en_passant_square)
        else:
            fen += "-"
        fen += " "
        fen += str(self.half_moves_count)
        fen += " "
        fen += str(self.full_moves_count)
        return fen
 
    def legal_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        return start_pos != end_pos
    
    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        """make a move in algebraic notation"""
        start_index, start_jndex = pos_to_indices(start_pos)
        end_index, end_jndex = pos_to_indices(end_pos)
        start_piece = self.board[start_index][start_jndex]
        assert start_piece is not None
        start_piece = piece.update_moved_bit(start_piece)
        self.board[start_index][start_jndex] = None
        self.board[end_index][end_jndex] = start_piece
        self.half_moves_count += 1
        if not self.white_move:
            self.full_moves_count += 1
        self.white_move = not self.white_move
