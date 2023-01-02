from openings import opening_explorer
import pygame
from collections import defaultdict
pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Chess Engine")
pygame.scrap.init()


BOARD = pygame.image.load("images/board.png")  # squares are 64px wide
DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BACKGROUND_COLOUR = (64, 64, 64)
contrasting_colour = (255-BACKGROUND_COLOUR[0], 255-BACKGROUND_COLOUR[1], 255-BACKGROUND_COLOUR[2])
FONT = pygame.font.SysFont("Segoe UI", 30)


class Piece(pygame.sprite.Sprite):
    def __init__(self, rank: int, file: int, colour, parent=None):
        self.rank = rank
        self.file = file
        self.colour = colour
        self.dragging = False
        self.moved = False
        if parent == None:
            self._parent = pieces  # pointer with defaul parameter of main "pieces" list
        else:
            self._parent = parent

    def __repr__(self):
        return f"{self.colour} {self.__class__.__name__} on rank {self.rank} on file {self.file}"

    def update_pos(self):
        global piece_held, mouse_down, occupied_spaces, occupied_colour
        if (self.rect.collidepoint(pygame.mouse.get_pos()) or self.dragging) and mouse_down and (not piece_held or self.dragging):
            self.dragging = True
            piece_held = True
            self.rect = self.image.get_rect(center=pygame.mouse.get_pos())
        else:
            if not mouse_down and self.dragging:
                occupied_spaces, occupied_colour = self.do_move(coordinates_to_position(pygame.mouse.get_pos(), self))
                self.rect = self.image.get_rect(
                    center=get_center_coordinates(self.rank, self.file))
            if not mouse_down:
                self.dragging = False
                piece_held = False

    def do_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None):
        global white_move
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour

        if self.legal_move(destination):
            occupied_spaces.discard((self.file, self.rank))
            occupied_colour[(self.file, self.rank)] = None
            self.file, self.rank = coordinates_to_position(
                        pygame.mouse.get_pos(), self)
            occupied_spaces.add((self.file, self.rank))
            occupied_colour[(self.file, self.rank)] = self.colour
            if game_mode:
                white_move = False if white_move else True
            for piece in pieces:
                if piece == self:
                    pass
                else:
                    if piece.rank == self.rank and piece.file == self.file:
                        pieces.remove(piece)
        self.moved = True
        return target_occupied_spaces, target_occupied_colour

    def legal_move(self, destination: tuple, target_occupied_colour=None) -> bool:
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not game_mode:
            return True
        if not (white_move and self.colour == "White" or not white_move and self.colour == "Black"):
            return False
        new_file, new_rank = destination
        if new_file == self.file and new_rank == self.rank:
            return False
        if target_occupied_colour[destination] == self.colour:
            return False
        # need to add avoiding check
        return True


class Pawn(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load(
            "images/wP.svg" if self.colour == "White" else "images/bP.svg"), (64, 64))
        self.rect = self.image.get_rect(
            center=get_center_coordinates(self.rank, self.file))

    def legal_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None) -> bool:
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not super().legal_move(destination, target_occupied_colour=target_occupied_colour):
            return False
        if not game_mode:
            return True
        new_file, new_rank = destination
        moved = False if self.colour == "White" and self.rank == 2 or self.colour == "Black" and self.rank == 7 else True
        direction = +1 if self.colour == "White" else -1
        if new_file == self.file and (new_rank == self.rank+direction or new_rank == self.rank+2*direction and not moved) and destination not in target_occupied_spaces:  # moving forward
            if new_rank == self.rank+2*direction and (self.file, self.rank+direction) in target_occupied_spaces:
                return False
            return True
        if (new_file == self.file+1 or new_file == self.file-1) and new_rank == self.rank+direction and destination in target_occupied_spaces:  # moving diagonally
            return True
        # en passant not yet implemented
        return False


