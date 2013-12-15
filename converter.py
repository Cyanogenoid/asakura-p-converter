import sys
import struct
from collections import namedtuple

Asakura_Map = namedtuple('Map',
              ['tileset_name', 'background_name', 'background_music_name',
               'tiles', 'enemies', 'items', 'moving_tiles', 'doors',
               'bubble_key', 'key', 'chest', 'enemy_set', 'time',
               'jump_reduction', 'inertia']
          )

def read_ints(fd, byte_count):
    return struct.unpack('i' * byte_count, fd.read(4 * byte_count))

def read_string(fd, length):
    return fd.read(length)

def skip_bytes(fd, byte_count):
    fd.seek(byte_count, 1)
