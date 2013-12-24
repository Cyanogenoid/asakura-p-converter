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

def load_map(fd):
    skip_bytes(fd, byte_count = 4)

    tileset_length, = read_ints(fd, byte_count = 1)
    tileset_name = read_string(fd, length = tileset_length)
    skip_bytes(fd, byte_count = 1) # skip null byte

    background_length, = read_ints(fd, byte_count = 1)
    background_name = read_string(fd, length = background_length)
    skip_bytes(fd, byte_count = 1) # skip null byte

    background_music_length, = read_ints(fd, byte_count = 1)
    background_music_name = read_string(fd, length = background_music_length)
    skip_bytes(fd, byte_count = 1) # skip null byte

    # tiles
    tiles = dict()
    for row in range(48):
        for column in range(77):
            tile_appearance, tile_property = read_ints(fd, 2)
            tiles[row, column] = tile_appearance, tile_property
        skip_bytes(fd, 8) # skip padding column

    skip_bytes(fd, byte_count = 1024)

    # enemies
    enemies = dict()
    enemy_count, = read_ints(fd, byte_count = 1)
    for _ in range(enemy_count):
        enemy_column, enemy_row, enemy_id = read_ints(fd, 3)
        enemies[enemy_row, enemy_column] = enemy_id

    # enemy set
    enemy_set, = read_ints(fd, byte_count = 1)

    # items
    items = dict()
    item_count, = read_ints(fd, byte_count = 1)
    for _ in range(item_count):
        item_column, item_row, item_id = read_ints(fd, byte_count = 3)
        items[item_column, item_row] = item_id

    # bubble key
    has_bubble_key = read_ints(fd, byte_count = 1)
    bubble_key = read_ints(fd, byte_count = 3)

    # bubble key
    has_key = read_ints(fd, byte_count = 1)
    key = read_ints(fd, byte_count = 3)

    # chest
    has_chest = read_ints(fd, byte_count = 1)
    chest = read_ints(fd, byte_count = 3)

    skip_bytes(fd, byte_count = 32)

    # moving tiles
    moving_tiles = dict()
    moving_tiles_count, = read_ints(fd, byte_count = 1)
    for _ in range(moving_tiles_count):
        moving_row, moving_column, moving_id = read_ints(fd, byte_count = 3)
        moving_tiles[moving_column, moving_row] = moving_id

    # jump reduction
    jump_reduction, = read_ints(fd, byte_count = 1)

    skip_bytes(fd, byte_count = 12)

    # inertia
    inertia, = read_ints(fd, byte_count = 1)

    skip_bytes(fd, byte_count = 8)

    # doors
    doors = dict()
    for i in range(4):
        door_id, target_door = read_ints(fd, byte_count = 2)
        doors[i] = door_id, target_door

    skip_bytes(fd, 4)

    time, = read_ints(fd, byte_count = 1)

    return Asakura_Map(tileset_name, background_name, background_music_name,
                       tiles, enemies, items, moving_tiles, doors,
                       bubble_key, key, chest,
                       enemy_set, time,
                       jump_reduction, inertia)
