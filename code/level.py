import pygame

from sprites import *
from settings import *
from player import Player
from random import uniform
from groups import AllSprites


# noinspection PyTypeChecker
class Level:
    def __init__(self, tmx_map, level_frames):
        self.win = pygame.display.get_surface()

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()

        self.player = None

        self.setup(tmx_map, level_frames)

    def setup(self, tmx_map, level_frames):
        for layer in ['BG', 'Terrain', 'FG', 'Platforms']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'Terrain': groups.append(self.collision_sprites)
                if layer == 'Platforms': groups.append(self.semi_collision_sprites)

                match layer:
                    case 'BG':
                        z = Z_LAYERS['bg tiles']
                    case 'FG':
                        z = Z_LAYERS['bg tiles']
                    case _:
                        z = Z_LAYERS['main']

                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)

        for obj in tmx_map.get_layer_by_name('BG details'):
            if obj.name == 'static':
                Sprite((obj.x, obj.y), obj.image, (self.all_sprites,), Z_LAYERS['bg tiles'])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, Z_LAYERS['bg tiles'])
                if obj.name == 'candle':
                    AnimatedSprite((obj.x, obj.y) + Vector2(-20, -20), level_frames['candle_light'], self.all_sprites,
                                   Z_LAYERS['bg tiles'])

        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'player':
                self.player = Player(
                    (obj.x, obj.y),
                    None,
                    self.all_sprites,
                    self.collision_sprites,
                    self.semi_collision_sprites,
                    level_frames['player']
                )

            else:
                if obj.name in ('barrel', 'crate'):
                    Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
                else:
                    frames = level_frames['palms'][obj.name] if 'palm' in obj.name else level_frames[obj.name]

                    if obj.name == "floor_spike" and obj.properties['inverted']:
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                    groups = [self.all_sprites]
                    if obj.name in ('palm_small', 'palm_large'): groups.append(self.semi_collision_sprites)
                    if obj.name in ('saw', 'floor_spike'): groups.append(self.damage_sprites)

                    z = Z_LAYERS['bg details'] if 'bg' in obj.name else Z_LAYERS['fg']

                    animation_speed = ANIMATION_SPEED if not 'palms' in obj.name else ANIMATION_SPEED + uniform(-1, 1)

                    AnimatedSprite((obj.x, obj.y), frames, groups, z)

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
