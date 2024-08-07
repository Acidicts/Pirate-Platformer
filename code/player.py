import math

import pygame

from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, collision_sprites, semi_collision_sprites, frames, data):
        # noinspection PyTypeChecker
        super().__init__(groups)

        self.data = data

        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]

        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox.copy()

        self.z = Z_LAYERS['main']

        self.direction = Vector2()
        self.speed = 200
        self.gravity = 1300
        self.attacking = False

        self.jump = False
        self.jump_height = 900

        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surf = {'floor': False, 'left': False, 'right': False}
        self.platform = None

        self.timers = {
            'wall jump': Timer(400),
            'wall slide block': Timer(250),
            'platform skip': Timer(300),
            'attack block': Timer(500),
            'hit': Timer(400),
        }

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['wall jump'].active:
            self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])

        if self.direction.x:
            self.direction.normalize().x

        if keys[pygame.K_SPACE]:
            self.jump = True

        if keys[pygame.K_s]:
            self.timers["platform skip"].activate()

        if keys[pygame.K_x]:
            self.attack()

    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()

    def move(self, dt):
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision('x')

        if not self.on_surf['floor'] and any((self.on_surf['left'],
                                              self.on_surf['right'])) and not self.timers['wall slide block'].active:
            self.direction.y = 0
            self.hitbox.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surf['floor']:
                self.direction.y = -self.jump_height
                self.timers['wall slide block'].activate()
                self.hitbox.bottom -= 1

            elif any((self.on_surf['left'], self.on_surf['right'])) and not self.timers['wall slide block'].active:

                self.timers['wall jump'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surf['left'] else -1

            self.jump = False

        self.collision('y')
        self.semi_collision()
        self.rect.center = self.hitbox.center

        if self.direction.x == 1:
            self.facing_right = True
        elif self.direction.x == -1:
            self.facing_right = False

    def platform_move(self, dt):
        if self.platform:
            self.hitbox.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 2))
        right_rect = pygame.Rect(self.hitbox.topright + Vector2(0, self.hitbox.height / 4), (2, self.hitbox.height / 2))
        left_rect = pygame.Rect(self.hitbox.topleft + Vector2(-2, self.hitbox.height / 4), (2, self.hitbox.height / 2))

        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]

        self.on_surf['floor'] = True if floor_rect.collidelist(collide_rects) > 0 or floor_rect.collidelist(
            semi_collide_rect) > 0 else False
        self.on_surf['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surf['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if axis == 'x':
                    if self.hitbox.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox.left = sprite.rect.right

                    if self.hitbox.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox.right = sprite.rect.left

                if axis == 'y':
                    if self.hitbox.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'):
                            self.rect.top += 6

                    if self.hitbox.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox.bottom = sprite.rect.top

                    self.direction.y = 0

    def semi_collision(self):
        if not self.timers['platform skip'].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox):
                    if self.hitbox.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= sprite.old_rect.top:
                        self.hitbox.bottom = sprite.rect.top
                        if self.direction.y >= 0:
                            self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if 'attack' in self.state and self.frame_index >= len(self.frames[self.state]):
            self.state = 'idle'
            self.attacking = False
        frame = pygame.transform.flip(self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])],
                                      not self.facing_right,
                                      False)
        self.image = frame

        self.get_state()

    def get_state(self):
        if self.on_surf['floor'] or self.direction.y == 0:
            if self.attacking:
                if self.state != "attack":
                    self.state = 'attack'
            else:
                self.state = 'run' if self.direction.x else 'idle'
        else:
            if self.attacking:
                if self.state != "air_attack":
                    self.state = 'air_attack'
            else:
                if any((self.on_surf['left'], self.on_surf['right'])):
                    self.state = 'wall'
                else:
                    self.state = 'jump' if self.direction.y < 0 else 'fall'

    def get_damaged(self):
        if not self.timers['hit'].active:
            self.timers['hit'].activate()
            self.data.health -= 1

    def flicker(self):
        if self.timers['hit'].active and math.sin(pygame.time.get_ticks() * 100) >= 0:
            mask = pygame.mask.from_surface(self.image)
            white_mask = mask.to_surface()
            white_mask.set_colorkey((0, 0, 0))
            self.image = white_mask

    def update(self, dt):
        self.old_rect = self.hitbox.copy()

        self.update_timers()

        self.input()
        self.move(dt)
        self.platform_move(dt)

        self.animate(dt)
        self.flicker()

        self.check_contact()
