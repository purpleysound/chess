from pieces import Piece

DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class Game:
    def __init__(self, fen: str = DEFAULT_FEN):
        self.board: list[list[Piece | None]] = self.board_from_fen(fen)
        self.move_rule_count = 0
        self.white_move = True
        self.en_passant_square = None
        self.castling_rights = [True, True, True, True]
        self.past_fens: list[str] = [self.get_fen()]

    def board_from_fen(self, fen: str) -> list[list[Piece | None]]:
        raise NotImplementedError
    
    def get_fen(self) -> str:
        """return fen string of current game state"""
        return DEFAULT_FEN  # Implement later
    