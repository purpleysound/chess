import piece
from utils_and_constants import *

DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
w_or_b = {"w": True, "b": False}
letter_to_class = {"p": piece.PAWN, "n": piece.KNIGHT, "b": piece.BISHOP, "r": piece.ROOK, "q": piece.QUEEN, "k": piece.KING}
piece_to_letter = {piece.PAWN: "p", piece.KNIGHT: "n", piece.BISHOP: "b", piece.ROOK: "r", piece.QUEEN: "q", piece.KING: "k"}

class Game:
    def __init__(self, fen: str = DEFAULT_FEN):
        self.en_passant_square = None
        self.half_moves_count = 0
        self.full_moves_count = 1  # in case fen doesn't have these, this might not be accurate but should affect anything too much
        try:
            fen_list = fen.split(" ")
            self.board: list[list[int | None]] = self.board_from_fen(fen_list.pop(0))  # starts in bottom left in rows, going up
            self.white_move = w_or_b[fen_list.pop(0)]
            fcastling = fen_list.pop(0)
            self.castling_rights = ["K" in fcastling, "Q" in fcastling, "k" in fcastling, "q" in fcastling]
            fEn_passant = fen_list.pop(0)
            self.en_passant_square: tuple[int, int] | None = notation_to_pos(fEn_passant) if fEn_passant != "-" else None
            self.half_moves_count = int(fen_list.pop(0))
            self.full_moves_count = int(fen_list.pop(0))
        except IndexError:
            pass

    def copy(self) -> 'Game':
        copy = Game()
        copy.board = [rank[:] for rank in self.board]
        copy.white_move = self.white_move
        copy.castling_rights = self.castling_rights[:]
        copy.en_passant_square = self.en_passant_square
        copy.half_moves_count = self.half_moves_count
        copy.full_moves_count = self.full_moves_count
        return copy
    
    def get_piece_from_pos(self, pos: tuple[int, int]) -> int | None:
        i, j = pos_to_indices(pos)
        return self.board[i][j]

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
        start_piece = self.get_piece_from_pos(start_pos)
        assert start_piece is not None
        piece_type = piece.get_piece_type(start_piece)
        legal_moves = PIECEWISE_LEGAL_MOVES[piece_type](self, start_pos)
        return (start_pos, end_pos) in legal_moves
    
    def get_legal_moves(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """return list of legal moves in (start_pos, end_pos) format"""
        legal_moves = []
        for i, rank in enumerate(self.board):
            for j, item in enumerate(rank):
                if item is not None:
                    piece_type, white, moved = piece.get_piece_attrs(item)
                    if white != self.white_move:
                        continue
                    start_pos = indices_to_pos(i, j)
                    legal_moves += PIECEWISE_LEGAL_MOVES[piece_type](self, start_pos)
        return legal_moves
    
    def not_in_check_after_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        game_copy = self.copy()
        game_copy.make_move(start_pos, end_pos)
        for move in game_copy.get_legal_moves():
            response_destination = game_copy.get_piece_from_pos(move[1])
            if response_destination is not None:
                piece_type = piece.get_piece_type(response_destination)
                if piece_type == piece.KING:
                    return False
        return True
    
    def get_legal_moves_with_check_check(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        for move in self.get_legal_moves():
            if self.not_in_check_after_move(*move):
                legal_moves.append(move)
        return legal_moves
    
    def legal_moves_from_start_pos(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        start_piece = self.get_piece_from_pos(start_pos)
        assert start_piece is not None
        piece_type = piece.get_piece_type(start_piece)
        legal_moves = PIECEWISE_LEGAL_MOVES[piece_type](self, start_pos)
        return legal_moves
        
    def legal_moves_from_start_pos_with_check_check(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = self.legal_moves_from_start_pos(start_pos)
        for move in legal_moves[:]:  # Need to use copy as items might be removed from list
            if not self.not_in_check_after_move(*move):
                legal_moves.remove(move)
        return legal_moves
    
    def legal_move_with_check_check(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        start_piece = self.get_piece_from_pos(start_pos)
        assert start_piece is not None
        piece_type = piece.get_piece_type(start_piece)
        legal_moves = PIECEWISE_LEGAL_MOVES[piece_type](self, start_pos)
        for move in legal_moves[:]:  # Need to use copy as items might be removed from list
            if not self.not_in_check_after_move(*move):
                legal_moves.remove(move)
        return (start_pos, end_pos) in legal_moves
    
    def get_pawn_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        legal_moves = []
        start_piece = self.get_piece_from_pos(start_pos)
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
                    side_white = piece.get_piece_colour(side_piece)
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
                    end_white = piece.get_piece_colour(end_piece)
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
                    end_white = piece.get_piece_colour(end_piece)
                    if end_white != self.white_move:
                        legal_moves.append((start_pos, end_pos))
                        
        king = self.get_piece_from_pos(start_pos)
        assert king is not None
        piece_type, piece_white, piece_moved = piece.get_piece_attrs(king)
        if not piece_moved:
            if piece_white:
                if self.castling_rights[0]:
                    legal_moves += self.check_castling(start_pos, (8, 1), [(7, 1), (6, 1)])
                if self.castling_rights[1]:
                    legal_moves += self.check_castling(start_pos, (1, 1), [(2, 1), (3, 1), (4, 1)])
            else:
                if self.castling_rights[2]:
                    legal_moves += self.check_castling(start_pos, (8, 8), [(7, 8), (6, 8)])
                if self.castling_rights[3]:
                    legal_moves += self.check_castling(start_pos, (1, 8), [(2, 8), (3, 8), (4, 8)])
        return legal_moves
    
    def check_castling(self, start_pos, rook_pos, in_between_posses) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """The arguments of this function are kind of weird but i just had too many repeated nested for loops with the arguments
        in the get_king_moves function so i think it makes the most sense here"""
        legal_moves = []
        rook = self.get_piece_from_pos(rook_pos)
        assert rook is not None
        rook_moved = piece.get_piece_moved(rook)
        if not rook_moved:
            in_between_indices = [pos_to_indices(pos) for pos in in_between_posses]
            in_between_pieces = [self.board[i][j] for i, j in in_between_indices]
            if all(piece is None for piece in in_between_pieces):
                direction = 1 if rook_pos[0] > start_pos[0] else -1
                if self.not_in_check_after_move(start_pos, vector_add(start_pos, (direction, 0))) and self.not_in_check_after_move(start_pos, start_pos):
                    """This is an odd idea because this is the only time we check if we are in check in the non-check_check functions
                    however, since you can't castle through check it is actually necessary here rather than in the rest of the cases
                    where we are only checking it for the user in seperate functions and leaving 'pseudo-legal' moves for the engine to use"""
                    legal_moves.append((start_pos, vector_add(start_pos, (2*direction, 0))))
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
                        end_white = piece.get_piece_colour(end_piece)
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
                        end_white = piece.get_piece_colour(end_piece)
                        if end_white != self.white_move:
                            legal_moves.append((start_pos, current_pos))
                        break
                else:
                    break
        return legal_moves
    
    def get_queen_moves(self, start_pos: tuple[int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        return self.get_bishop_moves(start_pos) + self.get_rook_moves(start_pos)
    
    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int], promotion_piece: int = piece.QUEEN):
        start_index, start_jndex = pos_to_indices(start_pos)
        end_index, end_jndex = pos_to_indices(end_pos)
        start_piece = self.board[start_index][start_jndex]
        assert start_piece is not None
        start_piece = piece.update_moved_bit(start_piece)
        self.board[start_index][start_jndex] = None
        if self.board[end_index][end_jndex] is not None:
            self.half_moves_count = -1
        self.board[end_index][end_jndex] = start_piece
        self.half_moves_count += 1
        if not self.white_move:
            self.full_moves_count += 1
        self.white_move = not self.white_move

        piece_type, piece_white, piece_moved = piece.get_piece_attrs(start_piece)
        if piece_type == piece.PAWN and end_pos == self.en_passant_square:
            pawn_to_take_pos = end_pos[0], start_pos[1]
            i, j = pos_to_indices(pawn_to_take_pos)
            self.board[i][j] = None
        self.en_passant_square = None

        if piece_type == piece.PAWN:
            self.half_moves_count = 0
            if abs(start_pos[1] - end_pos[1]) == 2:
                self.en_passant_square = vector_add(start_pos, (0, 1 if piece_white else -1))

            if (end_pos[1] == 1 or end_pos[1] == 8):
                self.board[end_index][end_jndex] = piece.generate_piece(promotion_piece, piece_white, True)

        if piece_type == piece.KING and abs(start_pos[0] - end_pos[0]) == 2:
            if end_pos[0] == 7:
                rook_start_pos = (8, 1)
                rook_start_i, rook_start_j = pos_to_indices(rook_start_pos)
                rook_end_pos = (6, 1)
                rook_end_i, rook_end_j = pos_to_indices(rook_end_pos)
                rook = self.board[rook_start_i][rook_start_j]
                assert rook is not None
                rook = piece.update_moved_bit(rook)
                self.board[rook_start_i][rook_start_j] = None
                self.board[rook_end_i][rook_end_j] = rook
            elif end_pos[0] == 3:
                rook_start_pos = (1, 1)
                rook_start_i, rook_start_j = pos_to_indices(rook_start_pos)
                rook_end_pos = (4, 1)
                rook_end_i, rook_end_j = pos_to_indices(rook_end_pos)
                rook = self.board[rook_start_i][rook_start_j]
                assert rook is not None
                rook = piece.update_moved_bit(rook)
                self.board[rook_start_i][rook_start_j] = None
                self.board[rook_end_i][rook_end_j] = rook

        if piece_type == piece.KING:
            if piece_white:
                self.castling_rights[0] = False
                self.castling_rights[1] = False
            else:
                self.castling_rights[2] = False
                self.castling_rights[3] = False
        if piece_type == piece.ROOK:
            if start_pos == (8, 1):
                self.castling_rights[0] = False
            elif start_pos == (1, 1):
                self.castling_rights[1] = False
            elif start_pos == (8, 8):
                self.castling_rights[2] = False
            elif start_pos == (1, 8):
                self.castling_rights[3] = False


PIECEWISE_LEGAL_MOVES = {
    piece.PAWN: Game.get_pawn_moves,
    piece.KNIGHT: Game.get_knight_moves,
    piece.BISHOP: Game.get_bishop_moves,
    piece.ROOK: Game.get_rook_moves,
    piece.QUEEN: Game.get_queen_moves,
    piece.KING: Game.get_king_moves,
}
