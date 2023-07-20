from utils_and_constants import *

"""
Classes here should only be concerned about themselves
if something needs to be done to the board, it should be done in game.py
"""

class Piece:
    def __init__(self, position: tuple, white: bool) -> None:
        assert len(position) == 2 and all(i in range(1, 9) for i in position)
        self.position = position
        self.white = white
        self.moved = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.position}, {self.white})"


class Pawn(Piece):
    def __init__(self, position: tuple, white: bool) -> None:
        super().__init__(position, white)


class Knight(Piece):
    def __init__(self, position: tuple, white: bool) -> None:
        super().__init__(position, white)


class Bishop(Piece):
    def __init__(self, position: tuple, white: bool) -> None:
        super().__init__(position, white)


class Rook(Piece):
    def __init__(self, position: tuple, white: bool) -> None:
        super().__init__(position, white)


class Queen(Piece):
    def __init__(self, position: tuple, white: bool) -> None:
        super().__init__(position, white)


class King(Piece):
    def __init__(self, position: tuple, white: bool) -> None:
        super().__init__(position, white)

