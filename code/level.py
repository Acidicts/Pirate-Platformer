import pygame

from sprites import *
from settings import *
from player import Player
from random import uniform
from groups import AllSprites
from enemies import Tooth, Shell, Pearl


# noinspection PyTypeChecker
class Level:
    def __init__(self, tmx_map, level_frames):
        self.win = pygame.display.get_surface()

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.items_sprites = pygame.sprite.Group()

        self.player = None

        self.setup(tmx_map, level_frames)

        self.particle_frames = level_frames['particles']

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
            if obj.name == "spike":
                Spike((obj.x + obj.width / 2, obj.y + obj.height / 2),
                      level_frames['spike'],
                      obj.properties['radius'],
                      obj.properties['speed'],
                      obj.properties['start_angle'],
                      obj.properties['end_angle'],
                      (self.all_sprites, self.damage_sprites))

                for radius in range(0, obj.properties['radius'], 20):
                    Spike((obj.x + obj.width / 2, obj.y + obj.height / 2),
                          level_frames['spike_chain'],
                          radius,
                          obj.properties['speed'],
                          obj.properties['start_angle'],
                          obj.properties['end_angle'],
                          self.all_sprites,
                          Z_LAYERS['bg details'])

            else:
                frames = level_frames[obj.name]
                groups = (self.all_sprites, self.semi_collision_sprites) if obj.properties["platform"] else (
                self.all_sprites,)

                if obj.width > obj.height:
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                else:
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)

                speed = obj.properties["speed"]
                MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, obj.properties['flip'])

                if obj.name == "saw":
                    if move_dir == "x":
                        y = start_pos[1] - level_frames['saw_chain'].get_height() / 2
                        left, right = start_pos[0], end_pos[0]
                        for x in range(int(left), int(right), 20):
                            Sprite((x, y), level_frames['saw_chain'], (self.all_sprites, self.damage_sprites),
                                   Z_LAYERS['bg details'])
                    else:
                        x = start_pos[0] - level_frames['saw_chain'].get_width() / 2
                        top, bottom = start_pos[1], end_pos[1]
                        for y in range(int(top), int(bottom), 20):
                            Sprite((x, y), level_frames['saw_chain'], (self.all_sprites, self.damage_sprites),
                                   Z_LAYERS['bg details'])

        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == "tooth":
                Tooth((obj.x, obj.y), level_frames['tooth'],
                      (self.all_sprites, self.tooth_sprites, self.damage_sprites),
                      self.collision_sprites, Z_LAYERS['main'], self.hit_player)
            elif obj.name == "shell":
                Shell((obj.x, obj.y), level_frames,
                      (self.all_sprites, self.damage_sprites, self.collision_sprites),
                      obj.properties['reverse'],
                      self.player, self.create_pearl)

        for obj in tmx_map.get_layer_by_name('Items'):
            Item(obj.name, (obj.x + TILE_SIZE/2, obj.y + TILE_SIZE/2), level_frames['items'][obj.name], (self.all_sprites, self.items_sprites))

    def create_pearl(self, pos, direction, surf):
        Pearl(pos, (self.all_sprites, self.damage_sprites, self.pearl_sprites), surf, direction,
              150, self.collision_sprites, self.player, self.hit_collision)

    def hit_player(self, rect):
        if rect.colliderect(self.player.hitbox):
            self.player.get_damage()

    def hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox):
                self.player.get_damage()

    def item_collision(self):
        if self.items_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.items_sprites, True)
            if item_sprites:
                ParticleEffectSprite(item_sprites[0].rect.center, self.particle_frames, self.all_sprites)

    def attack_collision(self):
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites():
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.reverse()

    def run(self, dt):
        self.win.fill((0, 0, 0))

        self.all_sprites.update(dt)

        self.item_collision()
        self.attack_collision()

        self.all_sprites.draw(self.player.hitbox.center)
