import pygame
pygame.init()
clock = pygame.time.Clock()

display = pygame.display.set_mode((800,800))
pygame.display.set_caption("Chess Engine")

BOARD = pygame.image.load("board.png")
DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def update_display():
    display.fill((80,80,80))
    display.blit(BOARD, (0,0))
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
            colour = "White" if piece.lower() == piece else "Black"
            if piece.lower() in letter_to_piece_dict:
                pieces.append(letter_to_piece_dict[piece.lower()](rank, file, colour))
            else:
                gap_adjustment += int(piece) - 1
                
    return pieces

class Piece(pygame.sprite.Sprite):
    def __init__(self, rank, file, colour):
        self.rank = rank
        self.file = file
        self.colour = colour

    def __repr__(self):
        return f"{self.__class__.__name__} piece on rank {self.rank} on file {self.file}"

class Pawn(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)

class Rook(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)
    
class Knight(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)

class Bishop(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)

class Queen(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)

class King(Piece):
    def __init__(self, rank, file, colour):
        super().__init__(rank, file, colour)

letter_to_piece_dict = {"p": Pawn, "r": Rook, "n": Knight, "b": Bishop, "q": Queen, "k": King}
pieces = get_board_state()
print(pieces)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_display()

pygame.quit()