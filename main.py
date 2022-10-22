import os
import random

import pygame as pg

from player import Player

pg.init()
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

tick = 0
clock = pg.time.Clock()
timers = {}
version = "v(-0.1.1) movement test"
world = {}
players = []
world_generation_options = {
    "world_size": 20*16*2,
    "bushes_min": 100,
    "bushes_max": 400,
    "puddles_min": 10,
    "puddles_max": 30,
    "ores_min": 100,
    "ores_max": 500,
    "ores":[
        ["coal", 25],
        ["chalcopyrite", 20], #copper pyrite, халькопирит (медный колчедан) CuFeS2
        ["hematite", 20], #гематит Fe2O3
        ["cassiterite", 15], #касситерит SnO2
        ["sphalerite", 15], #сфалерит ZnS 
        ["galenite", 10], #галенит PbS
        ["sulfur", 10], #самородная сера S
        ["uranium", 5] #природный уран 
    ],
}

players.append(Player(screen,version))

def generate_world():
    world = {"obj":{}}
    for i in range(random.randint(world_generation_options["bushes_min"],world_generation_options["bushes_max"])):
        size = random.choice([1,3,5])
        points = [random.randint(0,world_generation_options["world_size"]-size),random.randint(0,world_generation_options["world_size"]-size)]
        for pos1 in range(points[0],points[0]+size):
            for pos2 in range(points[1],points[1]+size):
                pos = f"{pos1}_{pos2}"
                world["obj"][pos] = {"block":"grass"}
    
    ores_dict = []
    for ore in world_generation_options["ores"]:
        for i in range(0,ore[1]+1):
            ores_dict.append(ore[0])
    for i in range(random.randint(0,2)):
        point = [random.randint(0,world_generation_options["world_size"]-1),random.randint(0,world_generation_options["world_size"]-1)]
        world["obj"][pos] = {"block":random.choice(ores_dict)}

    return world

players[0].world = generate_world()
players[0].load_sprites()

working = True
while working:

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            if evt.key == pg.K_r:
                players[0].display_array = generate_world()

    '''
    if [0] or pg.mouse.get_pressed()[2]:
        if click_pos[0] > w_indent and click_pos[0] < w_indent+tile_size*16 and click_pos[1] > h_indent and click_pos[1] < h_indent+tile_size*16:
            block_pos = f"{int((click_pos[1]-h_indent)/tile_size)}_{int((click_pos[0]-w_indent)/tile_size)}"
            if pg.mouse.get_pressed()[0] and block_pos in display_array["obj"]:
                display_array["obj"].pop(block_pos)
            elif pg.mouse.get_pressed()[2]:
                display_array["obj"][block_pos] = {"block":"concrete"}
    '''
    for player in players:
        player.update(screen,clock,tick,(pg.mouse.get_pos(),pg.mouse.get_pressed()),pg.key.get_pressed())
    clock.tick()
    tick += 60/clock.get_fps() if clock.get_fps() != 0 else 1
    for timer in timers:
        if timers[timer] >0: timers[timer]-=(60/clock.get_fps() if clock.get_fps() != 0 else 1)
    if tick >= 60: 
        tick -= 60
    if not working:
        pg.quit()

