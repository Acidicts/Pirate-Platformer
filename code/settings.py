import os
import pygame
from pygame.math import Vector2

from timer import *


BASE_PATH = os.path.dirname(__file__).replace('\\',
                                              '/').replace('code',
                                                           '').replace('"Pirate Platformer"/',
                                                                       '"Pirate Platformer"')

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 64
ANIMATION_SPEED = 6

# layers 
Z_LAYERS = {
    'bg': 0,
    'clouds': 1,
    'bg tiles': 2,
    'path': 3,
    'bg details': 4,
    'main': 5,
    'water': 6,
    'fg': 7
}
