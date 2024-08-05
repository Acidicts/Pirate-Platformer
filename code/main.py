import pygame
import sys

from settings import *
from level import Level
from support import *
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        self.level_frames = None
        pygame.init()

        self.win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.import_assets()

        pygame.display.set_caption("Super Pirate Adventure")

        self.tmx_maps = {0: load_pygame(BASE_PATH + 'data/levels/omni.tmx')}

        self.current_stage = Level(self.tmx_maps[0], self.level_frames)

    def import_assets(self):
        self.level_frames = {
            'flag': import_folder('graphics', 'level', 'flag'),
            'saw': import_folder('graphics', 'enemies', 'saw', 'animation'),
            'floor_spike': import_folder('graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders('graphics', 'level', 'palms'),
            'candle': import_folder('graphics', 'level', 'candle'),
            'window': import_folder('graphics', 'level', 'window'),
            'big_chain': import_folder('graphics', 'level', 'big_chains'),
            'small_chain': import_folder('graphics', 'level', 'small_chains'),
            'candle_light': import_folder('graphics', 'level', 'candle light'),
            'player': import_sub_folders('graphics', 'player'),
        }

    def run(self):
        running = True

        while running:
            dt = self.clock.tick() / 1000
            pygame.display.set_caption(f"Super Pirate Adventure - FPS: {int(self.clock.get_fps())}")
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
