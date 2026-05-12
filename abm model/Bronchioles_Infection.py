import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math


import mesa
from mesa.datacollection import DataCollector
from mesa import Model,Agent
from mesa.space import MultiGrid
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import Slider, SolaraViz, make_plot_component, make_space_component

#this cell is used for the creation of the model, which creates the grid
class LungModel(mesa.Model): 
    def __init__(self, a_radius=1.4, width=20, height=20, anti_doses=7,mucus_thinner=1,init_health_Bronchial=100, macrophage_gain=50, seed=100, simulator=None, start_pathogen = 20, start_macrophage = 5, start_mucin = 200, start_anti = 5, call_anti = 10,  call_mucus_thinner = 12):
        super().__init__(seed=seed)
        self.simulator = simulator
        self.simulator.setup(self)
        self.grid = MultiGrid(width, height, torus=True)
        self.step_count=0 
        self.death_step_list=[]
        self.death_pos_list=[]
        self.step_bac_tog=0
        self.ten_step=0 
        self.five_step=0 
        self.two_step=0 
        self.call_anti = call_anti
        self.call_mucus_thinner = call_mucus_thinner
        self.mucus_thinner=mucus_thinner
        self.start_pathogen=start_pathogen
        self.start_macrophage=start_macrophage
        self.start_mucin=start_mucin
        self.start_anti = start_anti
        self.a_radius=a_radius
        self.antibiotic_count=0
        self.anti_doses=anti_doses
        # self.start_paathogen = 20, start_macrophage = 5, start_mucin = 50, call_anti = 4
        reporters = {
            "Mucin": lambda m: len(m.agents_by_type.get(Mucin,[])),
            "Bronchial": lambda m: len(m.agents_by_type.get(Bronchial,[])),
            "Pathogen": lambda m: len(m.agents_by_type.get(Pathogen,[])),
            "Antibiotic": lambda m: len(m.agents_by_type.get(Antibiotic,[])),
            "Macrophage": lambda m: len(m.agents_by_type.get(Macrophage,[]))

        }
        agent_reporters = {
            "Bronch_health": lambda b: b.health if isinstance(b, Bronchial) else None,
            "Biofilm_formed": lambda b: int(b.biofilm_form) if isinstance(b, Pathogen) else None
            }
        self.datacollector = DataCollector(reporters, agent_reporters)


        #Set the fixed position of the bronchial layer
        for x in range(width):
            epithelial=Bronchial(
                self,
                (x,2),health=100,
                init_health = init_health_Bronchial,
                ) #Makes 20 of the bronchial, the ali form makes batches of randomly placed
            self.grid.place_agent(epithelial, (x,2))

        #Initial mucin of 1 for 3 layers, then the rest is randomized
        self.total_mucin = 0
        for x in range(width):
             for y in range (3,6):
                mucus_layer= Mucin(self,(x,y),start_mucus_thinner=8, mucus_thinner= 1, out_bound = False,)
                self.grid.place_agent(mucus_layer,(x,y))
                self.total_mucin +=1 

        while self.total_mucin <= self.start_mucin:
            for y in range(3,5):
                x = self.random.randrange(self.grid.width)
                mucus_layer= Mucin(self,(x,y), start_mucus_thinner=4,mucus_thinner=1, out_bound = False,)
                self.total_mucin+=1 #random placement within first line
                self.grid.place_agent(mucus_layer,(x,y))

        #Spawn pathogens within bounds of mucus
        total_bact = 0
        while total_bact != self.start_pathogen :
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(4,6)
            if any(isinstance(agent, Mucin) for agent in self.grid[x][y]): # might need to change this to be a range of the grid w mucin in it
                total_bact+=1
                bacteria = Pathogen(
                    self,
                    pos = (x,y),
                    health = 100, energy=self.random.random()*20,#a fifth the initial for macro
                    strength = 5, #start from layer above
                    bacteria_gain= 10,
                    p_rep = 0.04,
                    p_unstick = 0.04,
                    alive = True,
                    biofilm_form = False
                )
                self.grid.place_agent(bacteria, (x,y))
        #Ask ali if its okay to the proportions of energy that where used in Lab 6  for the energies of macrophages and bacteria 
        #Spawn macrophages within bounds of mucus
        total_macro = 0
        while total_macro != self.start_macrophage : 
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
    
            if any(isinstance(agent, Mucin) for agent in self.grid[x][y]):
                total_macro+=1
                macrophages = Macrophage(
                    self,
                    pos = (x,y),
                    energy = self.random.random()*(2*macrophage_gain),
                    macrophage_gain = 50,
                    p_rep = 0.04,
                    )
                self.grid.place_agent(macrophages, (x,y))

        #Spawn antibiotics within blood vessel -> lowkey i think we do not wanna initialize any antibiotic or it will quickly kill the pathogens
        #yeah make it happen like on day 2 or 3 and only increase by a given amount every day to better model it 
    def antibiotic_dosage(self):
            total_anti = 0
            while total_anti != self.start_anti:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(2)
                antibiotic=Antibiotic(
                self,
                pos=(x,y),
                health = 15,
                strength= 10,
                alive = True
                )
                self.grid.place_agent(antibiotic, (x,y))
                total_anti +=1

    def gen_cilia(self,pos):
        #while self.mucin_gen != 12:
                 #i wonder if there is a way to alter this depending on how much mucin hieght in the y direction 
            new_mu = Mucin(self,pos)
            self.grid.place_agent(new_mu, pos)
            #self.mucin_gen+=1
    

    #Calling macrophages in infected state
    def call_macro(self,pos): 
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(2)
        pos = (x,y)
        new_macro = Macrophage(self,pos,
                    energy = self.random.random()*2*50,
                    macrophage_gain = 20,
                    p_rep = 0.04,)
        self.grid.place_agent(new_macro, pos)

    #Calling mucin in infected state    
    def call_mucin(self,pos): #secretes mucin in infected state
        new_mu = Mucin(self,pos=pos)
        self.grid.place_agent(new_mu,pos=pos)

    #create an initial infection function that can keep track of how many ticks have past since a bronchiol was injured or died 
    #add to data collector checking the health of the bronchioles.
    def death_tracker(self):
        if self.health_count < 1:
            if len(list(self.agents_by_type[Bronchial]))<self.grid.width:#the health count is to insure that the same step isnt double counted for cell death in it, this is needed because removed cells delete their data 
                self.health_count+=1
            elif len(list(self.agents_by_type[Bronchial]))==20: #reset if everything has been replaced
                self.death_pos_list=[]
                self.death_step_list=[]

                
        #later tune this so there is a separate counter for each bronchiol
            
    #count function for number of bacteria in a space(biofilm)
    def biofilm_formed(self):
        bac_count = 0
        bac_surround = self.grid.get_neighborhood(self.pos, True, True)
        for i in bac_surround:
            if isinstance(i, Pathogen):
                bac_count += 1
                

