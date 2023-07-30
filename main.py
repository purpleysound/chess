import pygame
from game import Game
import piece
from utils_and_constants import *
from openings import opening_explorer
import engine

def load_image(path: str, size: tuple[int, int]) -> pygame.surface.Surface:
    image = pygame.image.load(path)
    try:
        image = pygame.transform.smoothscale(image, size)
    except ValueError:
        image = pygame.transform.scale(image, size)
    return image

BACKGROUND_COLOUR = (64, 64, 64)
CONTRASTING_COLOUR = tuple(255 - colour for colour in BACKGROUND_COLOUR)
MOVE_INDICATOR_COLOUR = (32, 196, 32)
BOARD_IMG = load_image("images/board.png", (512, 512))
MOUSE_ACTIONS = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]
DEFAULT_ENGINE_DEPTH = 3
FONT_SIZE = 28

white_class_name_to_img = {
    piece.PAWN: load_image("images/wP.svg", (64, 64)),
    piece.KNIGHT: load_image("images/wN.svg", (64, 64)),
    piece.BISHOP: load_image("images/wB.svg", (64, 64)),
    piece.ROOK: load_image("images/wR.svg", (64, 64)),
    piece.QUEEN: load_image("images/wQ.svg", (64, 64)),
    piece.KING: load_image("images/wK.svg", (64, 64)),
}
black_class_name_to_img = {
    piece.PAWN: load_image("images/bP.svg", (64, 64)),
    piece.KNIGHT: load_image("images/bN.svg", (64, 64)),
    piece.BISHOP: load_image("images/bB.svg", (64, 64)),
    piece.ROOK: load_image("images/bR.svg", (64, 64)),
    piece.QUEEN: load_image("images/bQ.svg", (64, 64)),
    piece.KING: load_image("images/bK.svg", (64, 64)),
}
colour_to_img = {True: white_class_name_to_img, False: black_class_name_to_img}
UI_TEXT = {
    0: ["1. GUI Settings", "2. Import/Export", "3. Engine", "4. Debug"],
    1: ["0. Home", "B. Flip Board", "P. Personalisation Settings"],
    2: ["0. Home", "F. Print FEN To Console", "C. Copy FEN To Clipboard", "V. Paste FEN From Clipboard", "O. Open Opening Explorer", "I. Open Endgame Scenarios", "Home. Load Start Position", "End. Clear Board"],
    3: ["0. Home", "M. Print Engine Move To Console", "S. Start/Stop Playing Against Engine (Engine's move when enabled)", "E. Start/Stop Deep Engine Analysis"],
    4: ["0. Home", "L. Print Legal Moves To Console"]
}

