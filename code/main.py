import pygame
import sys

from settings import *
from level import Level
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        pygame.init()

        self.win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Super Pirate Adventure")

        self.tmx_maps = {0: load_pygame(BASE_PATH + 'data/levels/omni.tmx')}

        self.current_stage = Level(self.tmx_maps[0])

    def run(self):
        running = True

        while running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.current_stage.run(dt)

            pygame.display.update()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
