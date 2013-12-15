import sys
from collections import namedtuple

Asakura_Map = namedtuple('Map',
              ['tileset_name', 'background_name', 'background_music_name',
               'tiles', 'enemies', 'items', 'moving_tiles', 'doors',
               'bubble_key', 'key', 'chest', 'enemy_set', 'time',
               'jump_reduction', 'inertia']
          )
