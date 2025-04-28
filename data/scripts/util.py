import pygame
import os
import math

BASE_IMG_PATH = 'data/images/'

def load_img(path, colorkey=(0, 0, 0)):
    img = pygame.image.load(BASE_IMG_PATH + path if not (BASE_IMG_PATH in path) else path).convert()
    if colorkey: img.set_colorkey(colorkey)
    return img

def load_imgs(path, colorkey=(0, 0, 0)):
    imgs = []
    for img_path in os.listdir(BASE_IMG_PATH + path if not (BASE_IMG_PATH in path) else path):
        if '.png' in img_path:
            imgs.append(load_img(str(BASE_IMG_PATH + path if not (BASE_IMG_PATH in path) else path) + f'/{img_path}', colorkey=colorkey))
    return imgs

def snip(img, pos, dimensions):
    img.set_clip(pygame.Rect(pos, dimensions))
    return img.subsurface(img.get_clip())

def load_tile_assets(path, tile_size, colorkey=(0, 0, 0)):
    sprite_sheet = load_img(path, colorkey=colorkey)
    tiles = []
    for y in range(math.ceil(sprite_sheet.get_height() / tile_size)):
        for x in range(math.ceil(sprite_sheet.get_width() / tile_size)):
            tiles.append(snip(sprite_sheet, (x * tile_size, y * tile_size), (tile_size, tile_size)))
    return tiles