class Rook(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load(
            "images/wR.svg" if self.colour == "White" else "images/bR.svg"), (64, 64))
        self.rect = self.image.get_rect(
            center=get_center_coordinates(self.rank, self.file))
        self.kingside = True if (file, rank) == (8, (1 if colour == "White" else 8)) else False
        self.queenside = True if (file, rank) == (1, (1 if colour == "White" else 8)) else False

    def legal_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None) -> bool:
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not super().legal_move(destination, target_occupied_colour=target_occupied_colour):
            return False
        if not game_mode:
            return True
        new_file, new_rank = destination
        if new_file != self.file and new_rank != self.rank:
            return False
        if new_file == self.file:
            for rank in range(self.rank, new_rank, +1 if self.rank < new_rank else -1):
                if (new_file, rank) == (self.file, self.rank):
                    continue
                if (new_file, rank) in target_occupied_spaces:
                    return False
        else:
            for file in range(self.file, new_file, +1 if self.file < new_file else -1):
                if (file, new_rank) == (self.file, self.rank):
                    continue
                if (file, new_rank) in target_occupied_spaces:
                    return False
        return True


class Knight(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load(
            "images/wN.svg" if self.colour == "White" else "images/bN.svg"), (64, 64))
        self.rect = self.image.get_rect(
            center=get_center_coordinates(self.rank, self.file))

    def legal_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None) -> bool:
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not super().legal_move(destination, target_occupied_colour=target_occupied_colour):
            return False
        if not game_mode:
            return True
        new_file, new_rank = destination
        dfile = new_file - self.file
        drank = new_rank - self.rank
        if abs(dfile) == 2 and abs(drank) == 1 or abs(dfile) == 1 and abs(drank) == 2:
            return True
        return False


class Bishop(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load(
            "images/wB.svg" if self.colour == "White" else "images/bB.svg"), (64, 64))
        self.rect = self.image.get_rect(
            center=get_center_coordinates(self.rank, self.file))

    def legal_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None) -> bool:
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not super().legal_move(destination, target_occupied_colour=target_occupied_colour):
            return False
        if not game_mode:
            return True
        new_file, new_rank = destination
        dfile = new_file - self.file
        drank = new_rank - self.rank
        if abs(dfile) != abs(drank):
            return False
        direction = tuple(map(lambda x: +1 if x else -1,(dfile > 0, drank > 0)))  # unit vector
        for distance in range(abs(drank)):
            if distance == 0:
                continue
            if (self.file + distance*direction[0], self.rank + distance*direction[1]) in occupied_spaces:
                return False
        return True


class Queen(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load(
            "images/wQ.svg" if self.colour == "White" else "images/bQ.svg"), (64, 64))
        self.rect = self.image.get_rect(
            center=get_center_coordinates(self.rank, self.file))

    def legal_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None) -> bool:
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not super().legal_move(destination, target_occupied_colour=target_occupied_colour):
            return False
        if not game_mode:
            return True
        if Bishop(self.rank, self.file, self.colour).legal_move(destination) or Rook(self.rank, self.file, self.colour).legal_move(destination):
            return True
        return False


