import pygame.sprite

from settings import *
from random import randint
from groups import WorldSprites
from sprites import Sprite, AnimatedSprite, Node, Icon, PathSprite


class Overworld:
    def __init__(self, tmx_map, data, overworld_frames, switch_stage):
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.data = data
        self.switch_stage = switch_stage

        self.all_sprites = WorldSprites(self.data)
        self.node_sprites = pygame.sprite.Group()

        self.paths = None
        self.icon = None

        self.setup(tmx_map, overworld_frames)

        self.current_node = [node for node in self.node_sprites if node.level == 0][0]

        self.path_frames = overworld_frames['path']
        self.create_path_tiles()

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

    def create_path_tiles(self):

        nodes = {node.level: Vector2(node.grid_pos) for node in self.node_sprites}
        path_tiles = {}

        for path_id, data in self.paths.items():
            path = data['pos']
            start_node, end_node = nodes[data['start']], nodes[path_id]
            path_tiles[path_id] = start_node
            path_tiles[path_id] = [start_node]

            for index, points in enumerate(path):
                if index < len(path) - 1:

                    start, end = Vector2(points), Vector2(path[index + 1])

                    path_dir = (end - start) / TILE_SIZE
                    start_tile = Vector2(int(start[0] / TILE_SIZE), int(start[1] / TILE_SIZE))

                    if path_dir.y:
                        dir_y = 1 if path_dir.y > 0 else -1
                        for y in range(dir_y, int(path_dir.y) + dir_y, dir_y):
                            path_tiles[path_id].append(start_tile + Vector2(0, y))

                    if path_dir.x:
                        dir_x = 1 if path_dir.x > 0 else -1
                        for x in range(dir_x, int(path_dir.x) + dir_x, dir_x):
                            path_tiles[path_id].append(start_tile + Vector2(x, 0))

            path_tiles[path_id].append(end_node)

        for key, path in path_tiles.items():
            for index, tile in enumerate(path):
                if 0 < index < len(path) - 1:
                    prev_tile = path[index - 1] - tile
                    next_tile = path[index + 1] - tile

                    if prev_tile.x == next_tile.x:
                        surf = self.path_frames['vertical']
                    elif prev_tile.y == next_tile.y:
                        surf = self.path_frames['horizontal']
                    else:
                        if int(prev_tile.x) == -1 and int(next_tile.y) == -1 or int(prev_tile.y) == -1 and int(
                                next_tile.x) == -1:
                            surf = self.path_frames['tl']
                        elif int(prev_tile.x) == 1 and int(next_tile.y) == 1 or int(prev_tile.y) == 1 and int(
                                next_tile.x) == 1:
                            surf = self.path_frames['br']
                        elif int(prev_tile.x) == -1 and int(next_tile.y) == 1 or int(prev_tile.y) == 1 and int(
                                next_tile.x) == -1:
                            surf = self.path_frames['bl']
                        elif int(prev_tile.x) == 1 and int(next_tile.y) == -1 or int(prev_tile.y) == -1 and int(
                                next_tile.x) == 1:
                            surf = self.path_frames['tr']
                        else:
                            surf = self.path_frames['horizontal']

                    PathSprite((tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                               surf, self.all_sprites, key)

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
            if keys[pygame.K_RETURN]:
                self.data.current_level = self.current_node.level
                self.switch_stage('level', self.current_node.level)

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
