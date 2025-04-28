import pygame, sys, time, random, math

import numpy as np
import noise

from data.scripts.tile_map import TILE_INFO

COLORS = {'stone': (50, 50, 50), 'dirt': (74, 19, 10), 'clay': (120, 32, 32), 'copper': (252, 101, 0), 'tin': (171, 127, 15), 'iron': (99, 88, 65), 'lead': (65, 78, 99), 'silver': (153, 153, 153), 'tungsten': (6, 64, 41),
'gold': (255, 183, 0), 'platinum': (87, 179, 179), 'grass': (0, 255, 0), 'wall_tiles/dirt': (37, 9, 5)}

TRANSLATE_COLORS = {COLORS[key]: key for key in COLORS}

class WorldGen:
    def __init__(self, width, height):
        self.world = pygame.Surface((width, height))
        if __name__ == '__main__':
            self.display = pygame.display.set_mode((1600, 1600))
            self.screen = pygame.Surface((800, 800))
            self.dt = 1
            self.last_time = time.time() - 1 / 60
            self.clock = pygame.time.Clock()
            self.running = True

            seed = 'asdflk9'
            self.gen_world(seed)

            self.scroll = [0, 0]
            self.pixel = False


    @staticmethod
    def generate_random_shape(size, color=(255, 255, 255)):
        surf = pygame.Surface((size, size))
        surf.fill((0, 0, 0))
        n = random.randint(10, 20)
        offset = random.random() * 10000
        pygame.draw.polygon(surf, (255, 255, 255), [(size * 0.5 + (math.sin(math.pi * 2 * i / n) * noise.pnoise1(i / n * 2 + offset) * size * 0.5), size * 0.5 + (math.cos(math.pi * 2 * i / n) * noise.pnoise1(i / n * 2 + offset) * size * 0.5)) for i in range(n)])
        surf.set_colorkey((0, 0, 0))
        surf = pygame.transform.gaussian_blur(surf, 1)
        mask = pygame.mask.from_surface(surf)
        surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
        return surf

    def gen_world(self, seed):
        random.seed(seed)
        self.world.fill((74, 19, 10))
        pygame.draw.rect(self.world, (50, 50, 50), (0, self.world.get_height() / 3, self.world.get_width(), self.world.get_height() - self.world.get_height() / 3))
        xpix, ypix = self.world.get_width(), self.world.get_height()
        pic = pygame.PixelArray(self.world)
        offset = random.random() * 1000
        for y in range(ypix):
            for x in range(xpix):
                #pygame.display.set_caption(f'{(y * len(pic[0]) + x) / (len(pic) * len(pic[0])) :.1f}')
                c = (74, 19, 10) if noise.pnoise2(x / 500 * 40 + offset, y / 500 * 40 + offset, octaves=5) < max(-0.0, (self.world.get_height() / 3 - y) * 1.5 / self.world.get_height()) else (50, 50, 50)
                pic[x, y] = c
            if y % 100 == 0: print(f'row {y} done')
        pic.close()
        mult = int(self.world.get_width() * self.world.get_height() / 640000)
        for _ in range(random.randint(50, 100) * 2 * mult):
            blob = self.generate_random_shape(random.randint(10, 30), color=(13, 2, 0))
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(200, self.world.get_height())))
        for _ in range(random.randint(50, 100) * mult):
            blob = self.generate_random_shape(random.randint(10, 50), color=COLORS['clay'])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(0, int(self.world.get_height() * 0.2))))
        ore_choices = [random.choice(pair) for pair in TILE_INFO['ore_pairs']]
        for _ in range(random.randint(50, 100) * 4 * mult):
            blob = self.generate_random_shape(random.randint(5, 20), color=COLORS[ore_choices[0]])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(0, int(self.world.get_height() * 0.9))))
        for _ in range(random.randint(50, 100) * 2 * mult):
            blob = self.generate_random_shape(random.randint(5, 20), color=COLORS[ore_choices[1]])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(0, int(self.world.get_height() * 0.9))))
        for _ in range(random.randint(75, 150) * mult):
            blob = self.generate_random_shape(random.choice([i + 2 for i in range(10)]), color=COLORS[ore_choices[2]])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(int(self.world.get_height() * 0.15), int(self.world.get_height() * 0.9))))
        for _ in range(random.randint(20, 40) * mult):
            blob = self.generate_random_shape(random.randint(5, 15), color=COLORS[ore_choices[3]])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(int(self.world.get_height() * 0.3), self.world.get_height())))
        for _ in range(random.randint(50, 60) * mult):
            blob = self.generate_random_shape(random.choice([i + 2 for i in range(10)]), color=COLORS[ore_choices[2]])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(int(self.world.get_height() * 0.5), self.world.get_height())))
        for _ in range(random.randint(50, 60) * mult):
            blob = self.generate_random_shape(random.randint(5, 15), color=COLORS[ore_choices[3]])
            self.world.blit(blob, (random.randint(0, self.world.get_width()), random.randint(int(self.world.get_height() * 0.5), self.world.get_height())))
        print(ore_choices)
        wall_tiles = {}
        noise_tex = pygame.Surface(self.world.get_size())
        xpix, ypix = noise_tex.get_width(), noise_tex.get_height()
        pic = pygame.PixelArray(noise_tex)
        offset = random.random() * 1000
        for y in range(ypix):
            for x in range(xpix):
                #pygame.display.set_caption(f'{(y * len(pic[0]) + x) / (len(pic) * len(pic[0])) :.1f}')
                n = noise.pnoise2(x / 500 * 20 + offset + offset, y / 500 * 20 + offset + offset) * 0.5
                n1 = noise.pnoise1(x / 500 + offset, octaves=20) * 50 + 100
                c = (255, 255, 255) if (not (0.0 < noise.pnoise2(x / 500 * 20 + offset, y / 500 * 20 + offset, octaves=3) < pygame.math.lerp(pygame.math.lerp(n, 0.2, math.sin(y * 0.01 - 100) * 0.5 + 0.5), 0.0, math.cos(x / 200 + offset) * 0.25 + 0.25))) and y > n1 else (0, 0, 0)
                if n1 < y < 200:
                    wall_tile_loc = f'{x};{y}'
                    wall_tiles[wall_tile_loc] = 'wall_tiles/dirt'
                    if c == (0, 0, 0):
                        c = COLORS['wall_tiles/dirt']
                elif y >= 200:
                    if c == (0, 0, 0):
                        c = (13, 2, 0)
                if n1 < y < 120 + noise.pnoise1(x / 50 + offset * 2) * 25:
                    if c == (0, 0, 0) or c == COLORS['wall_tiles/dirt']:
                        c = (255, 255, 255)
                pic[x, y] = c
            if y % 100 == 0: print(f'row {y} done')
        pic.close()
        noise_tex.set_colorkey((255, 255, 255))
        self.world.blit(noise_tex, (0, 0))
        map_data = {'level': {}, 'wall_tiles': wall_tiles}
        pic = pygame.PixelArray(self.world)
        for y in range(ypix):
            for x in range(xpix):
                loc = f'{x};{y}'
                c = tuple(self.world.unmap_rgb(pic[x, y]))
                c = (c[0], c[1], c[2])
                if c in {COLORS['dirt'], COLORS['clay']}:
                    if y < 150 + noise.pnoise1(x / 50) * 20:
                        cs = False
                        for shift in [(-1, 0), (0, -1), (1, 0)]:
                            try:
                                c2 = self.world.unmap_rgb(pic[x + shift[0], y + shift[1]])
                                c2 = (c2[0], c2[1], c2[2])
                                if not (c2 in TRANSLATE_COLORS and not ('wall_tiles' in TRANSLATE_COLORS[c2])):
                                    cs = True
                            except IndexError:
                                pass
                        if cs:
                            c = COLORS['grass']
                            pic[x, y] = c
                if c in TRANSLATE_COLORS and not ('wall_tiles' in TRANSLATE_COLORS[c]):
                    map_data['level'][loc] = {'type': TRANSLATE_COLORS[c], 'variant': 0}
            if y % 100 == 0: print(f'row {y} done')
        pic.close()
        #world_mask = pygame.mask.from_surface(noise_tex)
        ##pic = np.array([[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)])
        #pygame.pixelcopy.array_to_surface(self.world, pic)
        #pxarray = pygame.PixelArray(self.world)
        #for y in range(len(pxarray)):
        #    for x in range(len(pxarray[y])):
        #        value = noise([x / self.world.get_width(), y / self.world.get_height()])
        #        pxarray[y][x] = tuple([max(0, min(255, int(value * 255))) for _ in range(3)])
        return map_data

    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.scroll[0] += keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.scroll[1] -= keys[pygame.K_UP] - keys[pygame.K_DOWN]
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(self.world, self.screen.get_size()) if not self.pixel else self.world, (-self.scroll[0], -self.scroll[1]))
    
    def run(self):
        while self.running:
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()
                    if event.key == pygame.K_o:
                        self.pixel = not self.pixel
            self.update()
            pygame.transform.scale_by(self.screen, 2.0, self.display)
            pygame.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    WorldGen(1600, 800).run()
