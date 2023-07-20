import pygame

class Game:
    def __init__(self):
        pass


class User_Interface:
    BACKGROUND_COLOUR = (64, 64, 64)
    CONTRASTING_COLOUR = tuple(255 - colour for colour in BACKGROUND_COLOUR)
    BOARD_IMG = pygame.image.load("images/board.png")
    def __init__(self):
        self.display = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = Game()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self):
        pass

    def draw(self):
        self.display.fill(self.BACKGROUND_COLOUR)
        self.display.blit(self.BOARD_IMG, (0, 0))
        pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    User_Interface().run()
    pygame.quit()