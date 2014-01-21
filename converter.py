import argparse
import os.path
import struct
from collections import namedtuple, defaultdict
from functools import partial

import tmxlib

Asakura_Map = namedtuple('Map', [
    'tileset_name', 'background_name', 'background_music_name',
    'tiles', 'enemies', 'items', 'moving_tiles', 'doors',
    'bubble_key', 'key', 'chest', 'enemy_set', 'time',
    'jump_reduction', 'inertia'])


property_map = defaultdict(int)
property_map.update({
    120: 17
})


def read_ints(fd, words):
    byte_pack = struct.unpack('i' * words, fd.read(4 * words))
    return [int(i) for i in byte_pack]


def read_string(fd, length):
    return fd.read(length).decode('utf-8')


def skip_bytes(fd, words):
    fd.seek(int(words * 4), 1)


def load_askm(path):
    with open(path, 'rb') as f:
        return parse_askm(f)


def parse_askm(fd):
    skip_bytes(fd, words=1)

    tileset_length, = read_ints(fd, words=1)
    tileset_name = read_string(fd, length=tileset_length)
    skip_bytes(fd, words=1/4)  # skip null byte

    background_length, = read_ints(fd, words=1)
    background_name = read_string(fd, length=background_length)
    skip_bytes(fd, words=1/4)  # skip null byte

    background_music_length, = read_ints(fd, words=1)
    background_music_name = read_string(fd, length=background_music_length)
    skip_bytes(fd, words=1/4)  # skip null byte

    # tiles
    tiles = dict()
    for row in range(48):
        for column in range(77):
            tile_appearance, tile_property = read_ints(fd, 2)
            tiles[row, column] = tile_appearance, tile_property
        skip_bytes(fd, words=2)  # skip padding column

    skip_bytes(fd, words=256)

    # enemies
    enemies = dict()
    enemy_count, = read_ints(fd, words=1)
    for _ in range(enemy_count):
        enemy_column, enemy_row, enemy_id = read_ints(fd, 3)
        enemies[enemy_row, enemy_column] = enemy_id

    # enemy set
    enemy_set, = read_ints(fd, words=1)

    # items
    items = dict()
    item_count, = read_ints(fd, words=1)
    for _ in range(item_count):
        item_column, item_row, item_id = read_ints(fd, words=3)
        items[item_column, item_row] = item_id

    # bubble key
    skip_bytes(fd, words=1)
    bubble_key = read_ints(fd, words=3)

    # bubble key
    skip_bytes(fd, words=1)
    key = read_ints(fd, words=3)

    # chest
    skip_bytes(fd, words=1)
    chest = read_ints(fd, words=3)

    skip_bytes(fd, words=8)

    # moving tiles
    moving_tiles = dict()
    moving_tiles_count, = read_ints(fd, words=1)
    for _ in range(moving_tiles_count):
        moving_row, moving_column, moving_id = read_ints(fd, words=3)
        moving_tiles[moving_column, moving_row] = moving_id

    # jump reduction
    jump_reduction, = read_ints(fd, words=1)

    skip_bytes(fd, words=3)

    # inertia
    inertia, = read_ints(fd, words=1)

    skip_bytes(fd, words=2)

    # doors
    doors = dict()
    for i in range(4):
        door_id, target_door = read_ints(fd, words=2)
        doors[i] = door_id, target_door

    skip_bytes(fd, words=1)

    time, = read_ints(fd, words=1)

    return Asakura_Map(tileset_name, background_name, background_music_name,
                       tiles, enemies, items, moving_tiles, doors,
                       bubble_key, key, chest,
                       enemy_set, time,
                       jump_reduction, inertia)


def askm_to_tmx(askm, resource_path=''):
    # load template tmx
    tmx = tmxlib.Map(size=(78, 48), tile_size=(32, 32))

    resource_path_gen = partial(os.path.join, resource_path)

    # load tile tileset
    tiles_tileset_path = resource_path_gen(
                            askm.tileset_name.replace('.png', '.tsx')
                         )
    tiles_tileset = tmxlib.tileset.ImageTileset.open(tiles_tileset_path)

    # load properties tileset
    properties_tileset_path = resource_path_gen(tiles_tileset_path)
    properties_tileset = tmxlib.tileset.ImageTileset.open(
                             properties_tileset_path
                         )

    # load items tileset
    items_tileset_path = resource_path_gen('pat_item.tsx')
    items_tileset = tmxlib.tileset.ImageTileset.open(items_tileset_path)

    # create new tmx tileset list
    tmx.tilesets = tmxlib.tileset.TilesetList(tmx)

    # add tilesets to tmx
    tmx.tilesets.append(tiles_tileset)
    tmx.tilesets.append(properties_tileset)
    tmx.tilesets.append(items_tileset)

    # copy all askm tiles into a 'tiles' layer and
    # move properties into a separate layer
    tmx.add_layer('tiles')
    tmx.add_layer('properties')
    tiles_layer = tmx.layers['tiles']
    properties_layer = tmx.layers['properties']
    for position, tile in askm.tiles.items():
        x, y = reversed(position)

        tile_gid = tiles_tileset[tile[0]]
        tiles_layer[x, y] = tile_gid

        property_gid = properties_tileset[property_map[tile[1]]]
        properties_layer[x, y] = property_gid

    # copy all askm items into a 'items' layer
    tmx.add_layer('items')
    items_layer = tmx.layers['items']
    for position, item in askm.items.items():
        # ugly hack, an item row in the tileset has 6 images in it
        item_gid = items_tileset[item * 6]
        # for some reason position is not reversed here?
        items_layer[position] = item_gid

    # set properties that can't be stored elsewhere in the map
    tmx.properties = {
        'jump_reduction': str(askm.jump_reduction),
        'inertia': str(askm.inertia),
    }

    return tmx


def make_tileset(name, image_path, tile_size=(32,32)):
    image = tmxlib.image.open(image_path)
    tileset = tmxlib.ImageTileset(name=name, tile_size=tile_size, image=image)

    return tileset


def apply_terrain(tileset, terrain):
    pass


parser = argparse.ArgumentParser(description='Convert Asakura! P .map files'
                                             'to and from Tiled .tmx files')
parser.add_argument('input_path', help='path where the input map is located')
parser.add_argument('output_path', help='path where the output will be saved')
parser.add_argument('-r', '--resource', help='path where resources are located')
args = parser.parse_args()

askm = load_askm(args.input_path)
tmx = askm_to_tmx(askm, resource_path=args.resource)
tmx.save(args.output_path)