class UserInterface: 
    def __init__(self):
        self.display = pygame.display.set_mode((800, 800))
        pygame.scrap.init()  # has to be initialised after display created
        self.clock = pygame.time.Clock()
        self.running = True
        self.flipped = False
        self.auto_flip = False

        self.game = Game()
        self.pieces: list[list[DisplayPiece | None]] = self.generate_display_pieces()

        self.ui_text_mode = 0
        self.engine_mode = False
        self.engine_playing = False
        self.background_engine = None

    def generate_display_pieces(self):
        pieces: list[list[DisplayPiece | None]] = [[]]
        for i, rank in enumerate(self.game.board):
            for j, item in enumerate(rank):
                if item is not None:
                    pos = indices_to_pos(i, j)
                    pieces[-1].append(DisplayPiece(item, pos_to_pygame_coordinates(pos), flipped=self.flipped))
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
                if self.background_engine is not None:
                    self.background_engine.running = False
                self.running = False
            if event.type in MOUSE_ACTIONS:
                self.update(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.flip()
                if event.key == pygame.K_a:
                    self.auto_flip = not self.auto_flip
                if event.key == pygame.K_f:
                    print(self.game.get_fen())
                if event.key == pygame.K_c:
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.game.get_fen().encode())
                if event.key == pygame.K_v:
                    self.load_fen(pygame.scrap.get(pygame.SCRAP_TEXT).decode()[:-4])
                if event.key == pygame.K_l:
                    print(self.game.get_legal_moves())
                if event.key == pygame.K_o:
                    fen = opening_explorer.open_window()
                    if fen is not None and fen != "":
                        self.load_fen(fen)
                if event.key == pygame.K_HOME:
                    self.load_fen(DEFAULT_FEN)
                if event.key == pygame.K_END:
                    self.load_fen("8/8/8/8/8/8/8/8 w - - 0 1")
                if event.key == pygame.K_m:
                    print(engine.get_value_and_best_move(self.game, DEFAULT_ENGINE_DEPTH))
                if event.key == pygame.K_s:
                    self.engine_mode = not self.engine_mode
                    self.engine_playing = True
                    if self.engine_mode:
                        self.make_engine_move()
                if event.key == pygame.K_e:
                    if self.background_engine is None:
                        self.background_engine = engine.Engine(self.game.copy())
                    else:
                        self.background_engine.running = False
                        self.background_engine = None
                if event.key == pygame.K_0:
                    self.ui_text_mode = 0
                if event.key == pygame.K_1:
                    self.ui_text_mode = 1
                if event.key == pygame.K_2:
                    self.ui_text_mode = 2
                if event.key == pygame.K_3:
                    self.ui_text_mode = 3
                if event.key == pygame.K_4:
                    self.ui_text_mode = 4
    
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
        start_pos = pygame_coordinates_to_pos(piece.start_coords, flipped=self.flipped)
        if self.game.legal_move_with_check_check(start_pos, return_value):
            self.make_move(start_pos, return_value)
        else:
            piece.rect.topleft = piece.start_coords

    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        self.game.make_move(start_pos, end_pos)
        self.pieces = self.generate_display_pieces()
        if self.engine_mode:
            self.draw()  # looks kinda ugly without
            self.make_engine_move()
        if self.background_engine is not None:
            self.background_engine.running = False
            self.background_engine = engine.Engine(self.game.copy())
        if self.auto_flip:
            if self.game.white_move == self.flipped:
                self.flip()

    def make_engine_move(self):
        self.engine_playing = not self.engine_playing
        if self.engine_playing:
            evaluation, best_move = engine.get_value_and_best_move(self.game, DEFAULT_ENGINE_DEPTH)
            if best_move is None or not (self.game.get_game_state() == GameState.ONGOING):
                print("No legal moves")
                return
            self.make_move(*best_move)

    def load_fen(self, fen: str):
        self.game = Game(fen)
        self.pieces = self.generate_display_pieces()

    def flip(self):
        self.flipped = not self.flipped
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
                    for start_pos, end_pos in self.game.legal_moves_from_start_pos_with_check_check(pygame_coordinates_to_pos(item.start_coords, flipped=self.flipped)):
                        pygame.draw.circle(self.display, MOVE_INDICATOR_COLOUR, vector_add(pos_to_pygame_coordinates(end_pos, flipped=self.flipped), (32, 32)), 8)
                    item.draw(self.display)
                    continue
        for i, text in enumerate(self.get_display_text()):
            self.display.blit(pygame.font.SysFont("Segoe UI", FONT_SIZE).render(text, True, CONTRASTING_COLOUR), (0, 512 + i * FONT_SIZE))
        pygame.display.update()

    def get_display_text(self) -> list[str]:
        display_text = UI_TEXT[self.ui_text_mode].copy()
        if self.ui_text_mode == 0:
            display_text.append(f"{'White' if self.game.white_move else 'Black'}'s turn")
        if self.ui_text_mode == 1:
            display_text.append(f"A. Auto-Flip: {'Enabled' if self.auto_flip else 'Disabled'}")
        if self.ui_text_mode == 3:
            if self.background_engine is not None:
                display_text.append(f"Engine at depth {self.background_engine.depth}")
                if self.background_engine.best_move is not None:
                    display_text.append(f"Best move {pos_move_to_uci(self.background_engine.best_move)}")
        if self.ui_text_mode == 4:
            for key in self.game.__dict__:
                display_text.append(f"{key}: {self.game.__dict__[key]}")
            display_text.append(f"Game State: {STATE_TO_STR[self.game.get_game_state()]}")
        return display_text


class DisplayPiece(pygame.sprite.Sprite):
    def __init__(self, piece: int, coords: tuple[int, int], flipped: bool = False):
        super().__init__()
        self.piece = piece
        self.image: pygame.surface.Surface = self.get_image()
        self.rect: pygame.rect.Rect = self.image.get_rect(topleft=coords)
        self.flipped = flipped
        if self.flipped:
            self.flip()
        self.held = False
        self.start_coords = coords

    def get_image(self) -> pygame.surface.Surface:
        piece_type, white  = piece.get_piece_attrs(self.piece)
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
            end_pos = pygame_coordinates_to_pos(event.pos, flipped=self.flipped)
            if any(i not in range(1, 9) for i in end_pos):
                self.rect.topleft = self.start_coords
                return None
            return end_pos
        elif event.type == pygame.MOUSEMOTION and self.held:
            self.rect.center = event.pos

    def flip(self):
        self.rect.topleft = pos_to_pygame_coordinates(pygame_coordinates_to_pos(self.rect.topleft), flipped=True)


def pos_to_pygame_coordinates(tup: tuple, flipped: bool = False) -> tuple[int, int]:
    # each square is 64x64, top_left is (0, 0)
    if flipped:
        return int((8 - tup[0]) * 64), int((tup[1] - 1) * 64)
    return int((tup[0] - 1) * 64), int((8 - tup[1]) * 64)

def pygame_coordinates_to_pos(tup: tuple, flipped: bool = False) -> tuple[int, int]:
    # each square is 64x64, top_left is (0, 0)
    if flipped:
        return int(8 - tup[0] // 64), int(tup[1] // 64 + 1)
    return int(tup[0] // 64 + 1), int(8 - tup[1] // 64)


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Chess")
    UserInterface().run()
    pygame.quit()
