import pygame.sprite

from settings import *
from random import randint
from groups import WorldSprites
from sprites import Sprite, AnimatedSprite, Node, Icon


class Overworld:
    def __init__(self, tmx_map, data, overworld_frames):
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.data = data

        self.all_sprites = WorldSprites(self.data)
        self.node_sprites = pygame.sprite.Group()

        self.paths = None
        self.icon = None

        self.setup(tmx_map, overworld_frames)

        self.current_node = [node for node in self.node_sprites if node.level == 0][0]

    def setup(self, tmx_map, overworld_frames):
        for layer in ['main', 'top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, Z_LAYERS['bg tiles'])

        for col in range(tmx_map.width):
            for row in range(tmx_map.height):
                AnimatedSprite((col * TILE_SIZE, row * TILE_SIZE), overworld_frames['water'], self.all_sprites,
                               Z_LAYERS['bg'])

        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'palm':
                AnimatedSprite((obj.x, obj.y), overworld_frames['palms'], self.all_sprites, Z_LAYERS['main'],
                               randint(4, 6))
            else:
                z = Z_LAYERS[f'{'bg details' if obj.name == 'grass' else 'bg tiles'}']
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, Z_LAYERS['main'])

        self.paths = {}
        for obj in tmx_map.get_layer_by_name('Paths'):
            pos = [(p.x, p.y) for p in obj.points]
            start = obj.properties['start']
            end = obj.properties['end']
            self.paths[end] = {'pos': pos, 'start': start}

        for obj in tmx_map.get_layer_by_name('Nodes'):

            if obj.name == "Node" and obj.properties['stage'] == self.data.current_level:
                self.icon = Icon((obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), self.all_sprites, overworld_frames['icon'])

            if obj.name == "Node":
                available_paths = {k: v for k, v in obj.properties.items() if k in ('left', 'right', 'up', 'down')}
                Node((obj.x, obj.y), overworld_frames['path']['node'], (self.all_sprites, self.node_sprites),
                     obj.properties['stage'], self.data, available_paths)

    def input(self):
        keys = pygame.key.get_pressed()

        if self.current_node and not self.icon.path:
            if keys[pygame.K_s] and self.current_node.can_move('down'):
                self.move('down')
            if keys[pygame.K_w] and self.current_node.can_move('up'):
                self.move('up')
            if keys[pygame.K_a] and self.current_node.can_move('left'):
                self.move('left')
            if keys[pygame.K_d] and self.current_node.can_move('right'):
                self.move('right')

    def move(self, direction):
        path_key = int(self.current_node.paths[direction][0])
        path_reverse = True if self.current_node.paths[direction][-1] == "r" else False
        path = self.paths[path_key]['pos'][:] if not path_reverse else self.paths[path_key]['pos'][::-1]
        self.icon.start_move(path)

    def get_current_node(self):
        nodes = pygame.sprite.spritecollide(self.icon, self.node_sprites, False)
        if nodes:
            self.current_node = nodes[0]

    def run(self, dt):
        self.input()
        self.get_current_node()
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.icon.rect.center)
