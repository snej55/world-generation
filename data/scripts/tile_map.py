import pygame
import math
import gzip, bz2, lzma
import random
import json

from .bip import TILE_SIZE, TILE_CHUNK_SIZE

AUTO_TILE_MAP = {'0011': 1, '1011': 2, '1001': 3, '0001': 4, '0111': 5, '1111': 6, '1101': 7, '0101': 8, 
                '0110': 9, '1110': 10, '1100': 11, '0100': 12, '0010': 13, '1010': 14, '1000': 15, '0000': 16}
NEIGHBOUR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (0, 0)]
AUTO_TILE_TYPES = {"grass", "stone", "grass_seeds", "dirt", "clay", "sand", "copper", "tin", "iron", "lead", "silver", "tungsten", "gold", "platinum", "wall_tiles/dirt", "wall_tiles/jungle"}

TILE_INFO = {
    'ores': {"copper", "tin", "iron", "lead", "silver", "tungsten", "gold", "platinum"},
    'ore_pairs': [("copper", "tin"), ("iron", "lead"), ("silver", "tungsten"), ("gold", "platinum")]
}

LIGHTING_DIMINISH = 1

class TileMap:
    def __init__(self, app):
        self.app = app
        self.tile_map = {}
        self.tile_size = TILE_SIZE
        self.chunks = {}
        self.light_map = pygame.Surface(app.screen.get_size())
        self.background_light = pygame.Surface(app.screen.get_size())
        self.background_light.fill((0, 0, 0))

    def save(self, mdata, name):
        '''
        Compression algorithm. approx 44:1 compression ratio
        mdata: {'level': {}, 'wall_tiles': {}}
        '''
        with open(f'data/maps/{name}.mterworld', 'wb') as f:
            level = mdata['level']
            wall_tiles = mdata['wall_tiles']
            map_data = {} # return level data
            ref = {'NOTAREF':'NOTAREF'} # reference for compressed {'0x9': 'blocks'}
            tile_type_ref = {} # reference for compression {'blocks': '0x9'}
            slevel = ''
            if level.keys():
                mix, miy = [int(c) - 1 for c in list(level.keys())[-1].split(';')] # min x, min y
                mx, my = [int(c) + 1 for c in list(level.keys())[-1].split(';')] # max x, max y
                for key in level.keys():
                    coord = [int(c) for c in key.split(';')]
                    mix = coord[0] if mix > coord[0] else mix
                    miy = coord[1] if miy > coord[1] else miy
                    mx = coord[0] if mx < coord[0] else mx
                    my = coord[1] if my < coord[1] else my
                if wall_tiles.keys():
                    for key in wall_tiles.keys():
                        coord = [int(c) for c in key.split(';')]
                        mix = coord[0] if mix > coord[0] else mix
                        miy = coord[1] if miy > coord[1] else miy
                        mx = coord[0] if mx < coord[0] else mx
                        my = coord[1] if my < coord[1] else my
                c = 0
                for loc in level:
                    tile = level[loc]
                    if not (tile['type'] in tile_type_ref):
                        ref[str(c)] = tile['type']
                        if tile['type'] == 'wall_tiles/dirt':
                            print('oi', tile, loc)
                        tile_type_ref[tile['type']] = str(c)
                        c += 1
                for loc in wall_tiles:
                    tile = wall_tiles[loc]
                    if not (tile in tile_type_ref):
                        ref[str(c)] = tile
                        tile_type_ref[tile] = str(c)
                        print(tile_type_ref[tile], tile)
                        c += 1
                # loop through all chunks in map
                for y in range(math.floor(miy / TILE_CHUNK_SIZE[1]), math.ceil(my / TILE_CHUNK_SIZE[1])):
                    for x in range(math.floor(mix / TILE_CHUNK_SIZE[0]), math.ceil(mx / TILE_CHUNK_SIZE[0])):
                        chunk_loc = f'{x};{y}' # chunk_coord
                        clevel = '' # compressed level data
                        # do some compression magic
                        n_blank = 0 # num of blank tiles
                        # loop through all tiles in chunk
                        for ty in range(TILE_CHUNK_SIZE[1]):
                            for tx in range(TILE_CHUNK_SIZE[0]):
                                target_x = x * TILE_CHUNK_SIZE[0] + tx
                                target_y = y * TILE_CHUNK_SIZE[1] + ty
                                target_tile_coord = f'{target_x};{target_y}'
                                if target_tile_coord in level:
                                    if n_blank:
                                        clevel += str(n_blank)
                                        clevel += '/'
                                        n_blank = 0
                                    clevel += ';'
                                    tile_type = level[target_tile_coord]['type']
                                    clevel += tile_type_ref[tile_type]
                                    clevel += f':{level[target_tile_coord]["variant"]}'
                                else:
                                    if not n_blank:
                                        clevel += ';'
                                        clevel += '/'
                                        n_blank += 1
                                    else:
                                        n_blank += 1
                        if n_blank:
                            clevel += str(n_blank)
                            clevel += '/'
                            n_blank = 0
                        clevel += ';'
                        map_data[chunk_loc] = clevel
                        clevel = '' # compressed level data
                        # do some compression magic
                        n_blank = 0 # num of blank tiles
                        # loop through all tiles in chunk
                        for wy in range(TILE_CHUNK_SIZE[1]):
                            for wx in range(TILE_CHUNK_SIZE[0]):
                                target_x = x * TILE_CHUNK_SIZE[0] + wx
                                target_y = y * TILE_CHUNK_SIZE[1] + wy
                                target_tile_coord = f'{target_x};{target_y}'
                                if target_tile_coord in wall_tiles:
                                    if n_blank:
                                        clevel += str(n_blank)
                                        clevel += '/'
                                        n_blank = 0
                                    clevel += ';'
                                    tile_type = wall_tiles[target_tile_coord]
                                    clevel += tile_type_ref[tile_type]
                                    clevel += f':#'
                                else:
                                    if not n_blank:
                                        clevel += ';'
                                        clevel += '/'
                                        n_blank += 1
                                    else:
                                        n_blank += 1
                        if n_blank:
                            clevel += str(n_blank)
                            clevel += '/'
                            n_blank = 0
                        clevel += ';'
                        map_data[chunk_loc] += f'!{clevel}'
                type_ref = ''
                for tilet in ref:
                    type_ref += f'{tilet}:{ref[tilet]},'
                slevel += f'{mix}:{miy}:{mx}:{my}:{TILE_CHUNK_SIZE[0]}:{TILE_CHUNK_SIZE[1]}>{type_ref}>'
                for chunk_loc in map_data:
                    slevel += map_data[chunk_loc]
                    slevel += '*'
            print(ref, tile_type_ref, type_ref)
            compressed = gzip.compress(bz2.compress(lzma.compress(bytes(slevel, 'utf-8'))))
            f.write(compressed)
            f.close()
            return slevel

    def load_info(self, mdata):
        tile_map = mdata['level']
        print('Fetched tile_map')
        wall_tiles = mdata['wall_tiles']
        print('Fetched wall tiles')
        self.tile_map = tile_map
        print('Loaded tile_map')
        for loc in wall_tiles:
            wall_tiles[loc] = {'type': wall_tiles[loc], 'variant': 0}
        self.chunks = self.chunk(tile_map, wall_tiles)
        print('Loaded chunks')
        for loc in self.chunks:
            self.auto_tile(loc)
        print('Autotiled chunks')

    def load(self, name):
        with open(f'data/maps/{name}.mterworld', 'rb') as f:
            data = lzma.decompress(bz2.decompress(gzip.decompress(f.read()))).decode('utf-8')

            level_data = {}
            wall_tiles = {}
            type_ref = {pair.split(':')[0]: pair.split(':')[1] for pair in data.split('>')[1].split(',') if pair != ''}
            print(type_ref)
            chunk_size = list(TILE_CHUNK_SIZE)
            mix, miy, mx, my, chunk_size[0], chunk_size[1] = [int(c) for c in data.split('>')[0].split(':')]
            chunk_idx = 0
            print(f'{len(data.split(">")[-1].split("*"))} chunks to go')
            for y in range(math.floor(miy / chunk_size[1]), math.ceil(my / chunk_size[1])):
                for x in range(math.floor(mix / chunk_size[0]), math.ceil(mx / chunk_size[0])):
                    chunk = data.split('>')[-1].split('*')[chunk_idx]
                    chunk_idx += 1
                    tile_idx = 0
                    if not f'/{TILE_CHUNK_SIZE[0] * TILE_CHUNK_SIZE[1]}/' in chunk:
                        for tile in chunk.split('!')[0].split(';'):
                            target_x = x * chunk_size[0] + (tile_idx % chunk_size[0])
                            target_y = y * chunk_size[1] + math.floor(tile_idx / chunk_size[0])
                            target_tile_coord = f'{target_x};{target_y}'
                            if '/' in tile:
                                tile_idx += int(tile.split('/')[1])
                            elif tile != '':
                                tile_type = type_ref[tile.split(':')[0]]
                                tile_variant = tile.split(':')[1]
                                if 'a' in tile_variant:
                                    for _ in range(int(tile_variant.split('a')[1])):
                                        tile_idx += 1
                                        level_data[f'{x * chunk_size[0] + (tile_idx % chunk_size[0])};{y * chunk_size[1] + math.floor(tile_idx / chunk_size[0])}'] = {'type': tile_type, 'variant': tile_variant.split('a')[0]}
                                    tile_variant = tile_variant.split('a')[0]
                                else:
                                    tile_idx += 1
                                level_data[target_tile_coord] = {'type': tile_type, 'variant': tile_variant}
                        tile_idx = 0
                        for tile in chunk.split('!')[1].split(';'):
                            target_x = x * chunk_size[0] + (tile_idx % chunk_size[0])
                            target_y = y * chunk_size[1] + math.floor(tile_idx / chunk_size[0])
                            target_tile_coord = f'{target_x};{target_y}'
                            if '/' in tile:
                                tile_idx += int(tile.split('/')[1])
                            elif tile != '':
                                tile_type = type_ref[tile.split(':')[0]]
                                tile_variant = tile.split(':')[1]
                                if 'a' in tile_variant:
                                    for _ in range(int(tile_variant.split('a')[1])):
                                        tile_idx += 1
                                        wall_tiles[f'{x * chunk_size[0] + (tile_idx % chunk_size[0])};{y * chunk_size[1] + math.floor(tile_idx / chunk_size[0])}'] = {'type': tile_type, 'variant': tile_variant.split('a')[0]}
                                    tile_variant = tile_variant.split('a')[0]
                                else:
                                    tile_idx += 1
                                wall_tiles[target_tile_coord] = {'type': tile_type, 'variant': 0}
                    if chunk_idx % 100 == 0:
                        print(f'{len(data.split(">")[-1].split("*")) - chunk_idx} chunks to go')
            print('loaded tiles')
            chunks = self.chunk(level_data, wall_tiles)
        self.tile_map = level_data
        self.chunks = chunks
        for loc in self.chunks:
            self.auto_tile(loc)

    def load_json(self, path):
        with open(path, 'r') as f:
            level_data = json.load(f)
            chunks = self.chunk(level_data['level'], level_data['wall_tiles'])
            self.tile_map = level_data['level']
            self.chunks = chunks
            #for loc in self.chunks:
            #    self.auto_tile(loc)
            f.close()

    def save_json(self, path):
        with open(path, 'w') as f:
            tile_map = {}
            wall_tiles = {}
            for chunk_loc in self.chunks:
                chunk = self.chunks[chunk_loc]
                for tile_loc in chunk['tile_map']:
                    tile_map[tile_loc] = chunk['tile_map'][tile_loc]
                for wall_tile_loc in chunk['wall_tiles']:
                    wall_tiles[wall_tile_loc] = chunk['wall_tiles'][wall_tile_loc]
            json.dump({'level': tile_map, 'wall_tiles': wall_tiles}, f)
            f.close()

    def chunk(self, level_data, wall_tiles):
        chunks = {}
        for loc in level_data:
            tile_loc = [int(c) * TILE_SIZE for c in loc.split(';')]
            chunk_loc = [math.floor(coord / TILE_CHUNK_SIZE[i] / TILE_SIZE) for i, coord in enumerate(tile_loc)]
            chunk_loc = f'{chunk_loc[0]};{chunk_loc[1]}'
            if not (chunk_loc in chunks):
                chunks[chunk_loc] = {'tile_map': {}, 'tile_img': None, 'wall_tiles': {}, 'wall_img': None, 'img': None, 'background': None, 'lighting': {'queue': [], 'start_queue': [], 'light_map': None}, 'achunk': True}
            chunks[chunk_loc]['tile_map'][loc] = level_data[loc].copy()
        print('Chunked tile_map')
        for loc in wall_tiles:
            tile_loc = [int(c) * TILE_SIZE for c in loc.split(';')]
            chunk_loc = [math.floor(coord / TILE_CHUNK_SIZE[i] / TILE_SIZE) for i, coord in enumerate(tile_loc)]
            chunk_loc = f'{chunk_loc[0]};{chunk_loc[1]}'
            if not (chunk_loc in chunks):
                chunks[chunk_loc] = {'tile_map': {}, 'tile_img': None, 'wall_tiles': {}, 'wall_img': None, 'img': None, 'background': None, 'lighting': {'queue': [], 'start_queue': [], 'light_map': None}, 'achunk': True}
            chunks[chunk_loc]['wall_tiles'][loc] = wall_tiles[loc].copy()
        print('Chunked wall_tiles')
        return chunks

    def update_light_map(self, chunk_loc):
        if chunk_loc in self.chunks:
            chunk = self.chunks[chunk_loc]
            chunk_pos = [int(c) * TILE_SIZE * TILE_CHUNK_SIZE[i] for i, c in enumerate(chunk_loc.split(';'))]
            if chunk_pos[1] <= 200 * TILE_SIZE - TILE_SIZE * TILE_CHUNK_SIZE[1]:
                start_queue = []
                for y in range(TILE_CHUNK_SIZE[1]):
                    for x in range(TILE_CHUNK_SIZE[0]):
                        loc = f'{math.floor(chunk_pos[0] / TILE_SIZE) + x};{math.floor(chunk_pos[1] / TILE_SIZE) + y}'
                        if not loc in chunk['tile_map'] and not (loc in chunk['wall_tiles']):
                            pos = (math.floor(chunk_pos[0] / TILE_SIZE) + x, math.floor(chunk_pos[1] / TILE_SIZE) + y)
                            start_queue.append(pos)
                if chunk['achunk']:
                    for shift in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        achunk = f'{math.floor(chunk_pos[0] / TILE_SIZE / TILE_CHUNK_SIZE[0]) + shift[0]};{math.floor(chunk_pos[1] / TILE_SIZE / TILE_CHUNK_SIZE[1]) + shift[1]}'
                        if not achunk in self.chunks:
                            self.chunks[achunk] = {'tile_map': {}, 'tile_img': None, 'wall_tiles': {}, 'wall_img': None, 'img': None, 'background': None, 'lighting': {'queue': [], 'start_queue': [], 'light_map': None}, 'achunk': False}
                chunk['lighting']['start_queue'].extend(start_queue)

    def render_light_map(self, chunk_loc):
        if chunk_loc in self.chunks:
            chunk = self.chunks[chunk_loc]
            chunk_chunk_loc = [int(c) for c in chunk_loc.split(';')]
            chunk_tile_pos = [int(c) * TILE_CHUNK_SIZE[i] for i, c in enumerate(chunk_loc.split(';'))]
            if not chunk['lighting']['light_map']:
                chunk['lighting']['light_map'] = pygame.Surface((TILE_SIZE * TILE_CHUNK_SIZE[0], TILE_SIZE * TILE_CHUNK_SIZE[1]))
            chunk['lighting']['light_map'].fill((255, 255, 255))
            #if len(chunk['lighting']['start_queue']):
            #    for pos in chunk['lighting']['start_queue']:
            #        pygame.draw.rect(chunk['lighting']['light_map'], (0, 255, 255), ((pos[0] - chunk_tile_pos[0]) * TILE_SIZE, (pos[1] - chunk_tile_pos[1]) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if len(chunk['lighting']['queue']) or len(chunk['lighting']['start_queue']):
                lighting = {f'{x + chunk_tile_pos[0]};{y + chunk_tile_pos[1]}': [0, []] for x in range(TILE_CHUNK_SIZE[0]) for y in range(TILE_CHUNK_SIZE[1])}
                day_light = 15
                light_id = 1
                if len(chunk['lighting']['start_queue']):
                    chunk['lighting']['queue'].extend([(pos, day_light) for pos in chunk['lighting']['start_queue']])
                while len(chunk['lighting']['queue']):
                    for i, light in sorted(enumerate(chunk['lighting']['queue']), reverse=True):
                        loc = f'{light[0][0]};{light[0][1]}'
                        if loc in chunk['tile_map']:
                            light[1] -= LIGHTING_DIMINISH
                        if not light_id in lighting[loc][1]:
                            lighting[loc][0] += light[1]
                        light_intensity =  255 - max(0, min(255, 255 * lighting[loc][0] / 15))
                        pygame.draw.rect(chunk['lighting']['light_map'], (light_intensity, light_intensity, light_intensity), ((light[0][0] - chunk_tile_pos[0]) * TILE_SIZE, (light[0][1] - chunk_tile_pos[1]) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                        lighting[loc][1].append(light_id)
                        if light[1] - LIGHTING_DIMINISH > 0:
                            for shift in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                                tloc = f'{light[0][0] + shift[0]};{light[0][1] + shift[1]}'
                                if tloc in lighting:
                                    if not (light_id in lighting[tloc][1]):
                                        chunk['lighting']['queue'].append([[light[0][0] + shift[0], light[0][1] + shift[1]], light[1] - LIGHTING_DIMINISH])
                                elif f'{chunk_chunk_loc[0] + shift[0]};{chunk_chunk_loc[1] + shift[1]}' in self.chunks:
                                    achunk = self.chunks[f'{chunk_chunk_loc[0] + shift[0]};{chunk_chunk_loc[1] + shift[1]}']
                                    if loc in chunk['tile_map']:
                                        achunk['lighting']['queue'].append([[light[0][0] + shift[0], light[0][1] + shift[1]], light[1] + LIGHTING_DIMINISH * 2])
                                    else:
                                        achunk['lighting']['queue'].append([[light[0][0] + shift[0], light[0][1] + shift[1]], light[1] + LIGHTING_DIMINISH])
                        chunk['lighting']['queue'].pop(i)

    def render_chunk_tiles(self, chunk_loc):
        if chunk_loc in self.chunks:
            if not self.chunks[chunk_loc]['tile_img']:
                self.chunks[chunk_loc]['tile_img'] = pygame.Surface((TILE_SIZE * TILE_CHUNK_SIZE[0], TILE_SIZE * TILE_CHUNK_SIZE[1]))
                self.chunks[chunk_loc]['tile_img'].set_colorkey((0, 0, 0))  # removes transparent sections when rendering tiles
            self.chunks[chunk_loc]['tile_img'].fill((0, 0, 0))
            chunk_aloc = [int(c) * TILE_SIZE * TILE_CHUNK_SIZE[i] for i, c in enumerate(chunk_loc.split(';'))]
            for loc in self.chunks[chunk_loc]['tile_map']:
                tile = self.chunks[chunk_loc]['tile_map'][loc]
                tile_loc = [int(co) for co in loc.split(';')]
                try:
                    self.chunks[chunk_loc]['tile_img'].blit(self.app.assets[f'tiles/{tile["type"]}'][tile['variant']], (tile_loc[0] * TILE_SIZE - chunk_aloc[0], tile_loc[1] * TILE_SIZE - chunk_aloc[1]))
                except TypeError:
                    print(tile)

    def render_chunk_wall_tiles(self, chunk_loc):
        if chunk_loc in self.chunks:
            if not self.chunks[chunk_loc]['wall_img']:
                self.chunks[chunk_loc]['wall_img'] = pygame.Surface((TILE_SIZE * TILE_CHUNK_SIZE[0], TILE_SIZE * TILE_CHUNK_SIZE[1]))
                self.chunks[chunk_loc]['wall_img'].set_colorkey((0, 0, 0))  # removes transparent sections when rendering tiles
            self.chunks[chunk_loc]['wall_img'].fill((0, 0, 0))
            chunk_aloc = [int(c) * TILE_SIZE * TILE_CHUNK_SIZE[i] for i, c in enumerate(chunk_loc.split(';'))]
            for loc in self.chunks[chunk_loc]['wall_tiles']:
                tile = self.chunks[chunk_loc]['wall_tiles'][loc]
                tile_loc = [int(co) for co in loc.split(';')]
                try:
                    self.chunks[chunk_loc]['wall_img'].blit(self.app.assets[f'{tile["type"]}'][tile['variant']], (tile_loc[0] * TILE_SIZE - chunk_aloc[0], tile_loc[1] * TILE_SIZE - chunk_aloc[1]))
                except TypeError:
                    print(tile)

    def render_chunk_background(self, chunk_loc):
        if chunk_loc in self.chunks:
            chunk = self.chunks[chunk_loc]
            chunk_pos = [int(c) * TILE_SIZE * TILE_CHUNK_SIZE[i] for i, c in enumerate(chunk_loc.split(';'))]
            if chunk_pos[1] >= 200 * TILE_SIZE - TILE_SIZE * TILE_CHUNK_SIZE[1]:
                if not chunk['background']:
                    chunk['background'] = pygame.Surface((TILE_SIZE * TILE_CHUNK_SIZE[0], TILE_SIZE * TILE_CHUNK_SIZE[1]))
                bg = self.app.assets['background/cavern']
                width, height = bg.get_size()
                for y in range(math.ceil((TILE_SIZE * TILE_CHUNK_SIZE[1] + (chunk_pos[1] % height)) / height) + 1):
                    for x in range(math.ceil((TILE_SIZE * TILE_CHUNK_SIZE[0] + (chunk_pos[0] % width)) / width) + 1):
                        chunk['background'].blit(bg, (-(chunk_pos[0] % width) + x * width, -(chunk_pos[1] % height) + height * y))

    def render_chunk(self, chunk_loc):
        self.render_chunk_wall_tiles(chunk_loc)
        self.render_chunk_tiles(chunk_loc)
        if not self.chunks[chunk_loc]['img']:
            self.chunks[chunk_loc]['img'] = pygame.Surface((TILE_SIZE * TILE_CHUNK_SIZE[0], TILE_SIZE * TILE_CHUNK_SIZE[1]))
            self.chunks[chunk_loc]['img'].set_colorkey((0, 0, 0))  # removes transparent sections when rendering tiles
            self.render_chunk_background(chunk_loc)
        if self.chunks[chunk_loc]['background']:
            self.chunks[chunk_loc]['img'].blit(self.chunks[chunk_loc]['background'], (0, 0))
        if not self.chunks[chunk_loc]['lighting']['light_map']:
            self.update_light_map(chunk_loc)
            self.render_light_map(chunk_loc)
        self.chunks[chunk_loc]['img'].blit(self.chunks[chunk_loc]['wall_img'], (0, 0))
        self.chunks[chunk_loc]['img'].blit(self.chunks[chunk_loc]['tile_img'], (0, 0))

    def render_lighting(self, chunk_loc):
        if chunk_loc in self.chunks:
            chunk = self.chunks[chunk_loc]

    def auto_tile(self, chunk_loc):
        self.auto_tile_tiles(chunk_loc)
        self.auto_tile_wall_tiles(chunk_loc)

    def auto_tile_tiles(self, chunk_loc):
        if chunk_loc in self.chunks:
            for loc in self.chunks[chunk_loc]['tile_map']:
                tile = self.chunks[chunk_loc]['tile_map'][loc]
                tile_pos = [int(c) * TILE_SIZE for c in loc.split(';')]
                aloc = ''
                for shift in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                    check_loc = str(math.floor(tile_pos[0] / TILE_SIZE) + shift[0]) + ';' + str(math.floor(tile_pos[1] / TILE_SIZE) + shift[1])
                    if check_loc in self.chunks[chunk_loc]['tile_map']:
                        if self.chunks[chunk_loc]['tile_map'][check_loc]['type'] == tile['type'] or (self.chunks[chunk_loc]['tile_map'][check_loc]['type'] in AUTO_TILE_TYPES):
                            aloc += '1'
                        else:
                            aloc += '0'
                    else:
                        chunk_pos = [int(c) + shift[i] for i, c in enumerate(chunk_loc.split(';'))]
                        chunk_shift_loc = f'{chunk_pos[0]};{chunk_pos[1]}'
                        if chunk_shift_loc in self.chunks:
                            if check_loc in self.chunks[chunk_shift_loc]['tile_map']:
                                if self.chunks[chunk_shift_loc]['tile_map'][check_loc]['type'] == tile['type'] or (self.chunks[chunk_shift_loc]['tile_map'][check_loc]['type'] in AUTO_TILE_TYPES):
                                    aloc += '1'
                                else:
                                    aloc += '0'
                            else:
                                aloc += '0'
                        else:
                            aloc += '0'
                if tile['type'] in AUTO_TILE_TYPES:
                    tile['variant'] = AUTO_TILE_MAP[aloc] - 1
                else:
                    tile['variant'] = int(tile_variant)

    def auto_tile_wall_tiles(self, chunk_loc):
        if chunk_loc in self.chunks:
            for loc in self.chunks[chunk_loc]['wall_tiles']:
                tile = self.chunks[chunk_loc]['wall_tiles'][loc]
                tile_pos = [int(c) * TILE_SIZE for c in loc.split(';')]
                aloc = ''
                for shift in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                    check_loc = str(math.floor(tile_pos[0] / TILE_SIZE) + shift[0]) + ';' + str(math.floor(tile_pos[1] / TILE_SIZE) + shift[1])
                    if check_loc in self.chunks[chunk_loc]['wall_tiles']:
                        if self.chunks[chunk_loc]['wall_tiles'][check_loc]['type'] == tile['type'] or (self.chunks[chunk_loc]['wall_tiles'][check_loc]['type'] in AUTO_TILE_TYPES):
                            aloc += '1'
                        else:
                            aloc += '0'
                    else:
                        chunk_pos = [int(c) + shift[i] for i, c in enumerate(chunk_loc.split(';'))]
                        chunk_shift_loc = f'{chunk_pos[0]};{chunk_pos[1]}'
                        if chunk_shift_loc in self.chunks:
                            if check_loc in self.chunks[chunk_shift_loc]['wall_tiles']:
                                if self.chunks[chunk_shift_loc]['wall_tiles'][check_loc]['type'] == tile['type'] or (self.chunks[chunk_shift_loc]['wall_tiles'][check_loc]['type'] in AUTO_TILE_TYPES):
                                    aloc += '1'
                                else:
                                    aloc += '0'
                            else:
                                aloc += '0'
                        else:
                            aloc += '0'
                if tile['type'] in AUTO_TILE_TYPES:
                    tile['variant'] = AUTO_TILE_MAP[aloc] - 1
                else:
                    tile['variant'] = int(tile_variant)

    def draw(self, surf, scroll):
        self.light_map.fill((0, 0, 0))
        for y in range(math.floor(scroll[1] / TILE_SIZE / TILE_CHUNK_SIZE[1]), math.floor((scroll[1] + surf.get_height()) / TILE_SIZE / TILE_CHUNK_SIZE[1]) + 1):
            for x in range(math.floor(scroll[0] / TILE_SIZE / TILE_CHUNK_SIZE[0]), math.floor((scroll[0] + surf.get_width()) / TILE_SIZE / TILE_CHUNK_SIZE[0]) + 1):
                chunk_loc = f'{x};{y}'
                if chunk_loc in self.chunks:
                    chunk = self.chunks[chunk_loc]
                    if not chunk['img']:
                        self.render_chunk(chunk_loc)
                    surf.blit(chunk['img'], (x * TILE_SIZE * TILE_CHUNK_SIZE[0] - scroll[0], y * TILE_SIZE * TILE_CHUNK_SIZE[1] - scroll[1]))
                    self.light_map.blit(chunk['lighting']['light_map'], (x * TILE_SIZE * TILE_CHUNK_SIZE[0] - scroll[0], y * TILE_SIZE * TILE_CHUNK_SIZE[1] - scroll[1]))
                else:
                    self.light_map.blit(self.background_light, (x * TILE_SIZE * TILE_CHUNK_SIZE[0] - scroll[0], y * TILE_SIZE * TILE_CHUNK_SIZE[1] - scroll[1]))
        return self.light_map