# think abt bc for stopping mucus at bronchior

#set the initial position of antibiotics

    #Each step of the model
    def step(self):
        self.health_count=0
        self.agents_by_type[Mucin].shuffle_do("step")
        self.agents_by_type[Macrophage].shuffle_do("step")
        if self.step_count==self.call_anti: #we can make this tunable maybe?
            self.antibiotic_dosage()
        if self.step_count>self.call_anti:
            self.antibiotic_count+=1
            if self.antibiotic_count%self.anti_doses==0:
                self.antibiotic_dosage()
        if len(self.agents_by_type.get(Antibiotic,[]))>0:
            self.agents_by_type[Antibiotic].shuffle_do("step")
        self.agents_by_type[Pathogen].shuffle_do("step")
        self.agents_by_type[Bronchial].shuffle_do("step")
        self.datacollector.collect(self)
        self.step_count+=1
        if self.ten_step>=0 and self.ten_step<=10:
            self.ten_step+=1
        if self.five_step>=0 and self.ten_step<=5:
            self.five_step+=1
        if self.two_step>=0 and self.ten_step<=2:
            self.two_step+=1


AGENT_COLORS = {
    "Bronchial": "#FD7D7B",
    "Mucin": "green",
    "Pathogen": "blue",
    "Antibiotic": "black",
    "Macrophage": "purple"
}



