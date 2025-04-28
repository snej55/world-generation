import pygame
import time
import sys
import json
import math

from world_gen import WorldGen
from data.scripts.util import load_tile_assets, load_img
from data.scripts.bip import WIDTH, HEIGHT, TILE_SIZE
from data.scripts.tile_map import TileMap
from data.scripts.mgl import MGL

class App:
    def __init__(self):
        self.display = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.DOUBLEBUF | pygame.OPENGL)
        self.screen = pygame.Surface((WIDTH, HEIGHT))

        self.vaos = {}
        self.mgl = MGL()
        #self.vaos['shader'] = self.mgl.default_ro()
        self.add_shader('shader', 'data/scripts/shaders/blur.frag', 'data/scripts/shaders/default.vert')

        self.clock = pygame.time.Clock()
        self.dt = 1
        self.last_time = time.time() - 1/60

        self.running = True

        self.scroll = pygame.Vector2(0, 600)
        self.render_scroll = [0, 0]

        self.assets = {
            'tiles/grass': load_tile_assets('env/tiles/grass.png', TILE_SIZE),
            'tiles/stone': load_tile_assets('env/tiles/stone.png', TILE_SIZE),
            'tiles/grass_seeds': load_tile_assets('env/tiles/grass_seeds.png', TILE_SIZE),
            'tiles/dirt': load_tile_assets('env/tiles/dirt.png', TILE_SIZE),
            'tiles/clay': load_tile_assets('env/tiles/clay.png', TILE_SIZE),
            'tiles/copper': load_tile_assets('env/tiles/copper.png', TILE_SIZE),
            'tiles/tin': load_tile_assets('env/tiles/tin.png', TILE_SIZE),
            'tiles/sand': load_tile_assets('env/tiles/sand.png', TILE_SIZE),
            'tiles/iron': load_tile_assets('env/tiles/iron.png', TILE_SIZE),
            'tiles/lead': load_tile_assets('env/tiles/lead.png', TILE_SIZE),
            'tiles/platinum': load_tile_assets('env/tiles/platinum.png', TILE_SIZE),
            'tiles/tungsten': load_tile_assets('env/tiles/tungsten.png', TILE_SIZE),
            'tiles/gold': load_tile_assets('env/tiles/gold.png', TILE_SIZE),
            'tiles/silver': load_tile_assets('env/tiles/silver.png', TILE_SIZE),
            'wall_tiles/jungle': load_tile_assets('env/wall_tiles/jungle_wall.png', TILE_SIZE),
            'wall_tiles/dirt': load_tile_assets('env/wall_tiles/dirt_wall.png', TILE_SIZE),
            'background/cavern': load_img('env/background/cavern_background.png')
        }

        self.world_gen = WorldGen(400, 400)
        seed = 'Mini Terraria'
        #level = self.world_gen.gen_world(seed)
        self.tile_map = TileMap(self)
        #level = {}
        #with open('data/maps/0.json', 'r') as f:
        #    level = json.load(f)
        #self.tile_map.save(level, 'world_0')
        #self.tile_map.load_info(level)
        #self.tile_map.save_json('data/maps/0.json')
        self.tile_map.load_json('data/maps/0.json')

        self.frame_count = 0

        self.light_map = pygame.Surface(self.screen.get_size())

    def add_shader(self, name, frag_path, vert_path=None, buffer=None, vao_args=['2f 2f', 'vert', 'texcoord']):
        self.vaos[name] = self.mgl.render_object(frag_path, vert_path, vao_args, buffer)
        if name != 'default' and 'default' in self.vaos:
            del self.vaos['default']
            return 1
        return 0

    def shade(self, uniforms, dest=None):
        for vao in self.vaos:
            rdest = None
            if dest:
                if vao in dest:
                    rdest = dest[vao]
            self.vaos[vao].render(rdest, uniforms[vao])

    def close(self):
        print('closing')
        self.running = False
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def update(self):
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.dt = min(self.dt, 4)
        self.last_time = time.time()
        # self.scroll[0] -= 0.5 * self.dt
        keys = pygame.key.get_pressed()
        self.scroll[0] += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.dt * 5
        self.scroll[1] -= (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * self.dt * 5
        self.render_scroll = [math.floor(self.scroll.x), math.floor(self.scroll.y)]

    def draw(self):
        self.screen.fill((0, 149, 233))
        self.light_map = self.tile_map.draw(self.screen, self.render_scroll)

#       pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, 100, 100))
#       pygame.draw.rect(self.screen, (255, 255, 255), (200, 200, 100, 100))
#       mx, my = [m / 2 for m in list(pygame.mouse.get_pos())]
#       for y in range(10):
#           for x in range(10):
#               pygame.draw.rect(self.screen, pygame.Color(255, 0, 255).lerp((255, 200, 0), max(0, min(1, math.sqrt((y - 5) ** 2 + (x - 5) ** 2) / 5))).lerp((0, 0, 0), max(0, min(1, math.sqrt((y - 5) ** 2 + (x - 5) ** 2) / 5))), (x * 8 + mx, y * 8 + my, 8, 8))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()

            self.update()
            self.draw()

            self.shade(uniforms={'shader': {'tex': self.screen, 'light': self.light_map}})

            pygame.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')
            pygame.display.flip()
            self.clock.tick()

            self.frame_count += 1

if __name__ == '__main__':
    App().run()