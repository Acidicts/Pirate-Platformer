import pygame

from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, collision_sprites):
        super().__init__(groups)

        self.image = pygame.Surface((48, 56))
        self.image.fill("red")

        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()

        self.direction = Vector2()
        self.speed = 200
        self.gravity = 1300

        self.jump = False
        self.jump_height = 900

        self.collision_sprites = collision_sprites
        self.on_surf = {'floor': False, 'left': False, 'right': False}

        self.timers = {
            'wall jump': Timer(400),
            'wall slide block': Timer(250)
        }

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['wall jump'].active:
            self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])

        if self.direction.x:
            self.direction.normalize().x

        if keys[pygame.K_SPACE]:
            self.jump = True

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('x')

        if not self.on_surf['floor'] and any((self.on_surf['left'],
                                                     self.on_surf['right'])) and not self.timers['wall slide block'].active:
            self.direction.y = 0
            self.rect.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surf['floor']:
                self.direction.y = -self.jump_height

            elif any((self.on_surf['left'], self.on_surf['right'])) and not self.timers['wall slide block'].active:

                self.timers['wall jump'].activate()
                self.timers['wall slide block'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surf['left'] else -1

            self.jump = False

        self.collision('y')

    def check_contact(self):
        floor_rect = pygame.Rect(self.rect.bottomleft, (self.rect.width, 2))
        right_rect = pygame.Rect(self.rect.topright + Vector2(0, self.rect.height / 4), (2, self.rect.height / 2))
        left_rect = pygame.Rect(self.rect.topleft + Vector2(-2, self.rect.height / 4), (2, self.rect.height / 2))

        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        self.on_surf['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 else False
        self.on_surf['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surf['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == 'x':
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right

                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left

                if axis == 'y':
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom

                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top

                    self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.old_rect = self.rect.copy()

        self.update_timers()

        self.input()
        self.move(dt)

        self.check_contact()
