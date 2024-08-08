import pygame
import sys

from ui import UI
from support import *
from data import Data
from settings import *
from level import Level
from debug import debug_display
from overworld import Overworld
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.audio_files = None
        self.level_frames = None
        self.overworld_frames = None
        self.font = None
        self.ui_frames = None

        self.win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.import_assets()

        pygame.display.set_caption("Super Pirate Adventure")

        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)

        self.tmx_maps = {0: load_pygame(BASE_PATH + 'data/levels/0.tmx'),
                         1: load_pygame(BASE_PATH + 'data/levels/1.tmx'),
                         2: load_pygame(BASE_PATH + 'data/levels/2.tmx'),
                         3: load_pygame(BASE_PATH + 'data/levels/3.tmx'),
                         4: load_pygame(BASE_PATH + 'data/levels/4.tmx'),
                         5: load_pygame(BASE_PATH + 'data/levels/5.tmx'),
                         }
        self.tmx_overworld = load_pygame(BASE_PATH + 'data/overworld/overworld.tmx')
        self.switch_stage('overworld', -1)

        self.audio_files['bg_music'].set_volume(0.2)
        self.audio_files['bg_music'].play(-1)

    def switch_stage(self, target, unlock=0):
        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames,
                                       self.data, self.switch_stage, self.audio_files)
        else:
            if unlock > 0:
                self.data.unlocked_level = max(unlock, self.data.unlocked_level)
            else:
                self.data.health -= 1
            self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)

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
            'water_top': import_folder('graphics', 'level', 'water', 'top'),
            'water_body': import_image('graphics', 'level', 'water', 'body'),
            'bg_tiles': import_folder_dict('graphics', 'level', 'bg', 'tiles'),
            'small_clouds': import_folder('graphics', 'level', 'clouds', 'small'),
            'big_clouds': import_image('graphics', 'level', 'clouds', 'large_cloud'),
        }

        self.ui_frames = {
            'heart': import_folder('graphics', 'ui', 'heart'),
            'coin': import_image('graphics', 'ui', 'coin'),
        }

        self.overworld_frames = {
            'palms': import_folder('graphics', 'overworld', 'palm'),
            'water': import_folder('graphics', 'overworld', 'water'),
            'path': import_folder_dict('graphics', 'overworld', 'path'),
            'icon': import_sub_folders('graphics', 'overworld', 'icon'),
        }

        self.audio_files = {
            'coin': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'coin.wav')),
            'attack': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'attack.wav')),
            'damage': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'damage.wav')),
            'hit': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'hit.wav')),
            'jump': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'jump.wav')),
            'pearl': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'pearl.wav')),
            'bg_music': pygame.mixer.Sound(join(BASE_PATH, 'audio', 'starlight_city.mp3')),
        }

    def check_game_over(self):
        if self.data.health <= 0:
            pygame.quit()
            sys.exit()

    def run(self):
        running = True

        while running:
            dt = self.clock.tick() / 1000
            self.check_game_over()
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