class King(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load(
            "images/wK.svg" if self.colour == "White" else "images/bK.svg"), (64, 64))
        self.rect = self.image.get_rect(
            center=get_center_coordinates(self.rank, self.file))
        self.castling = None

    def legal_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None) -> bool:
        if target_occupied_spaces is None:
            target_occupied_spaces = occupied_spaces
        if target_occupied_colour is None:
            target_occupied_colour = occupied_colour
        if not super().legal_move(destination, target_occupied_colour=target_occupied_colour):
            return False
        if not game_mode:
            return True
        new_file, new_rank = destination
        dfile = new_file - self.file
        drank = new_rank - self.rank
        if abs(dfile) <= 1 and abs(drank) <= 1:
            return True

        if abs(dfile) == 2 and drank == 0 and not self.moved:  # castling
            kingside_rook = get_rook(self._parent, True, self.colour)
            print(kingside_rook)
            queenside_rook = get_rook(self._parent, False, self.colour)
            print(queenside_rook)
            if self.colour == "White":
                if destination == (7, 1) and kingside_rook and not kingside_rook.moved:
                    self.castling = "Kingside"
                    return True
                if destination == (3, 1) and queenside_rook and not queenside_rook.moved:
                    self.castling = "Queenside"
                    return True
            else:
                if destination == (7, 8) and kingside_rook and not kingside_rook.moved:
                    self.castling = "Kingside"
                    return True
                if destination == (3, 8) and queenside_rook and not queenside_rook.moved:
                    self.castling = "Queenside"
                    return True

        return False

    def do_move(self, destination: tuple, target_occupied_spaces=None, target_occupied_colour=None):
        #doesn't correctly edit the rook piece from self._parent list, need to figure that out
        if self.castling == "Kingside":
            kingside_rook = get_rook(self._parent, True, self.colour)
            _index = self._parent.index(kingside_rook)
            kingside_rook.moved = True
            kingside_rook.file = 6
            self._parent[_index].moved = True
            self._parent[_index].file = 6
        if self.castling == "Queenside":
            queenside_rook = get_rook(self._parent, False, self.colour)
            _index = self._parent.index(queenside_rook)
            queenside_rook.moved = True
            queenside_rook.file = 4
            self._parent[_index].moved = True
            self._parent[_index].file = 4
        self.castling = None
        return super().do_move(destination, target_occupied_spaces, target_occupied_colour)


def update_display():
    display.fill(BACKGROUND_COLOUR)
    display.blit(BOARD, (0, 0))
    for piece in pieces:
        display.blit(piece.image, piece.rect)
    for piece in pieces:
        if piece.dragging:
            display.blit(piece.image, piece.rect)
    for text in initialise_text():
        display.blit(text[0], text[1])
    pygame.display.update()


def initialise_text():
    yield (FONT.render("Press O to open the opening explorer", True, contrasting_colour), (0, 512))
    yield (FONT.render(f"Current Mode: {'Game Mode' if game_mode else 'Setup Mode'} (press G to toggle)", True, contrasting_colour), (0, 544))
    yield (FONT.render(f"{'White' if white_move else 'Black'}'s move", True, contrasting_colour), (0, 576))


def FEN_to_pieces_list(FEN=DEFAULT_FEN):
    global white_move, occupied_spaces, occupied_colour
    pieces = []
    board_position = FEN.split(" ")[0]
    white_move = True if FEN.split(" ")[1] == "w" else False
    board_position = board_position.split("/")
    for rank_index, data in enumerate(board_position):
        rank = 8 - rank_index
        gap_adjustment = 0
        for file_index, piece in enumerate(data):
            file = file_index + 1 + gap_adjustment
            colour = "Black" if piece.lower() == piece else "White"
            if piece.lower() in letter_to_piece_dict:
                pieces.append(
                    letter_to_piece_dict[piece.lower()](rank, file, colour))
            else:
                gap_adjustment += int(piece) - 1
    occupied_spaces = set([(piece.file, piece.rank) for piece in pieces])
    occupied_colour = defaultdict(lambda: None, {(piece.file, piece.rank): piece.colour for piece in pieces})

    for piece in pieces:
        piece._parent = pieces
    return pieces


