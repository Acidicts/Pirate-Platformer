from settings import *
from sprites import AnimatedSprite
from random import randint


class UI:
    def __init__(self, font, frames):
        self.display_surf = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        self.heart_frames = frames['heart']
        self.heart_surf_width = self.heart_frames[0].get_width()
        self.heart_padding = 6

        self.coins = 0
        self.coin_timer = Timer(1000)
        self.coin_surf = frames['coin']

    def create_hearts(self, num):
        self.sprites.empty()
        for heart in range(num):
            x = 10 + heart * (self.heart_surf_width + self.heart_padding)
            y = 10
            # noinspection PyTypeChecker
            Heart((x, y), self.heart_frames, self.sprites)

    def display_text(self):
        coin_rect = self.coin_surf.get_frect(topleft=(8, 34))
        self.display_surf.blit(self.coin_surf, coin_rect)

        text_surf = self.font.render(str(self.coins), False, '#33323d')
        text_rect = text_surf.get_frect(midleft=(coin_rect.right + 10, coin_rect.centery))
        self.display_surf.blit(text_surf, text_rect)

    def show_coins(self, amount):
        self.coins = amount

    def update(self, dt):
        self.sprites.update(dt)
        self.sprites.draw(self.display_surf)
        self.display_text()


class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0, 2000) == 1:
                self.active = True
