import pygame
from game import Game
import piece
from utils_and_constants import *

BACKGROUND_COLOUR = (64, 64, 64)
CONTRASTING_COLOUR = tuple(255 - colour for colour in BACKGROUND_COLOUR)
BOARD_IMG = pygame.image.load("images/board.png")
MOUSE_ACTIONS = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]

white_class_name_to_img = {
    piece.PAWN: pygame.transform.smoothscale(pygame.image.load("images/wP.svg"), (64, 64)),
    piece.KNIGHT: pygame.transform.smoothscale(pygame.image.load("images/wN.svg"), (64, 64)),
    piece.BISHOP: pygame.transform.smoothscale(pygame.image.load("images/wB.svg"), (64, 64)),
    piece.ROOK: pygame.transform.smoothscale(pygame.image.load("images/wR.svg"), (64, 64)),
    piece.QUEEN: pygame.transform.smoothscale(pygame.image.load("images/wQ.svg"), (64, 64)),
    piece.KING: pygame.transform.smoothscale(pygame.image.load("images/wK.svg"), (64, 64)),
}
black_class_name_to_img = {
    piece.PAWN: pygame.transform.smoothscale(pygame.image.load("images/bP.svg"), (64, 64)),
    piece.KNIGHT: pygame.transform.smoothscale(pygame.image.load("images/bN.svg"), (64, 64)),
    piece.BISHOP: pygame.transform.smoothscale(pygame.image.load("images/bB.svg"), (64, 64)),
    piece.ROOK: pygame.transform.smoothscale(pygame.image.load("images/bR.svg"), (64, 64)),
    piece.QUEEN: pygame.transform.smoothscale(pygame.image.load("images/bQ.svg"), (64, 64)),
    piece.KING: pygame.transform.smoothscale(pygame.image.load("images/bK.svg"), (64, 64)),
}
colour_to_img = {True: white_class_name_to_img, False: black_class_name_to_img}


class User_Interface: 
    def __init__(self):
        self.display = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = Game()
        self.pieces: list[list[DisplayPiece | None]] = [[]]
        for i, rank in enumerate(self.game.board):
            for j, item in enumerate(rank):
                if item is not None:
                    pos = indices_to_pos(i, j)
                    self.pieces[-1].append(DisplayPiece(item, pos_to_pygame_coordinates(pos)))
                else:
                    self.pieces[-1].append(None)
            self.pieces.append([])
        self.pieces.pop()


    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type in MOUSE_ACTIONS:
                self.update(event)
    
    def update(self, event: pygame.event.Event):
        for rank in self.pieces:
            for item in rank:
                if item is not None:
                    return_value = item.update(event)
                    self.handle_piece_update_return_value(item, return_value)

    def handle_piece_update_return_value(self, piece: "DisplayPiece", return_value: tuple[int, int] | None):
        if return_value is None:
            return
        start_pos = pygame_coordinates_to_pos(piece.start_coords)
        if self.game.legal_move(start_pos, return_value):
            self.game.make_move(start_pos, return_value)
            start_index, start_jndex = pos_to_indices(start_pos)
            end_index, end_jndex = pos_to_indices(return_value)
            self.pieces[end_index][end_jndex] = piece
            self.pieces[start_index][start_jndex] = None
            piece.rect.topleft = pos_to_pygame_coordinates(return_value)
            piece.start_coords = piece.rect.topleft

    def draw(self):
        self.display.fill(BACKGROUND_COLOUR)
        self.display.blit(BOARD_IMG, (0, 0))
        for rank in self.pieces:
            for item in rank:
                if item is not None:
                    self.display.blit(item.image, item.rect)
        for rank in self.pieces:
            for item in rank:
                if item is not None and item.held:
                    item.draw(self.display)
                    continue
        pygame.display.update()


class DisplayPiece(pygame.sprite.Sprite):
    def __init__(self, piece: int, coords: tuple[int, int]):
        super().__init__()
        self.piece = piece
        self.image: pygame.surface.Surface = self.get_image()
        self.rect: pygame.rect.Rect = self.image.get_rect(topleft=coords)
        self.held = False
        self.start_coords = coords

    def get_image(self) -> pygame.surface.Surface:
        piece_type, white, _  = piece.get_piece_attrs(self.piece)
        return colour_to_img[white][piece_type]
    
    def draw(self, display: pygame.surface.Surface):
        display.blit(self.image, self.rect) # type: ignore (pygame types are silly)

    def update(self, event: pygame.event.Event) -> tuple[int, int] | None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.held = True
                self.start_coords = self.rect.topleft
        elif event.type == pygame.MOUSEBUTTONUP and self.held:
            self.held = False
            end_pos = pygame_coordinates_to_pos(event.pos)
            if any(i not in range(1, 9) for i in end_pos):
                self.rect.topleft = self.start_coords
                return None
            return end_pos
        elif event.type == pygame.MOUSEMOTION and self.held:
            self.rect.center = event.pos


def pos_to_pygame_coordinates(tup: tuple) -> tuple[int, int]:
    # each square is 64x64, top_left is (0, 0)
    return int((tup[0] - 1) * 64), int((8 - tup[1]) * 64)

def pygame_coordinates_to_pos(tup: tuple) -> tuple[int, int]:
    # each square is 64x64, top_left is (0, 0)
    return int(tup[0] // 64 + 1), int(8 - tup[1] // 64)


if __name__ == "__main__":
    pygame.init()
    User_Interface().run()
    pygame.quit()
