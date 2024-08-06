import pygame.sprite

from settings import *


class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, z=Z_LAYERS['main'], hit_player=Nonedddddddddddd):
        # noinspection PyTypeChecker
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]

        self.rect = self.image.get_frect(topleft=pos)
        self.z = z
        self.direction = choice((-1, 1))

        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 200

        self.hit_player = hit_player

    def update(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

        self.image = pygame.transform.flip(self.image, self.direction == -1, False)

        self.rect.x += self.direction * self.speed * dt

        floor_rect_right = pygame.FRect(self.rect.bottomright, (1, 1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1, 1))

        rect_right = pygame.FRect(self.rect.topright, (1, 1))
        rect_left = pygame.FRect(self.rect.topleft, (-1, 1))

        if floor_rect_right.collidelist(self.collision_rects) < 0 < self.direction or rect_right.collidelist(self.collision_rects) >= 0:
            self.direction = -1
        if floor_rect_left.collidelist(self.collision_rects) < 0 > self.direction or rect_left.collidelist(self.collision_rects) >= 0:
            self.direction = 1

        self.hit_player(self.rect)


class Shell(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, reverse, player, create_pearl):
        # noinspection PyTypeChecker
        super().__init__(groups)

        self.pearl = frames['pearl']

        self.frames, self.frame_index = frames['shell'], 0
        self.state = 'idle'

        self.bullet_direction = -1 if reverse else 1
        self.image = pygame.transform.flip(self.frames[self.state][self.frame_index], reverse, False)
        self.reversed = reverse

        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()

        self.z = Z_LAYERS['main']

        self.player = player

        self.shoot_timer = Timer(3000)
        self.has_fired = False
        self.create_pearl = create_pearl

    def state_management(self):
        player_pos, shell_pos = Vector2(self.player.hitbox.center), Vector2(self.rect.center)
        player_near = shell_pos.distance_to(player_pos) < 500

        player_front = shell_pos.x < player_pos.x if self.bullet_direction > 0 else shell_pos.x > player_pos.x
        player_level = abs(shell_pos.y - player_pos.y) < 30

        if player_near and player_front and player_level and not self.shoot_timer.active:
            self.state = 'fire'
            self.shoot_timer.activate()

    def update(self, dt):
        self.state_management()
        self.shoot_timer.update()

        self.frame_index += ANIMATION_SPEED * dt

        if int(self.frame_index) < len(self.frames[self.state]):

            frame = pygame.transform.flip(self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])],
                                          self.reversed, False)
            self.image = frame

            if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
                self.has_fired = True
                self.create_pearl(self.rect.center, self.bullet_direction, self.pearl)

        else:
            self.frame_index = 0
            if self.state == 'fire':
                self.state = 'idle'
                self.has_fired = False


class Pearl(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surf, direction, speed, collide_sprites, player, coll):
        # noinspection PyTypeChecker
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos + Vector2(50 * direction, 10))

        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']

        self.collide_sprites = collide_sprites
        self.player = player

        self.life = Timer(5000)
        self.life.activate()

        self.collision_hit = coll

    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt

        for sprite in self.collide_sprites:
            if sprite.__class__ != Shell:
                if self.rect.colliderect(sprite.rect):
                    self.kill()
                    break
                elif self.rect.colliderect(self.player.hitbox):
                    self.kill()
                    self.collision_hit()

        if self.life.active:
            self.life.update()
        else:
            self.kill()
