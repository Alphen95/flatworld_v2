import os
import random

import pygame as pg

from player import Player

pg.init()
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

tick = 0
c_tick = 0
clock = pg.time.Clock()
timers = {}
version = "v(-0.1.5) 'display scaling and amost completely player removing' update"
world = {}
players = []
camera_options = {
    "display_tiles":16,
    "hitboxes":False
}
world_generation_options = {
    "world_size": 10*16*2,
    "bushes_min": 0,
    "bushes_max": 0,
    "puddles_min": 10,
    "puddles_max": 30,
    "ores_min": 1000,
    "ores_max": 3000,
    "ores":[
        ["coal", 25],
        ["chalcopyrite", 20], #copper pyrite, халькопирит (медный колчедан) CuFeS2
        ["hematite", 20], #гематит Fe2O3
        ["cassiterite", 15], #касситерит SnO2
        ["sphalerite", 15], #сфалерит ZnS 
        ["galenite", 10], #галенит PbS
        ["sulfur", 10], #самородная сера S
        ["uranium", 5] #природный уран 235U
    ],
}

players.append(Player(screen,version,camera_options))
players[0].speed = 2
players[0].offset = [0,0]

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
        for i in range(0,ore[1]):
            ores_dict.append(ore[0])
    for i in range(random.randint(world_generation_options["ores_min"],world_generation_options["ores_max"])):
        points = [random.randint(0,world_generation_options["world_size"]-1),random.randint(0,world_generation_options["world_size"]-1)]
        pos = f"{points[0]}_{points[1]}"
        world["obj"][pos] = {"block":random.choice(ores_dict)}

    return world
world = generate_world()
world["obj"]["0_0"] = {"block":"planks"}
world["obj"]["16_9"] = {"block":"planks"}
world["obj"]["0_1"] = {"block":"conveyor","rot":0}
players[0].world = world
players[0].load_sprites()


working = True
global_changes = []
player_global_changes = []
while working:

    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            working = False
        elif evt.type == pg.KEYDOWN:
            if evt.key == pg.K_r:
                players[0].display_array = generate_world()

    for player in players:
        block_changes = player.update(screen,clock,c_tick,tick,(pg.mouse.get_pos(),pg.mouse.get_pressed()),pg.key.get_pressed(),world_generation_options["world_size"],player_global_changes)
        global_changes.append(block_changes[0])
    player_global_changes = []
    player_global_changes = global_changes.copy()
    #print(player_global_changes)
    for change in player_global_changes:
        if change != {}:
            if change["type"] == "remove" and change["pos"] in world["obj"]:
                world["obj"].pop(change["pos"])
    global_changes = []

    clock.tick()
    tick += 60/clock.get_fps() if clock.get_fps() != 0 else 1
    c_tick += 60/clock.get_fps() if clock.get_fps() != 0 else 1
    for timer in timers:
        if timers[timer] >0: timers[timer]-=(60/clock.get_fps() if clock.get_fps() != 0 else 1)
    if tick >= 60: 
        tick -= 60
    if c_tick >= 239:
        c_tick -= 0
    if not working:
        pg.quit()

