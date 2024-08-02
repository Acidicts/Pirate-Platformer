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

        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])

        if self.direction.x:
            self.direction.normalize().x

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('x')

        self.direction.y += self.gravity / 2 * dt
        self.rect.y += self.direction.y * dt
        self.direction.y += self.gravity / 2 * dt
        self.collision('y')

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

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.input()
        self.move(dt)
