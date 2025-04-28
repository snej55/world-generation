import pygame, sys, time, math, random

WIDTH = 250
HEIGHT = 250

GRID_WIDTH = 25
GRID_HEIGHT = 25

TILE_SIZE = [math.floor(WIDTH / GRID_WIDTH), math.floor(HEIGHT / GRID_HEIGHT)]

class App:
    def __init__(self):
        self.display = pygame.display.set_mode((WIDTH * 2, HEIGHT * 2))
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True
        self.grid = [[0 for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
        self.water = [[0 for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
    
    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def update(self):
        self.screen.fill((200, 200, 200))
        mx, my = pygame.mouse.get_pos()
        mx = math.floor(mx / 2 / TILE_SIZE[0])
        my = math.floor(my / 2 / TILE_SIZE[1])
        try:
            if not pygame.key.get_pressed()[pygame.K_SPACE]:
                if pygame.mouse.get_pressed()[0]:
                    self.grid[my][mx] = 1
                elif pygame.mouse.get_pressed()[2]:
                    self.grid[my][mx] = 0
            else:
                self.water[my][mx] = [1, 0] 
        except IndexError:
            pass
        
        done = []
        for y, row in enumerate(self.water):
            for x, tile in enumerate(row):
                if tile and not ((x, y) in done):
                    water = tile
                    try:
                        if not self.grid[y + 1][x] and not self.water[y + 1][x]:
                            self.water[y + 1][x] = [1, 0]
                            self.water[y][x] = 0
                            done.append((x, y + 1))
                        else:
                            if not water[1]:
                                water[1] = random.choice([1, -1])
                            if not self.grid[y][x + water[1]] and not self.water[y][x + water[1]]:# or not self.grid[y][x - 1]:
                                self.water[y][x + water[1]] = [1, water[1]]
                                self.water[y][x] = 0
                                done.append((x + water[1], y))
                            elif not self.grid[y][x - water[1]] and not self.water[y][x - water[1]]:# or not self.grid[y][x - 1]:
                                self.water[y][x - water[1]] = [1, -water[1]]
                                self.water[y][x] = 0
                                done.append((x - water[1], y))
                    except IndexError:
                        water[1] *= -1  
        done_pos = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.water[y][x]
                if tile:
                    try:
                        if self.grid[y + 1][x] or self.water[y + 1][x]:
                            done_pos.append((x, y))
                            aloc = (x, y)
                            
                        else:
                            pygame.draw.rect(self.screen, (0, 0, 255), (x * TILE_SIZE[0], y * TILE_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
                    except IndexError:
                        pygame.draw.rect(self.screen, (0, 0, 255), (x * TILE_SIZE[0], y * TILE_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile:
                    pygame.draw.rect(self.screen, (0, 0, 0), (x * TILE_SIZE[0], y * TILE_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
    
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
            self.update()
            pygame.transform.scale_by(self.screen, 2.0, self.display)
            pygame.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')
            pygame.display.flip()
            self.clock.tick()

if __name__ == '__main__':
    App().run()
