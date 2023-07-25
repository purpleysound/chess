import pygame
from game import Game, PIECEWISE_LEGAL_MOVES
import piece
from utils_and_constants import *
from openings import opening_explorer

BACKGROUND_COLOUR = (64, 64, 64)
CONTRASTING_COLOUR = tuple(255 - colour for colour in BACKGROUND_COLOUR)
MOVE_INDICATOR_COLOUR = (32, 196, 32)
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
CONSTANT_UI_TEXT = ["Press 'F' to print the FEN string", "Press 'L' to print the legal moves", "Press 'O' to open the opening explorer"]

class User_Interface: 
    def __init__(self):
        self.display = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = Game()
        self.pieces: list[list[DisplayPiece | None]] = self.generate_display_pieces()

    def generate_display_pieces(self):
        pieces: list[list[DisplayPiece | None]] = [[]]
        for i, rank in enumerate(self.game.board):
            for j, item in enumerate(rank):
                if item is not None:
                    pos = indices_to_pos(i, j)
                    pieces[-1].append(DisplayPiece(item, pos_to_pygame_coordinates(pos)))
                else:
                    pieces[-1].append(None)
            pieces.append([])
        pieces.pop()
        return pieces

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    print(self.game.get_fen())
                if event.key == pygame.K_l:
                    print(self.game.get_legal_moves())
                if event.key == pygame.K_o:
                    fen = opening_explorer.open_window()
                    if fen is not None and fen != "":
                        self.game = Game(fen)
                        self.pieces = self.generate_display_pieces()
    
    def update(self, event: pygame.event.Event):
        for rank in self.pieces:
            for item in rank:
                if item is not None and piece.get_piece_colour(item.piece) == self.game.white_move:
                    return_value = item.update(event)
                    self.handle_piece_update_return_value(item, return_value)

    def handle_piece_update_return_value(self, piece: 'DisplayPiece', return_value: tuple[int, int] | None):
        """Returns the piece to its original position if the move is illegal, otherwise makes the move
        return_value is the end position of the piece, or None if the piece was not moved"""
        if return_value is None:
            return
        start_pos = pygame_coordinates_to_pos(piece.start_coords)
        if self.game.legal_move_with_check_check(start_pos, return_value):
            self.make_move(start_pos, return_value)
        else:
            piece.rect.topleft = piece.start_coords

    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        self.game.make_move(start_pos, end_pos)
        self.pieces = self.generate_display_pieces()

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
                    for start_pos, end_pos in self.game.legal_moves_from_start_pos_with_check_check(pygame_coordinates_to_pos(item.start_coords)):
                        pygame.draw.circle(self.display, MOVE_INDICATOR_COLOUR, vector_add(pos_to_pygame_coordinates(end_pos), (32, 32)), 8)
                    item.draw(self.display)
                    continue
        for i, text in enumerate(self.get_display_text()):
            self.display.blit(pygame.font.SysFont("Segoe UI", 32).render(text, True, CONTRASTING_COLOUR), (0, 512 + i * 32))
        pygame.display.update()

    def get_display_text(self) -> list[str]:
        display_text = CONSTANT_UI_TEXT.copy()
        display_text.append(f"{'White' if self.game.white_move else 'Black'}'s turn")
        return display_text


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
