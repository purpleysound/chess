import pygame
from game import Game
from utils_and_constants import *

BACKGROUND_COLOUR = (64, 64, 64)
CONTRASTING_COLOUR = tuple(255 - colour for colour in BACKGROUND_COLOUR)
BOARD_IMG = pygame.image.load("images/board.png")
white_class_name_to_img = {
    "Pawn": pygame.transform.smoothscale(pygame.image.load("images/wP.svg"), (64, 64)),
    "Knight": pygame.transform.smoothscale(pygame.image.load("images/wN.svg"), (64, 64)),
    "Bishop": pygame.transform.smoothscale(pygame.image.load("images/wB.svg"), (64, 64)),
    "Rook": pygame.transform.smoothscale(pygame.image.load("images/wR.svg"), (64, 64)),
    "Queen": pygame.transform.smoothscale(pygame.image.load("images/wQ.svg"), (64, 64)),
    "King": pygame.transform.smoothscale(pygame.image.load("images/wK.svg"), (64, 64)),
}
black_class_name_to_img = {
    "Pawn": pygame.transform.smoothscale(pygame.image.load("images/bP.svg"), (64, 64)),
    "Knight": pygame.transform.smoothscale(pygame.image.load("images/bN.svg"), (64, 64)),
    "Bishop": pygame.transform.smoothscale(pygame.image.load("images/bB.svg"), (64, 64)),
    "Rook": pygame.transform.smoothscale(pygame.image.load("images/bR.svg"), (64, 64)),
    "Queen": pygame.transform.smoothscale(pygame.image.load("images/bQ.svg"), (64, 64)),
    "King": pygame.transform.smoothscale(pygame.image.load("images/bK.svg"), (64, 64)),
}
colour_to_img = {True: white_class_name_to_img, False: black_class_name_to_img}


class User_Interface: 
    def __init__(self):
        self.display = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = Game()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self):
        pass

    def draw(self):
        self.display.fill(BACKGROUND_COLOUR)
        self.display.blit(BOARD_IMG, (0, 0))
        for rank in self.game.board:
            for piece in rank:
                if piece is not None:
                    self.display.blit(colour_to_img[piece.white][piece.__class__.__name__], self.tuple_to_coordinates(piece.position))
        pygame.display.update()

    @staticmethod
    def tuple_to_coordinates(tup: tuple) -> tuple[int, int]:
        # each square is 64x64, top_left is (0, 0)
        return int((tup[0] - 1) * 64), int((8 - tup[1]) * 64)


if __name__ == "__main__":
    pygame.init()
    User_Interface().run()
    pygame.quit()
