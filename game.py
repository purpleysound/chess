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
        return (start_pos, end_pos) in self.get_legal_moves()
    
    def get_legal_moves(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """return list of legal moves in (start_pos, end_pos) format"""
        piecewise_legal_moves = {
            piece.PAWN: self.get_pawn_moves,
            piece.KNIGHT: self.get_knight_moves,
            piece.BISHOP: self.get_bishop_moves,
            piece.ROOK: self.get_rook_moves,
            piece.QUEEN: self.get_queen_moves,
            piece.KING: self.get_king_moves,
        }
        legal_moves = []
        for i, rank in enumerate(self.board):
            for j, item in enumerate(rank):
                if item is not None:
                    piece_type, white, moved = piece.get_piece_attrs(item)
                    if white != self.white_move:
                        continue
                    start_pos = indices_to_pos(i, j)
                    legal_moves += piecewise_legal_moves[piece_type](start_pos)
        return legal_moves
    
    def get_pawn_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        start_index, start_jndex = pos_to_indices(start_pos)
        start_piece = self.board[start_index][start_jndex]
        assert start_piece is not None
        piece_type, white, moved = piece.get_piece_attrs(start_piece)
        assert piece_type == piece.PAWN
        direction = 1 if white else -1
        ahead = vector_add(start_pos, (0, direction))
        i, j = pos_to_indices(ahead)
        if self.board[i][j] is None:
            legal_moves.append((start_pos, ahead))
            if not moved:
                ahead2 = vector_add(ahead, (0, direction))
                i, j = pos_to_indices(ahead2)
                if self.board[i][j] is None:
                    legal_moves.append((start_pos, ahead2))
        for side in [(1, direction), (-1, direction)]:
            side_pos = vector_add(start_pos, side)
            i, j = pos_to_indices(side_pos)
            if 0 <= i < 8 and 0 <= j < 8:
                side_piece = self.board[i][j]
                if side_piece is not None:
                    side_piece_type, side_white, side_moved = piece.get_piece_attrs(side_piece)
                    if side_white != white:
                        legal_moves.append((start_pos, side_pos))
                elif side_pos == self.en_passant_square:
                    legal_moves.append((start_pos, side_pos))
        return legal_moves
    
    def get_knight_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        direction_vectors = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
        for direction in direction_vectors:
            end_pos = vector_add(start_pos, direction)
            i, j = pos_to_indices(end_pos)
            if 0 <= i < 8 and 0 <= j < 8:
                end_piece = self.board[i][j]
                if end_piece is None:
                    legal_moves.append((start_pos, end_pos))
                else:
                    end_piece_type, end_white, end_moved = piece.get_piece_attrs(end_piece)
                    if end_white != self.white_move:
                        legal_moves.append((start_pos, end_pos))
        return legal_moves
    
    def get_king_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        direction_vectors = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
        for direction in direction_vectors:
            end_pos = vector_add(start_pos, direction)
            i, j = pos_to_indices(end_pos)
            if 0 <= i < 8 and 0 <= j < 8:
                end_piece = self.board[i][j]
                if end_piece is None:
                    legal_moves.append((start_pos, end_pos))
                else:
                    end_piece_type, end_white, end_moved = piece.get_piece_attrs(end_piece)
                    if end_white != self.white_move:
                        legal_moves.append((start_pos, end_pos))
        return legal_moves
        
    def get_bishop_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        direction_vectors = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for direction in direction_vectors:
            current_pos = start_pos
            while True:
                current_pos = vector_add(current_pos, direction)
                i, j = pos_to_indices(current_pos)
                if 0 <= i < 8 and 0 <= j < 8:
                    end_piece = self.board[i][j]
                    if end_piece is None:
                        legal_moves.append((start_pos, current_pos))
                    else:
                        end_piece_type, end_white, end_moved = piece.get_piece_attrs(end_piece)
                        if end_white != self.white_move:
                            legal_moves.append((start_pos, current_pos))
                        break
                else:
                    break
        return legal_moves
    
    def get_rook_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        direction_vectors = [(1, 0), (0, 1), (0, -1), (-1, 0)]
        for direction in direction_vectors:
            current_pos = start_pos
            while True:
                current_pos = vector_add(current_pos, direction)
                i, j = pos_to_indices(current_pos)
                if 0 <= i < 8 and 0 <= j < 8:
                    end_piece = self.board[i][j]
                    if end_piece is None:
                        legal_moves.append((start_pos, current_pos))
                    else:
                        end_piece_type, end_white, end_moved = piece.get_piece_attrs(end_piece)
                        if end_white != self.white_move:
                            legal_moves.append((start_pos, current_pos))
                        break
                else:
                    break
        return legal_moves
    
    def get_queen_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        return self.get_bishop_moves(start_pos) + self.get_rook_moves(start_pos)
    
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
