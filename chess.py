import pygame
pygame.init()
clock = pygame.time.Clock()

display = pygame.display.set_mode((800,800))
pygame.display.set_caption("Chess Engine")
pygame.scrap.init()

BOARD = pygame.image.load("images/board.png") #squares are 64px wide
DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def update_display():
    display.fill((80,80,80))
    display.blit(BOARD, (0,0))
    for piece in pieces:
        display.blit(piece.image, piece.rect)
    for piece in pieces:
        if piece.dragging:
            display.blit(piece.image, piece.rect)
    pygame.display.update()

def FEN_to_pieces_list(FEN=DEFAULT_FEN):
    global white_move
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
                pieces.append(letter_to_piece_dict[piece.lower()](rank, file, colour))
            else:
                gap_adjustment += int(piece) - 1                
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

    for piece in sorted_pieces: #doesn't fill rest of board with space after last piece
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
    FEN = FEN[:-1] #removes final "/"
    FEN += " w KQkq - 0 1" #needs to be actually implemented in future
    return FEN


def get_center_coordinates(rank: int, file: int) -> tuple:
    file_coordinates = -32 + 64*file
    rank_coordinates = 32 + 64*(8-rank)
    return (file_coordinates, rank_coordinates)

def coordinates_to_position(coordinates, piece):
    if coordinates[0] > 512 or coordinates[1] > 512:
        return piece.rank, piece.file
    file = coordinates[0]//64 + 1
    rank = 8 - coordinates[1]//64
    return file, rank

class Piece(pygame.sprite.Sprite):
    def __init__(self, rank, file, colour):
        self.rank = rank
        self.file = file
        self.colour = colour
        self.dragging = False

    def __repr__(self):
        return f"{self.colour} {self.__class__.__name__} piece on rank {self.rank} on file {self.file}"

    def update_pos(self):
        global piece_held, mouse_down
        if (self.rect.collidepoint(pygame.mouse.get_pos()) or self.dragging) and mouse_down and (not piece_held or self.dragging):
            self.dragging = True
            piece_held = True
            self.rect = self.image.get_rect(center=pygame.mouse.get_pos())
        else:
            if not mouse_down and self.dragging:
                self.file, self.rank = coordinates_to_position(pygame.mouse.get_pos(), self)
                for piece in pieces:
                    if piece == self:
                        pass
                    else:
                        if piece.rank == self.rank and piece.file == self.file:
                            pieces.remove(piece)
            self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))
            if not mouse_down:
                self.dragging = False
                piece_held = False


class Pawn(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load("images/wP.svg" if self.colour == "White" else "images/bP.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class Rook(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load("images/wR.svg" if self.colour == "White" else "images/bR.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))
    
class Knight(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load("images/wN.svg" if self.colour == "White" else "images/bN.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class Bishop(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load("images/wB.svg" if self.colour == "White" else "images/bB.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class Queen(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load("images/wQ.svg" if self.colour == "White" else "images/bQ.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class King(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.smoothscale(pygame.image.load("images/wK.svg" if self.colour == "White" else "images/bK.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

letter_to_piece_dict = {"p": Pawn, "r": Rook, "n": Knight, "b": Bishop, "q": Queen, "k": King}
piece_to_letter_dict = {"Pawn": "p", "Rook": "r", "Knight": "n", "Bishop": "b", "Queen": "q", "King": "k"}
pieces = FEN_to_pieces_list()
mouse_down = False
piece_held = False

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
                clipboard = str(pygame.scrap.get(pygame.SCRAP_TEXT))
                clipboard = clipboard[2:-5]
                print(clipboard)
                pieces = FEN_to_pieces_list(FEN=clipboard)

    for piece in pieces:
        piece.update_pos()
    if mouse_down and not piece_held:
        mouse_down = False

    update_display()
    clock.tick(60)

pygame.quit()