def pieces_to_FEN() -> str:
    current_rank = 8
    current_file = 1
    FEN = ""
    sort_rank = 8
    sort_file = 1
    sorted_pieces = []
    while sort_rank >= 1:
        for piece in pieces:
            if piece.rank == sort_rank and piece.file == sort_file:
                sorted_pieces.append(piece)
                break
        sort_file += 1
        if sort_file > 8:
            sort_file = 1
            sort_rank -= 1

    for piece in sorted_pieces:
        if piece.rank == current_rank and piece.file == current_file:
            FEN += piece_to_letter_dict[piece.__class__.__name__] if piece.colour == "Black" else piece_to_letter_dict[piece.__class__.__name__].upper()
        elif piece.rank == current_rank:
            file_gap = piece.file - current_file
            FEN += str(file_gap)
            FEN += piece_to_letter_dict[piece.__class__.__name__] if piece.colour == "Black" else piece_to_letter_dict[piece.__class__.__name__].upper()
            current_file += file_gap
        else:
            rank_gap = current_rank - piece.rank
            while rank_gap >= 1:
                file_gap = 9 - current_file
                FEN += str(file_gap)
                current_file = 1
                current_rank -= 1
                FEN += "/"
                rank_gap = current_rank - piece.rank
            file_gap = piece.file - current_file
            if file_gap != 0:
                FEN += str(file_gap)
            FEN += piece_to_letter_dict[piece.__class__.__name__] if piece.colour == "Black" else piece_to_letter_dict[piece.__class__.__name__].upper()
            current_file += file_gap

        current_file += 1
        if current_file > 8:
            current_file = 1
            current_rank -= 1
            FEN += "/"
    while current_rank >= 1:
        FEN += str(9 - current_file)
        current_file = 1
        FEN += "/"
        current_rank -= 1

    FEN = FEN[:-1]  # removes final "/"
    FEN += " "
    FEN += "w" if white_move else "b"
    FEN += " "
    FEN += "KQkq - 0 1"  # needs to be actually implemented in future
    return FEN


def get_center_coordinates(rank: int, file: int) -> tuple:
    file_coordinates = -32 + 64*file
    rank_coordinates = 32 + 64*(8-rank)
    return (file_coordinates, rank_coordinates)


def coordinates_to_position(coordinates: tuple, piece: Piece):
    if coordinates[0] > 512 or coordinates[1] > 512:
        return piece.file, piece.rank
    file = coordinates[0]//64 + 1
    rank = 8 - coordinates[1]//64
    return file, rank


def get_legal_moves(pieces: list):
    for piece in pieces:
        for file in range(1, 9):
            for rank in range(1, 9):
                if piece.legal_move((file, rank)):
                    yield (piece, (file, rank))

def get_rook(target_pieces: list[Piece], kingside: bool, colour: str) -> Rook:
    """Linear search to return Rook Piece from a list, returns None if specified piece is not in list"""
    for piece in target_pieces:
        if type(piece) == Rook and piece.colour == colour:
            print(f"{piece} piece found, kingside: {piece.kingside}, queenside: {piece.queenside}")
            if (piece.kingside if kingside else piece.queenside):
                return piece
    return None


letter_to_piece_dict = {"p": Pawn, "r": Rook,
                        "n": Knight, "b": Bishop, "q": Queen, "k": King}
piece_to_letter_dict = {"Pawn": "p", "Rook": "r",
                        "Knight": "n", "Bishop": "b", "Queen": "q", "King": "k"}
pieces = list()
pieces = FEN_to_pieces_list()
mouse_down = False
piece_held = False
game_mode = True

if __name__ == "__main__":
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_END:
                    pieces = FEN_to_pieces_list(FEN="8/8/8/8/8/8/8/8 w - - 0 1")
                if event.key == pygame.K_HOME:
                    pieces = FEN_to_pieces_list()
                if event.key == pygame.K_f:
                    print(pieces_to_FEN())
                if event.key == pygame.K_l:
                    pieces = FEN_to_pieces_list(
                        FEN=str(pygame.scrap.get(pygame.SCRAP_TEXT))[2:-5])
                if event.key == pygame.K_g:
                    game_mode = True if not game_mode else False
                if event.key == pygame.K_o:
                    chosen_opening = opening_explorer.open_window()
                    if chosen_opening:
                        pieces = FEN_to_pieces_list(FEN=chosen_opening)
                if event.key == pygame.K_p:
                    print(list(get_legal_moves(pieces)))

        for piece in pieces:
            piece.update_pos()
        if mouse_down and not piece_held:
            mouse_down = False

        update_display()
        clock.tick(60)

    pygame.quit()
