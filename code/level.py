import pygame

from sprites import *
from settings import *
from player import Player
from groups import AllSprites


# noinspection PyTypeChecker
class Level:
    def __init__(self, tmx_map):
        self.win = pygame.display.get_surface()

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()

        self.player = None

        self.setup(tmx_map)

    def setup(self, tmx_map):
        for x, y, surf in tmx_map.get_layer_by_name('Terrain').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'player':
                self.player = Player((obj.x, obj.y), None, self.all_sprites, self.collision_sprites, self.semi_collision_sprites)

        for obj in tmx_map.get_layer_by_name('Moving Objects'):
            if obj.name == 'helicopter':
                if obj.width > obj.height:
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                else:
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)

                speed = obj.properties["speed"]

                MovingSprite((self.all_sprites, self.semi_collision_sprites), start_pos, end_pos, move_dir, speed)

    def run(self, dt):
        self.win.fill((0, 0, 0))

        self.all_sprites.draw(self.player.hitbox.center)
        self.all_sprites.update(dt)
