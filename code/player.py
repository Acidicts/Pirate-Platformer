import pygame

from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = pygame.Surface((48, 56))
        self.image.fill("red")
        self.rect = self.image.get_frect(topleft=pos)

        self.direction = Vector2()
        self.speed = 200

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])

        if self.direction.magnitude():
            self.direction.normalize()

    def move(self, dt):
        self.rect.topleft += self.direction * self.speed * dt

    def update(self, dt):
        self.input()
        self.move(dt)
