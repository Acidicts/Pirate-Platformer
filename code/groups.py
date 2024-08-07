import pygame.display

from settings import *
from sprites import Sprite


class AllSprites(pygame.sprite.Group):
    def __init__(self, width, height, bg_tile=None, top_limit=0):
        super().__init__()

        self.display_surf = pygame.display.get_surface()
        self.offset = Vector2()

        self.width, self.height = width * TILE_SIZE, height * TILE_SIZE

        if bg_tile:
            for col in range(int(width)):
                for row in range(int(-top_limit/TILE_SIZE), int(height)):
                    x, y = col * TILE_SIZE, row * TILE_SIZE - (10 * TILE_SIZE)
                    Sprite((x, y), bg_tile, self, -1)

    # noinspection PyTypeChecker
    def camera_constraint(self):
        self.offset.x = max(-(self.width - WINDOW_WIDTH), min(0, self.offset.x))

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        self.camera_constraint()

        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surf.blit(sprite.image, offset_pos)
