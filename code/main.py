import pygame
import sys

from ui import UI
from support import *
from data import Data
from settings import *
from level import Level
from debug import debug_display
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        pygame.init()

        self.level_frames = None
        self.font = None
        self.ui_frames = None

        self.win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.import_assets()

        pygame.display.set_caption("Super Pirate Adventure")

        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)

        self.tmx_maps = {0: load_pygame(BASE_PATH + 'data/levels/omni.tmx')}
        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.data)

    def import_assets(self):
        self.font = pygame.font.Font(join(BASE_PATH, 'graphics', 'ui', 'runescape_uf.ttf'), 30)

        self.level_frames = {
            'flag': import_folder('graphics', 'level', 'flag'),
            'floor_spike': import_folder('graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders('graphics', 'level', 'palms'),
            'candle': import_folder('graphics', 'level', 'candle'),
            'window': import_folder('graphics', 'level', 'window'),
            'big_chain': import_folder('graphics', 'level', 'big_chains'),
            'small_chain': import_folder('graphics', 'level', 'small_chains'),
            'candle_light': import_folder('graphics', 'level', 'candle light'),
            'player': import_sub_folders('graphics', 'player'),
            'saw': import_folder('graphics', 'enemies', 'saw', 'animation'),
            'saw_chain': import_image('graphics', 'enemies', 'saw', 'saw_chain'),
            'helicopter': import_folder('graphics', 'level', 'helicopter'),
            'boat': import_folder('graphics', 'objects', 'boat'),
            'spike': import_image('graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spike_chain': import_image('graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'tooth': import_folder('graphics', 'enemies', 'tooth', 'run'),
            'shell': import_sub_folders('graphics', 'enemies', 'shell'),
            'pearl': import_image('graphics', 'enemies', 'bullets', 'pearl'),
            'items': import_sub_folders('graphics', 'items'),
            'particles': import_folder('graphics', 'effects'),
        }

        self.ui_frames = {
            'heart': import_folder('graphics', 'ui', 'heart'),
            'coin': import_image('graphics', 'ui', 'coin'),
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

            self.ui.update(dt)
            pygame.display.update()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
