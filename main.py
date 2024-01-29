import pygame
from game import Game
import piece
from utils_and_constants import *
from openings import opening_explorer
import engine
import personalisation_settings
import scenario_creator
# import requests

def load_image(path: str, size: tuple[int, int]) -> pygame.surface.Surface:
    image = pygame.image.load(path)
    try:
        image = pygame.transform.smoothscale(image, size)
    except ValueError:
        image = pygame.transform.scale(image, size)
    return image

SERVER_URL = "localhost:5000"
BOARD_IMG = load_image(preferences[Prefs.BOARD_IMAGE], (512, 512))
MOUSE_ACTIONS = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]
pygame.font.init()
FONT = pygame.font.SysFont("Segoe UI", preferences[Prefs.FONT_SIZE])

UI_TEXT = {
    0: ["1. GUI Settings", "2. Import/Export", "3. Engine", "4. Debug"],
    1: ["0. Home", "B. Flip Board", "P. Personalisation Settings", "Left Arrow. Back", "Right Arrow. Forward"],
    2: ["0. Home", "F. Print FEN To Console", "C. Copy FEN To Clipboard", "V. Paste FEN From Clipboard", "O. Open Opening Explorer", "I. Open Endgame Scenarios", "Home. Load Start Position", "End. Clear Board"],
    3: ["0. Home", "M. Print Engine Move To Console", "S. Start/Stop Playing Against Engine (Engine's move when enabled)", "E. Start/Stop Deep Engine Analysis", "Z. Deep Server Analysis"],
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
        self.state = GameState.WHITE_TURN
        self.engine_mode = False
        self.engine_playing = False
        self.background_engine = None

        self.list_of_FENs: list[str | None] = [self.game.get_fen()]
        self.move_list = MoveList()

    def get_current_list_of_FENs_idx(self) -> int:
        return 2*self.game.get_full_moves_count() + (not self.game.get_white_move()) - 2

    def generate_display_pieces(self):
        pieces: list[list[DisplayPiece | None]] = [[]]
        for i, rank in enumerate(self.game.get_board()):
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
                if event.type == pygame.MOUSEMOTION or event.button == 1:
                    self.update(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.flip()
                if event.key == pygame.K_a:
                    self.auto_flip = not self.auto_flip
                if event.key == pygame.K_p:
                    personalisation_settings.open_window()
                if event.key == pygame.K_LEFT:
                    self.scroll_through_game(True)
                if event.key == pygame.K_RIGHT:
                    self.scroll_through_game(False)
                if event.key == pygame.K_f:
                    print(self.game.get_fen())
                if event.key == pygame.K_c:
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.game.get_fen().encode())
                if event.key == pygame.K_v:
                    try:
                        self.load_fen(pygame.scrap.get(pygame.SCRAP_TEXT).decode()[:-4])
                    except:
                        print("Invalid FEN string, make sure it was copied correctly")
                if event.key == pygame.K_l:
                    print(self.game.get_legal_moves())
                if event.key == pygame.K_o:
                    fen = opening_explorer.open_window()
                    if fen is not None and fen != "":
                        self.load_fen(fen)
                if event.key == pygame.K_i:
                    fen = scenario_creator.main()
                    if fen is not None and fen != "":
                        self.load_fen(fen)
                if event.key == pygame.K_HOME:
                    self.load_fen(DEFAULT_FEN)
                if event.key == pygame.K_END:
                    self.load_fen("8/8/8/8/8/8/8/8 w - - 0 1")
                if event.key == pygame.K_m:
                    print(engine.get_value_and_best_move(self.game, preferences[Prefs.DEFAULT_ENGINE_DEPTH]))
                if event.key == pygame.K_s:
                    self.engine_mode = not self.engine_mode
                    self.engine_playing = False
                    if self.engine_mode:
                        self.make_engine_move()
                if event.key == pygame.K_e:
                    if self.background_engine is None:
                        self.background_engine = engine.Engine(self.game.copy())
                    else:
                        self.background_engine.running = False
                        self.background_engine = None
                if event.key == pygame.K_z:
                    try:
                        fen = self.game.get_fen()
                        fen = fen.replace(" ", "%20")
                        fen = fen.replace("/", "=")
                        queryparams = {"d": str(preferences[Prefs.DEFAULT_ENGINE_DEPTH] + 1)}
                        response = requests.get(f"http://{SERVER_URL}/chess/{fen}", params=queryparams)
                        print(response.json())
                    except Exception as e:
                        print(e)
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
                if item is not None and piece.get_piece_colour(item.piece) == self.game.get_white_move():
                    return_value = item.update(event)
                    self.handle_piece_update_return_value(item, return_value)

    def handle_piece_update_return_value(self, piece: 'DisplayPiece', return_value: tuple[int, int] | None):
        """Returns the piece to its original position if the move is illegal, otherwise makes the move
        return_value is the end position of the piece, or None if the piece was not moved"""
        if return_value is None:
            return
        start_pos = pygame_coordinates_to_pos(piece.start_coords, flipped=self.flipped)
        if self.state not in ENDED_STATES and self.game.legal_move_with_check_check(start_pos, return_value):
            self.make_move(start_pos, return_value)
        else:
            piece.rect.topleft = piece.start_coords

    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        self.game.make_move(start_pos, end_pos)
        self.pieces = self.generate_display_pieces()
        self.list_of_FENs = self.list_of_FENs[0:self.get_current_list_of_FENs_idx()]
        self.move_list.crop(self.get_current_list_of_FENs_idx())
        self.move_list.append(pos_move_to_uci((start_pos, end_pos)))
        self.move_list.set_current_idx(self.get_current_list_of_FENs_idx()-1)
        self.list_of_FENs.append(self.game.get_fen())

        if self.check_threefold_repetition():
            self.state = GameState.DRAW
        else:
            self.state = self.game.get_game_state()

        if self.engine_mode:
            self.draw()  # looks kinda ugly without
            self.make_engine_move()
        if self.background_engine is not None:
            self.background_engine.running = False
            self.background_engine = engine.Engine(self.game.copy())

        if self.auto_flip:
            if self.game.get_white_move() == self.flipped:
                self.flip()
        

    def make_engine_move(self):
        try:
            self.engine_playing = not self.engine_playing
            if self.engine_playing:
                evaluation, best_move = engine.get_value_and_best_move(self.game, preferences[Prefs.DEFAULT_ENGINE_DEPTH])
                if best_move is None or self.state in ENDED_STATES:
                    print("No legal moves")
                    return
                self.make_move(*best_move)
        except Exception as e:
            print(f"Unable to make engine move: {e}")
            self.engine_playing = False
            self.engine_mode = False

    def load_fen(self, fen: str, reset_list_of_FENs: bool = True):
        self.game = Game(fen)
        self.pieces = self.generate_display_pieces()
        self.state = self.game.get_game_state()
        if reset_list_of_FENs:
            self.list_of_FENs = [self.game.get_fen()]
            self.move_list = MoveList()
            while self.get_current_list_of_FENs_idx() != len(self.list_of_FENs) - 1:
                self.list_of_FENs.insert(0, None)  # make sure current_idx is correct
                self.move_list.prepend("--")
            self.move_list.prepend("--")
            self.move_list.prepend("--")
        self.move_list.set_current_idx(self.get_current_list_of_FENs_idx()-1)

    def scroll_through_game(self, left: bool):
        if left:
            new_idx = self.get_current_list_of_FENs_idx() - 1
        else:
            new_idx = self.get_current_list_of_FENs_idx() + 1
        if 0 <= new_idx < len(self.list_of_FENs):
            if self.list_of_FENs[new_idx] is None:
                return
            else:
                self.load_fen(self.list_of_FENs[new_idx], reset_list_of_FENs=False) # type: ignore (we know it's not None)

    def flip(self):
        self.flipped = not self.flipped
        self.pieces = self.generate_display_pieces()

    def draw(self):
        self.display.fill(preferences[Prefs.BACKGROUND_COLOUR])
        self.display.blit(BOARD_IMG, (0, 0))
        self.move_list.draw(self.display)
        for i, text in enumerate(self.get_display_text()):
            self.display.blit(FONT.render(text, True, preferences[Prefs.CONTRASTING_COLOUR]), (0, 512 + i * preferences[Prefs.FONT_SIZE]))
        for rank in self.pieces:
            for item in rank:
                if item is not None:
                    self.display.blit(item.image, item.rect)
        for rank in self.pieces:
            for item in rank:
                if item is not None and item.held:
                    if self.state not in ENDED_STATES:
                        for start_pos, end_pos in self.game.legal_moves_from_start_pos_with_check_check(pygame_coordinates_to_pos(item.start_coords, flipped=self.flipped)):
                            pygame.draw.circle(self.display, preferences[Prefs.MOVE_INDICATOR_COLOUR], vector_add(pos_to_pygame_coordinates(end_pos, flipped=self.flipped), (32, 32)), 8)
                    item.draw(self.display)
                    break
            else:
                continue  # if break called before, breaks again to break outer loop, else continues
            break
        pygame.display.update()

    def get_display_text(self) -> list[str]:
        display_text = UI_TEXT[self.ui_text_mode].copy()
        if self.ui_text_mode == 0:
            display_text.append(STATE_TO_STR[self.state])
        if self.ui_text_mode == 1:
            display_text.append(f"A. Auto-Flip: {'Enabled' if self.auto_flip else 'Disabled'}")
        if self.ui_text_mode == 3:
            if self.background_engine is not None:
                display_text.append(f"Engine at depth {self.background_engine.depth}")
                if self.background_engine.best_move is not None:
                    display_text.append(f"Best move {pos_move_to_uci(self.background_engine.best_move)}")
        if self.ui_text_mode == 4:
            # This is usually really bad practice however for this case where we are debugging,
            # we actually do want to read the objects internal dictionary
            for key in self.game.__dict__:
                display_text.append(f"{key}: {self.game.__dict__[key]}")
        return display_text
    
    def check_threefold_repetition(self):
        board_position_fens = list(map(lambda fen: fen.split(" ")[0], self.list_of_FENs))
        last_board = board_position_fens[-1]
        if board_position_fens.count(last_board) == 3:
            return True
        return False


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
        try:
            return load_image(preferences[Prefs.PIECE_IMAGES][self.piece], (64, 64))
        except FileNotFoundError:
            return load_image(DEFAULT_PREFERENCES[Prefs.PIECE_IMAGES][self.piece], (64, 64))
    
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


class MoveList(pygame.sprite.Sprite):
    def __init__(self):
        """Width: 288, Height: 512"""
        self.rect = pygame.Rect(512,0, 288, 512)
        self.move_list = []
        self.background_colour = preferences[Prefs.BACKGROUND_COLOUR]
        self.font_colour = preferences[Prefs.CONTRASTING_COLOUR]
        self.font_size = preferences[Prefs.FONT_SIZE]
        self.special_colour = preferences[Prefs.MOVE_INDICATOR_COLOUR]
        self.surface = pygame.surface.Surface((288,512))
        self.surface.fill(self.background_colour)
        self.current_idx = 0
        self.max_length = 512//self.font_size

    def draw(self, display):
        display.blit(self.surface, self.rect)

    def append(self, move):
        self.move_list.append(move)
        self.update_image()

    def prepend(self, item):
        self.move_list.insert(0, item)
    
    def crop(self, idx):
        """Crops anything after idx off move_list"""
        self.move_list = self.move_list[0:idx-1]
        self.update_image()

    def update_image(self):
        self.surface = pygame.surface.Surface((288,512))
        self.surface.fill(self.background_colour)
        column_shift = (len(self.move_list)+1)//2 -self.max_length
        if column_shift*2 > self.current_idx:
            column_shift = (self.current_idx-1)//2
        if column_shift < 0:
            column_shift = 0
        moves_on_row = 0
        column = 0
        for i, move in enumerate(self.move_list):
            if i == self.current_idx:
                colour = self.special_colour
            else:
                colour = self.font_colour
            self.surface.blit(FONT.render(move, True, colour), (moves_on_row*144,(column-column_shift)*self.font_size))
            moves_on_row += 1
            if moves_on_row == 2:
                moves_on_row = 0
                column += 1

    def set_current_idx(self, idx):
        self.current_idx = idx
        self.update_image()

    def increment_idx(self):
        self.current_idx += 1


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
