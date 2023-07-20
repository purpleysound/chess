from pygame import Vector2

"""
Classes here should only be concerned about themselves
if something needs to be done to the board, it should be done in game.py
"""

class Piece:
    def __init__(self, position: Vector2, white: bool) -> None:
        assert position.x in range(1, 9) and position.y in range(1, 9)
        self.position = position
        self.white = white
        self.moved = False


class Pawn(Piece):
    def __init__(self, position: Vector2, white: bool) -> None:
        super().__init__(position, white)


class Knight(Piece):
    def __init__(self, position: Vector2, white: bool) -> None:
        super().__init__(position, white)


class Bishop(Piece):
    def __init__(self, position: Vector2, white: bool) -> None:
        super().__init__(position, white)


class Rook(Piece):
    def __init__(self, position: Vector2, white: bool) -> None:
        super().__init__(position, white)


class Queen(Piece):
    def __init__(self, position: Vector2, white: bool) -> None:
        super().__init__(position, white)


class King(Piece):
    def __init__(self, position: Vector2, white: bool) -> None:
        super().__init__(position, white)

