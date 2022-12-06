import pygame
pygame.init()
clock = pygame.time.Clock()

display = pygame.display.set_mode((800,800))
pygame.display.set_caption("Chess Engine")

BOARD = pygame.image.load("board.png")

def update_display():
    display.fill((192,192,192))
    display.blit(BOARD, (0,0))
    pygame.display.update()

class Piece:
    def __init__(self):
        pass

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_display()

pygame.quit()