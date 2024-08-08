from settings import *
from random import randint
from groups import WorldSprites
from sprites import Sprite, AnimatedSprite, Node, Icon


class Overworld:
    def __init__(self, tmx_map, data, overworld_frames):
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.data = data

        self.all_sprites = WorldSprites(self.data)

        self.icon = None
        self.setup(tmx_map, overworld_frames)

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



        for obj in tmx_map.get_layer_by_name('Nodes'):
            if obj.name == "Node":
                Node((obj.x, obj.y), overworld_frames['path']['node'], self.all_sprites, obj.properties['stage'], self.data)

            if obj.name == "Node" and obj.properties['stage'] == self.data.current_level:
                self.icon = Icon((obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), self.all_sprites, overworld_frames['icon'])

    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.icon.rect.center)
