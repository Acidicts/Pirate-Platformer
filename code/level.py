import pygame

from settings import *
from player import Player
from sprites import Sprite


# noinspection PyTypeChecker
class Level:
    def __init__(self, tmx_map):
        self.win = pygame.display.get_surface()

        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.player = None

        self.setup(tmx_map)

    def setup(self, tmx_map):
        for x, y, surf in tmx_map.get_layer_by_name('Terrain').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'player':
                self.player = Player((obj.x, obj.y), None, self.all_sprites, self.collision_sprites)

    def run(self, dt):
        self.win.fill((0, 0, 0))

        self.all_sprites.draw(self.win)
        self.all_sprites.update(dt)
