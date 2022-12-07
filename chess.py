import pygame
pygame.init()
clock = pygame.time.Clock()

display = pygame.display.set_mode((800,800))
pygame.display.set_caption("Chess Engine")

BOARD = pygame.image.load("board.png") #squares are 64px wide
DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def update_display():
    display.fill((80,80,80))
    display.blit(BOARD, (0,0))
    for piece in pieces:
        display.blit(piece.image, piece.rect)
        if piece.dragging: #should put moving piece on top, doesn't work
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
        return f"{self.__class__.__name__} piece on rank {self.rank} on file {self.file}"

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
        self.image = pygame.transform.scale(pygame.image.load("wP.svg" if self.colour == "White" else "bP.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class Rook(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.scale(pygame.image.load("wR.svg" if self.colour == "White" else "bR.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))
    
class Knight(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.scale(pygame.image.load("wN.svg" if self.colour == "White" else "bN.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class Bishop(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.scale(pygame.image.load("wB.svg" if self.colour == "White" else "bB.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class Queen(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.scale(pygame.image.load("wQ.svg" if self.colour == "White" else "bQ.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

class King(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
        self.image = pygame.transform.scale(pygame.image.load("wK.svg" if self.colour == "White" else "bK.svg"), (64,64))
        self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))

letter_to_piece_dict = {"p": Pawn, "r": Rook, "n": Knight, "b": Bishop, "q": Queen, "k": King}
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

    for piece in pieces:
        piece.update_pos()
    if mouse_down and not piece_held:
        mouse_down = False

    update_display()
    clock.tick(60)

pygame.quit()