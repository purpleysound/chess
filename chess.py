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
    pygame.display.update()

def get_board_state(FEN=DEFAULT_FEN):
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

class Piece(pygame.sprite.Sprite):
    def __init__(self, rank, file, colour):
        self.rank = rank
        self.file = file
        self.colour = colour

    def __repr__(self):
        return f"{self.__class__.__name__} piece on rank {self.rank} on file {self.file}"

    def update_pos(self):
        new_mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(new_mouse_pos) and pygame.mouse.get_pressed()[0]:
            dx = new_mouse_pos[0] - old_mouse_pos[0] + 32 #i don't know why you need to add 32 but it works
            dy = new_mouse_pos[1] - old_mouse_pos[1] + 32
            self.rect = self.image.get_rect(center=(self.rect[0]+dx, self.rect[1]+dy))
        else:
            self.rect = self.image.get_rect(center=get_center_coordinates(self.rank,self.file))


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
pieces = get_board_state()
print(pieces)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for piece in pieces:
        piece.update_pos()
    old_mouse_pos = pygame.mouse.get_pos()

    update_display()
    clock.tick(60)

pygame.quit()