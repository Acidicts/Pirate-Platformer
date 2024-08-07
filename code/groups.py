import pygame.display

from settings import *
from timer import Timer
from sprites import Sprite, Cloud
from random import choice, randint


class WorldSprites(pygame.sprite.Group):
    def __init__(self, data):
        super().__init__()
        self.display_surf = pygame.display.get_surface()
        self.update(data)

        self.offset = Vector2()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        for sprit in sorted(self, key=lambda sprit: sprit.z):
            offset_pos = sprit.rect.topleft + self.offset
            self.display_surf.blit(sprit.image, offset_pos)


class AllSprites(pygame.sprite.Group):
    def __init__(self, width, height, bg_tile=None, top_limit=0, clouds=None, horizon_line=400):
        super().__init__()

        self.display_surf = pygame.display.get_surface()
        self.offset = Vector2()

        self.width, self.height = int(width * TILE_SIZE), int(height * TILE_SIZE)
        self.top_limit = top_limit

        self.sky = not bg_tile
        self.horizon_line = horizon_line

        if bg_tile:
            for col in range(int(width)):
                for row in range(-int(top_limit/TILE_SIZE) - 1, int(height) + 10):
                    x, y = col * TILE_SIZE, row * TILE_SIZE
                    # noinspection PyTypeChecker
                    Sprite((x, y), bg_tile, self, -1)

        else:
            self.large_cloud = clouds['big']
            self.small_cloud = clouds['small']

            self.cloud_direction = -1

            self.large_cloud_speed = 50
            self.large_cloud_x = 0
            self.large_cloud_tiles = int(self.width / self.large_cloud.get_width()) + 2
            self.large_cloud_width, self.large_cloud_height = self.large_cloud.get_size()

            self.cloud_timer = Timer(2500, self.create_cloud, True)
            self.cloud_timer.active = True

            for cloud in range(20):
                pos = (randint(0, int(self.width)), randint(self.top_limit, self.horizon_line))
                Cloud(pos, choice(self.small_cloud), self)

    # noinspection PyTypeChecker
    def camera_constraint(self):
        self.offset.x = max(-(self.width - WINDOW_WIDTH), min(0, self.offset.x))

        self.offset.y = self.offset.y if self.height > (-self.height +
                                                        WINDOW_HEIGHT) else (-self.height + WINDOW_HEIGHT)
        self.offset.y = self.offset.y if self.offset.y < self.top_limit else self.top_limit

    def draw_sky(self):
        self.display_surf.fill('#ddc6a1')

        sea_rect = pygame.FRect(0, self.horizon_line, WINDOW_WIDTH, WINDOW_HEIGHT - self.horizon_line)
        sea_rect.y += self.offset.y
        pygame.draw.rect(self.display_surf, '#92a9ce', sea_rect)

        pygame.draw.line(self.display_surf, '#f5f1de', (0, self.horizon_line + self.offset.y),
                         (WINDOW_WIDTH, self.horizon_line + self.offset.y), 4)

    def draw_large_cloud(self, dt):
        self.large_cloud_x += self.large_cloud_speed * dt * self.cloud_direction

        if self.large_cloud_x <= -self.large_cloud_width:
            self.large_cloud_x = 0

        for cloud in range(self.large_cloud_tiles):
            x = self.large_cloud_x + self.large_cloud_width * cloud
            y = self.horizon_line - self.large_cloud_height + self.offset.y
            self.display_surf.blit(self.large_cloud, (x, y))

    def create_cloud(self):
            pos = (randint(self.width + 200, self.width + 500) , randint(self.top_limit, self.horizon_line))
            Cloud(pos, choice(self.small_cloud), self)

    def draw(self, target_pos, dt):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        self.camera_constraint()

        if self.sky:
            self.cloud_timer.update()
            self.draw_sky()
            self.draw_large_cloud(dt)

        for sprit in sorted(self, key=lambda sprit: sprit.z):
            offset_pos = sprit.rect.topleft + self.offset
            self.display_surf.blit(sprit.image, offset_pos)
