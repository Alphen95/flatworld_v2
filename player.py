import os
import random

import pygame as pg


class Player():
    def __init__(self,screen,version,options):
        self.version = version 
        self.display_size = options["display_tiles"]
        self.hitboxes = options["hitboxes"]
        self.speed = 2
        self.pos = [0,0]
        self.offset = [0,0]
        self.font = pg.font.Font(os.path.join("res","verdana.ttf"), 16)
        self.energy = 100
        self.inventory = []
        self.connectable_blocks = [["grass",0],["dirt",1],["concrete",3]]
        self.connectable_blocks_condition = []
        for i in self.connectable_blocks: self.connectable_blocks_condition.append(i[0])
        self.world = {}
        self.w, self.h = screen.get_size()    
        self.hexadecimal = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
        max_tile_size = int(self.h/self.display_size)
        print(self.h)
        self.tile_size = 32
        while self.tile_size+32 <= max_tile_size: self.tile_size+=32
        self.w_indent = (self.w-self.tile_size*self.display_size)/2
        self.h_indent = (self.h-self.tile_size*self.display_size)/2
        self.BG_GRAY = (115,115,115)
        self.sprites = {}
        self.old_pressed = []

    def load_sprites(self):
        sprites_filenames = os.listdir("res")
        for sprites_filename in sprites_filenames:
            if not(sprites_filename in [".DS_Store",".vscode","font.ttf","verdana.ttf"]):self.sprites[sprites_filename[:-4]] = pg.image.load(os.path.join("res",sprites_filename)).convert_alpha()


        self.sprites["render_conveyor_vertical"] = self.sprites["conveyor"].subsurface(0,0,32,48)
        self.sprites["render_conveyor_horizontal"] = self.sprites["conveyor"].subsurface(32,0,32,48)
        self.sprites["render_conveyor_turn_side_top"] = self.sprites["conveyor"].subsurface(64,0,32,48)
        self.sprites["render_conveyor_turn_side_bottom"] = self.sprites["conveyor"].subsurface(96,0,32,48)
        self.sprites["render_conveyor_plate"] = self.sprites["conveyor"].subsurface(129,0,26,8)

        self.sprites["conveyor_down"] = []
        for frame in range(0,32):
            render_surface = pg.Surface((32,48),pg.SRCALPHA)
            conveyor_surface = pg.Surface((26,32),pg.SRCALPHA)
            conveyor_surface.blit(self.sprites["render_conveyor_plate"],(0,-8+(frame)%40))
            conveyor_surface.blit(self.sprites["render_conveyor_plate"],(0,-8+(frame+8)%40))
            conveyor_surface.blit(self.sprites["render_conveyor_plate"],(0,-8+(frame+16)%40))
            conveyor_surface.blit(self.sprites["render_conveyor_plate"],(0,-8+(frame+24)%40))
            conveyor_surface.blit(self.sprites["render_conveyor_plate"],(0,-8+(frame+32)%40))
            render_surface.blit(self.sprites["render_conveyor_vertical"],(0,0))
            render_surface.blit(conveyor_surface,(4,0))
            self.sprites["conveyor_down"].append(render_surface)

        self.sprites["hud_energy"] = self.sprites["hud"].subsurface(0,0,32,32)
        self.sprites["hud_inv_slot"] = self.sprites["hud"].subsurface(32,0,32,32)
        self.sprites["stone"] = self.sprites["ground_tiles"].subsurface(32,0,32,32)
        for block in self.connectable_blocks:
            block_name = block[0]
            block_row = block[1]
            self.sprites[block_name] = self.sprites["ground_tiles"].subsurface(0,32*block_row,32,32)
            self.sprites[f"{block_name}_corner"] = self.sprites["ground_tiles"].subsurface(32,32*block_row,32,32)
            self.sprites[f"{block_name}_side_full"] = self.sprites["ground_tiles"].subsurface(32*2,32*block_row,32,32)
            self.sprites[f"{block_name}_corner_full"] = self.sprites["ground_tiles"].subsurface(32*3,32*block_row,32,32)
            self.sprites[f"{block_name}_corner_outer"] = self.sprites["ground_tiles"].subsurface(32*4,32*block_row,32,32)

        self.sprites["coal"] = self.sprites["ground_tiles"].subsurface(0,32*2,32,32)
        self.sprites["chalcopyrite"] = self.sprites["ground_tiles"].subsurface(32,32*2,32,32)
        self.sprites["hematite"] = self.sprites["ground_tiles"].subsurface(32*2,32*2,32,32)
        self.sprites["cassiterite"] = self.sprites["ground_tiles"].subsurface(32*3,32*2,32,32)
        self.sprites["sphalerite"] = self.sprites["ground_tiles"].subsurface(32*4,32*2,32,32)
        self.sprites["galenite"] = self.sprites["ground_tiles"].subsurface(32*5,32*2,32,32)
        self.sprites["sulfur"] = self.sprites["ground_tiles"].subsurface(32*6,32*2,32,32)
        self.sprites["uranium"] = self.sprites["ground_tiles"].subsurface(32*7,32*2,32,32)

        self.sprites["planks"] = self.sprites["blocks"].subsurface(32,0,32,48)
        self.sprites["position_register"] = self.sprites["blocks"].subsurface(64,16,32,32)

    def draw(self,screen,clock,c_tick,tick,world_border):
        screen.fill(self.BG_GRAY)
        pg.draw.rect(screen,(160,160,160),[self.w_indent,self.h_indent,self.tile_size*16,self.tile_size*16])
        for draw_x in range(-1,self.display_size+1):
            for draw_y in range(-1,self.display_size+1):
                pos = [draw_x-((self.offset[0]%32)/32),draw_y-((self.offset[1]%32)/32)]
                exact_pos = [draw_x+self.pos[0],draw_y+self.pos[1]]
                if self.hitboxes: screen.blit(pg.transform.scale(self.sprites["position_register"],(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                if f"{draw_x+self.pos[0]}_{draw_y+self.pos[1]}" in self.world["obj"]:
                    sides, corners = [],[]

                    i = f"{draw_x+self.pos[0]}_{draw_y+self.pos[1]}"
                    sides = [
                            True if exact_pos[1] > 0 and f"{exact_pos[0]}_{exact_pos[1]-1}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]-1}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]-1}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]-1}"]["block"]) else False,
                            True if exact_pos[0] < world_border and f"{exact_pos[0]+1}_{exact_pos[1]}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]}"]["block"]) else False,
                            True if exact_pos[1] < world_border and f"{exact_pos[0]}_{exact_pos[1]+1}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]+1}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]+1}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]+1}"]["block"]) else False,
                            True if exact_pos[0] > 0 and f"{exact_pos[0]-1}_{exact_pos[1]}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]}"]["block"]) else False
                        ]
                    

                    if self.world["obj"][i]["block"] == "conveyor":
                        c_sides = [
                            True if exact_pos[1] > 0 and f"{exact_pos[0]}_{exact_pos[1]-1}" in self.world["obj"] and self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]-1}"] == {"block":"conveyor","rot":0} else False,
                            True if exact_pos[0] < world_border and f"{exact_pos[0]+1}_{exact_pos[1]}" in self.world["obj"] and self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]}"] == {"block":"conveyor","rot":0} else False,
                            True if exact_pos[1] < world_border and f"{exact_pos[0]}_{exact_pos[1]+1}" in self.world["obj"] and self.world["obj"][f"{exact_pos[0]}_{exact_pos[1]+1}"] == {"block":"conveyor","rot":0} else False,
                            True if exact_pos[0] > 0 and f"{exact_pos[0]-1}_{exact_pos[1]}" in self.world["obj"] and self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]}"] == {"block":"conveyor","rot":0} else False
                        ]
                        frame = int(c_tick / (240/32))%32
                        print(frame)
                        if self.world["obj"][i]["rot"] == 0 and (not(c_sides[1] or c_sides[3]) or c_sides[0]):
                            screen.blit(pg.transform.scale(self.sprites["conveyor_down"][frame],(self.tile_size,self.tile_size*1.5)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1]-0.5)))
                    else:
                        if self.sprites[self.world["obj"][i]["block"]].get_height() == 48:
                            screen.blit(pg.transform.scale(self.sprites[self.world["obj"][i]["block"]],(self.tile_size,self.tile_size*1.5)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1]-0.5)))
                        else:
                            screen.blit(pg.transform.scale(self.sprites[self.world["obj"][i]["block"]],(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                    if self.world["obj"][i]["block"] in self.connectable_blocks_condition:
                        corners = [
                            True if exact_pos[0] > 0 and exact_pos[1] > 0 and f"{exact_pos[0]-1}_{exact_pos[1]-1}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]-1}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]-1}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]-1}"]["block"]) else False,
                            True if exact_pos[0] < world_border and exact_pos[1] > 0 and f"{exact_pos[0]+1}_{exact_pos[1]-1}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]-1}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]-1}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]-1}"]["block"]) else False,
                            True if exact_pos[0] < world_border and exact_pos[1] < world_border and f"{exact_pos[0]+1}_{exact_pos[1]+1}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]+1}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]+1}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]+1}_{exact_pos[1]+1}"]["block"]) else False,
                            True if exact_pos[0] > 0 and exact_pos[1] < world_border and f"{exact_pos[0]-1}_{exact_pos[1]+1}" in self.world["obj"] and (self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]+1}"]["block"] in ["grass","dirt"] and self.world["obj"][i]["block"] in ["grass","dirt"] or self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]+1}"]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] in self.connectable_blocks_condition and self.world["obj"][i]["block"] == self.world["obj"][f"{exact_pos[0]-1}_{exact_pos[1]+1}"]["block"]) else False
                        ]
                        if sides[0]:screen.blit(pg.transform.scale(self.sprites[f"{self.world['obj'][i]['block']}_side_full"],(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[1]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_side_full"],270),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[2]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_side_full"],180),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[3]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_side_full"],90),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[0] and sides[3] and corners[0]:screen.blit(pg.transform.scale(self.sprites[f"{self.world['obj'][i]['block']}_corner_full"],(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif not(sides[0] or sides[3] or corners[0]) or not(sides[0] or sides[3]):screen.blit(pg.transform.scale(self.sprites[f"{self.world['obj'][i]['block']}_corner"],(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif sides[0] and sides[3] and not corners[0]:screen.blit(pg.transform.scale(self.sprites[f"{self.world['obj'][i]['block']}_corner_outer"],(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[1] and sides[0] and corners[1]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner_full"],270),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif not(sides[1] or sides[0] or corners[1]) or not(sides[1] or sides[0]):screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner"],270),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif sides[1] and sides[0] and not corners[1]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner_outer"],270),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[2] and sides[1] and corners[2]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner_full"],180),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif not(sides[2] or sides[1] or corners[2]) or not(sides[2] or sides[1]):screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner"],180),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif sides[2] and sides[1] and not corners[2]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner_outer"],180),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        if sides[3] and sides[2] and corners[3]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner_full"],90),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif not(sides[3] or sides[2] or corners[3]) or not(sides[3] or sides[2]):screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner"],90),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
                        elif sides[3] and sides[2] and not corners[3]:screen.blit(pg.transform.scale(pg.transform.rotate(self.sprites[f"{self.world['obj'][i]['block']}_corner_outer"],90),(self.tile_size,self.tile_size)),(self.w_indent+self.tile_size*(pos[0]),self.h_indent+self.tile_size*(pos[1])))
        '''
        player_pos = [self.offset[0],self.offset[1]]
        if self.pos[0] >7 or self.pos[0]==7 and self.offset[0]%32>=16:
            player_pos[0] = 7.5*32
            if self.offset[0]/32 >= world_border-8.5:
                player_pos[0]+=self.offset[0]%((world_border-8.5)*32)
        if self.pos[1] >7 or self.pos[1]==7 and self.offset[1]%32>=16:
            player_pos[1] = 7.5*32
            if self.offset[1]/32 >= world_border-8.5:
                player_pos[1]+=self.offset[1]%((world_border-8.5)*32)
        screen.blit(pg.transform.scale(self.sprites["player"],(self.tile_size,self.tile_size)),((player_pos[0]*self.tile_size/32)+self.w_indent,(player_pos[1]*self.tile_size/32)+self.h_indent))
        '''
        pg.draw.rect(screen,self.BG_GRAY,(0,0,self.w_indent,self.h))
        pg.draw.rect(screen,self.BG_GRAY,(self.w_indent+self.tile_size*self.display_size,0,self.w_indent,self.h))
        pg.draw.rect(screen,self.BG_GRAY,(0,0,self.w,self.h_indent))
        pg.draw.rect(screen,self.BG_GRAY,(0,self.h_indent+self.tile_size*self.display_size,self.w,self.h_indent))
        #for i in range(0,16):
        #    for l in range(0,16):
        #        text = self.font.render(f"{self.hexadecimal[i]}{self.hexadecimal[l]}",True,(255,255,255))
        #        screen.blit(text,(self.w_indent+self.tile_size*i,self.h_indent+self.tile_size*l))
        pg.draw.rect(screen,(50,50,50),(0,self.h/2-36,136,72))
        pg.draw.rect(screen,(0,0,0),(4,self.h/2-32,128,64))
        screen.blit(pg.transform.scale(self.sprites["hud_energy"],(64,64)),(4,self.h/2-32))
        energy_txt = self.font.render(str(self.energy),True,(57,191,0))
        screen.blit(energy_txt,(80,self.h/2-8))
        for i in range(0,len(self.inventory)):
            screen.blit(pg.transform.scale(self.sprites["hud_inv_slot"],(128,128)),(self.w-128,self.h/2-128*((len(self.inventory))/2-i)))
            if self.inventory[i][0] != "":
                screen.blit(pg.transform.scale(self.sprites[f"item_{self.inventory[i][0]}_{self.inventory[i][1]}"],(128,128)),(self.w-128,self.h/2-128*((len(self.inventory))/2-i)))
        version = self.font.render(self.version,True,(0,0,0))
        screen.blit(version,[0,0])
        version = self.font.render(f"x:{self.offset[0]/32} y:{self.offset[1]/32}",True,(0,0,0))
        screen.blit(version,[0,30])
        
        fps_counter = self.font.render("fps: "+str(int(clock.get_fps())), False, ((255 if clock.get_fps() < 60 else 0), (255 if clock.get_fps() > 15 else 0), 0))
        screen.blit(fps_counter, (0, self.h-32))

        pg.display.flip()

    def click_handler(self,click_pos,pressed,world_border):
        blockchanges = [{}]
        if pressed[0] or pressed[2]:
            if click_pos[0] > self.w_indent and click_pos[0] < self.w_indent+self.tile_size*self.display_size and click_pos[1] > self.h_indent and click_pos[1] < self.h_indent+self.tile_size*self.display_size:
                x_click = int((click_pos[0]-self.w_indent+(self.offset[0]%32*self.tile_size/32))/self.tile_size)+self.pos[0]
                y_click = int((click_pos[1]-self.h_indent+(self.offset[1]%32*self.tile_size/32))/self.tile_size)+self.pos[1]
                #print(x_click)
                block_pos = f"{x_click}_{y_click}"
                print(block_pos)
                blockchanges = [{"type":"remove","pos":block_pos}]
        return blockchanges

    def key_handler(self,pressed,world_border):
        if pressed[pg.K_UP] and self.offset[1] > 0:
            self.offset[1] -= self.speed
        if pressed[pg.K_DOWN] and self.offset[1] < (world_border-1-self.display_size)*32:
            self.offset[1] += self.speed
        if pressed[pg.K_LEFT] and self.offset[0] > 0: #and not self.old_pressed[pg.K_LEFT]:
            self.offset[0] -= self.speed
        if pressed[pg.K_RIGHT] and self.offset[0] < (world_border-1-self.display_size)*32: # and not self.old_pressed[pg.K_RIGHT]:
            self.offset[0] += self.speed
        self.pos = [int(self.offset[0]/32),int(self.offset[1]/32)]

    def update(self,screen,clock,c_tick,tick,mouse,keys,world_border,changes):
        for change in changes:
            if change != {}:
                if change["type"] == "remove" and change["pos"] in self.world["obj"]:
                    self.world["obj"].pop(change["pos"])
        self.key_handler(keys,world_border)
        tile_updates = self.click_handler(mouse[0],mouse[1],world_border)
        self.draw(screen,clock,c_tick,tick,world_border)
        self.old_pressed = keys
        return tile_updates
