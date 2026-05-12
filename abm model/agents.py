
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




class Antibiotic(mesa.Agent):
    def __init__(self, model,pos, a_radius=1.4 ,health = 15, strength = 10,alive = True): #radius inputted should be in meter
        super().__init__(model)
        self.pos = pos
        self.health = health
        self.strength = strength
        self.alive = alive
        self.a_radius=a_radius # adjusted radus that will be multiplied by *10**(-10)

    #Antibiotic production(idt this is theright word lol)
    def call_anti(self):  #idk if we wanna adjustable concentration we probabaly need to make this an attritube and set it to call a certain amt (like call_macro)
        tot_anti = 0
        for x in range(self.model.grid.width):
            for y in range(2):
                pos = x,y
                blood_anti = self.model.grid.get_cell_list_contents(pos)
                for b in blood_anti:   
                    if isinstance(b, Antibiotic):
                        tot_anti += 1 
        while tot_anti < 5:
            x = self.random.randrange(self.model.grid.width)
            y = self.random.choice([0,1])
            pos = x,y
            new_anti= Antibiotic(self.model, pos,self.health, self.strength)
            self.model.grid.place_agent(new_anti, pos)
            tot_anti +=1


    #Movement of antibiotics limited by mucin intensity
    def move_anti(self): #as far as im concerned this shoudl be working good
        #limiting the movement of the antibiotics based on mucin content, epithelial layer and biofilm formation
        self.radius = self.a_radius *10**(-10)
        slot_space = self.model.grid.get_cell_list_contents([self.pos])
        muc_no = 0
        bac =[]
        biofilm = False
        muc_no = sum(1 for obj in slot_space if isinstance(obj, Mucin) == True)
        for obj in slot_space:
            if isinstance(obj, Pathogen):
                bac.append(obj)
        for b in bac:
            if b.biofilm_form == True:
                biofilm = True

        #Initial diffusion and biofilm movement
        if self.pos[1] < 3: #Initial diffusion from bloodstream
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1]+1 )) 
        elif (biofilm ==True) and (self.random.random() > 0.15) : # stops movement of the antibiotic to stick on biofilm
                return
            
      
        mag_move = 0
        anti_start_move = False

        move_mag = 1
        x,y = self.pos
        self.list_expo=np.geomspace(.1,100,5)
        #Limited movemment of antibiotics by mucus
        if muc_no >=5:
            nu=self.list_expo[4]
            Diffusion_CO=310*1.38*(10**(-23))/(6*np.pi*nu*self.radius)
            Rmsd=2*np.sqrt(Diffusion_CO*3600)*10**6 #to go give me micrometers, assumption that a cell above the brochioles is approx 16 micrometers as normal mucus thickness is 50um
            move=round(Rmsd) 
            self.cells_to_move=round(move/160)
            self.model.ten_step=0 
            if self.model.ten_step>=10:#set up movement
                 #take 10steps to move one steps_to_run
                 anti_start_move = True
            if self.random.random() <0.10: #if it is surrounded by mucin, there is a chance it gets stuck
                self.model.ten_step-=1  
        elif muc_no ==4:
            nu=self.list_expo[3]
            Diffusion_CO=310*1.38*(10**(-23))/(6*np.pi*nu*self.radius)
            Rmsd=2*np.sqrt(Diffusion_CO*3600)*10**6 #to go give me micrometers, assumption that a cell above the brochioles is approx 16 micrometers as normal mucus thickness is 50um
            move=round(Rmsd)
            self.cells_to_move=round(move/160)
            self.model.five_step=0 
            if self.model.five_step>=5:#set up movement
                  #take 5 steps to move, divide by 10 to reduce for grid size
                  anti_start_move = True
            if self.random.random() <0.05:
                self.model.five_step-=1#if it is surrounded by mucin, there is a chance it gets stuck
                return      
        elif muc_no ==3:
            nu=self.list_expo[2]
            Diffusion_CO=310*1.38*(10**(-23))/(6*np.pi*nu*self.radius)
            Rmsd=2*np.sqrt(Diffusion_CO*3600)*10**6 #to go give me micrometers, assumption that a cell above the brochioles is approx 16 micrometers as normal mucus thickness is 50um
            move=round(Rmsd)
            self.cells_to_move=round(move/160) #take 2 steps to move, divide by 10 to reduce for grid siz
            self.model.two_step=0
            if self.model.two_step>=2:#set up movement
                anti_start_move = True
        elif muc_no ==2:
            nu=self.list_expo[1]
            Diffusion_CO=310*1.38*(10**(-23))/(6*np.pi*nu*self.radius)
            Rmsd=2*np.sqrt(Diffusion_CO*3600)*10**6 #to go give me micrometers, assumption that a cell above the brochioles is approx 16 micrometers as normal mucus thickness is 50um
            move=round(Rmsd)
            self.cells_to_move=round(move/160) #moves one cell
        elif muc_no <=1:
            mag_move = 3
            nu=self.list_expo[0]
            Diffusion_CO=310*1.38*(10**(-23))/(6*np.pi*nu*self.radius)
            Rmsd=2*np.sqrt(Diffusion_CO*3600)*10**6 #to go give me micrometers, assumption that a cell above the brochioles is approx 16 micrometers as normal mucus thickness is 50um
            move=round(Rmsd)
            self.cells_to_move=round(move/160) #moves 3 cells
        

        if anti_start_move == True:
            for i in mag_move:
                anti_move_c = self.model.grid.get_neighbors(self.pos, True, radius = 1)
                muc_limit = [] #list to set the limit antibiotic movement to mucin
                muc_limit_layer = 0
                anti_found = False 
                anti_spread = [] #Better spread (diffusion) of antibiotics by having them "evade" each other
                
                for agent in anti_move_c:
                    if isinstance(agent, Mucin):
                        muc_limit.append(agent.pos[1])
                    if isinstance(agent, Antibiotic) == False:
                        anti_found = True
                        anti_spread.append(agent.pos)
                if len(muc_limit) > 0:
                    muc_limit_layer = max(muc_limit)


            
                if self.pos[1] ==3 : #Ensure it does not go back down
                    possible_directions = [(x,y), (x+move_mag,y), (x-move_mag, y), (x+move_mag, y+move_mag), (x-move_mag, y+move_mag), (x,y+move_mag)]
                    anti_pos = self.random.choice(possible_directions)
                    self.model.grid.move_agent(self, anti_pos)
                elif self.pos[1] >=muc_limit_layer: #Limitied by max layer mucin
                    possible_directions = [(x,y), (x+move_mag,y), (x-move_mag, y), (x+move_mag, y-move_mag), (x-move_mag, y-move_mag), (x,y-move_mag)]
                    anti_pos = self.random.choice(possible_directions)
                    self.model.grid.move_agent(self, anti_pos)
                elif anti_found == True: # Ensure antibiotics are not overlapping with one another (diffusing properly)
                    anti_move = self.random.choice(anti_spread) 
                    move_x = anti_move[0] - x
                    move_y = anti_move[1] - y
                    anti_pos = (x + (move_x * move_mag), y + (move_y * move_mag))
                    self.model.grid.move_agent(self, anti_pos)
                else: #other options = movement not limited
                    anti_move = self.random.choice(anti_move_c)
                    move_x = anti_move[0] - x
                    move_y = anti_move[1] - y
                    anti_pos = (x + (move_x * move_mag), y + (move_y * move_mag))
                    self.model.grid.move_agent(self, anti_pos)
                    #im not sure if i want this to be sepearet or an elif command written in but for now im combingin it 
                    #ensures that the antibiotics are 

    
    def kill_bacteria(self): 
        slot_space = self.model.grid.get_cell_list_contents([self.pos])
        bac = [obj for obj in slot_space if isinstance(obj, Pathogen)]
        biofilm_bac = []
        non_biofilm_bac =[]
        for b in bac:
            if b.biofilm_form ==True:
                biofilm_bac.append(b)
            elif b.biofilm_form ==False:
                non_biofilm_bac.append(b)    
        if len(non_biofilm_bac) > len(biofilm_bac):
            bac_atk=self.random.choice(non_biofilm_bac)#If bacteria has not formed biofilm, it will kill one pathogen in and get destroyed
            bac_atk.alive = False
            self.alive = False
        

        elif len(biofilm_bac) > 1: #formation of stronger biofilm will decrease further
            bac_atk = self.random.choice(bac)
            bac_atk.health -= 25
            self.health -=5
            


            #the antibiotic slowly dealing damage to the bacteria not immediate and the bacteria can keep functioning while being attack (find paper) and then eventually randomize and sometimes they ust weaken alot
#set up that bioflim attracts mucin so that antibiotic diffuses slower, and once in the bioflim itll diffuse slowest.

#when its a normal free bacteria itll destroy it and destroy itself, if it a biofilm it made just remain in the bioflim not making any until an amount of ticks and then itll deal the damage to whatever bacteria it is on top off

    def step(self):
        if getattr(self, "alive", True) is False:
            return
        if self.model.step_count%14==1:
             self.call_anti()
             
        self.move_anti()
        self.kill_bacteria()
        if self.health <= 0 or self.alive == False:
            self.remove()


#this cell is used for the base class of the macrophage
class Macrophage(mesa.Agent):
    def __init__(self, model, pos, energy = 8, strength = 5, macrophage_gain= 2, p_rep = 0.04):
        super().__init__(model)
        self.pos = pos
        self.energy = energy
        self.strength = strength
        self.macrophage_gain = macrophage_gain
        self.p_rep = p_rep
    
    #Movement of macrophage within mucin
    def move_macrophage(self):
        findneighbors = self.model.grid.get_neighbors(self.pos,True,False)
        pathogen_found_list=[]
        distances=[]
        maxmucin = 3 #default maxmucin value
        for agent in findneighbors:
            if isinstance(agent,Mucin):
                distances.append(agent.pos[1])
                maxmucin=max(distances)
            else:
                maxmucin=self.pos[1]
        #
        if self.pos[1]>2 and self.pos[1]<=maxmucin: #I dont want them to leave the mucin but they in theory shouldnt as long at there is bacteria near by we could limit them to the tallest mucin with get all cells find the farthest distance with get distance and based on that put an if condition, but we can see
            for obj in findneighbors:
                if isinstance(obj, Pathogen):
                    pathogen_found=obj.pos
                    pathogen_found_list.append(pathogen_found)
        #do we want random movement? if yes, i think this needs to go in a diff if, else line
            if len(pathogen_found_list)>0:
                self.model.grid.move_agent_to_one_of(self,pathogen_found_list)
            else:
                return
        elif self.pos[1]<=2:
                self.model.grid.move_agent(self,(self.pos[0],self.pos[1]+1)) 
                #for now its in step 0 but since they will only be called during infection that shouldnt be a problem
        else:
            return

    #Attack mechanism of macrophage  
    def macro_feed(self):#due to immunocompirmised state, macrphages cannot killl, only samage
        slot_space = self.model.grid.get_cell_list_contents([self.pos])
        bac = [obj for obj in slot_space if isinstance(obj, Pathogen)]
        if len(bac) >0:
            bac_attk = self.random.choice(bac)
            if bac_attk.biofilm_formation==False:
                bac_attk.health-=100
                self.energy+=self.macrophage_gain
            elif self.model.random.random()<.20: #this is only for when we actually get the bioflim to work
                bac_attk.health -=100
                self.energy += self.macrophage_gain
        
        #     self.energy +=5 we need to make bioflim step based because they could just be randomly attach to each other and not in bioflim, maybe randomly they stay nieghbors for a certain amount of steps then they form they bioflim through sensing, idk, or if we are only making the bioflims attached to brochioles only make this be the case if the nieghbors of the bcteria in question are brnchiolo

    def spawn_rep(self): #mechanism for macrophages to increase through replication
        #using half of its health, it can spawn offspring
        self.energy /= 2
        new_macro= Macrophage(self.model, self.pos,self.energy, self.strength, self.macrophage_gain_gain, self.p_rep)
        self.model.grid.place_agent(new_macro, self.pos)
    
    def move_cilia(self):
        self.model.grid.move_agent(self, (self.pos[0]-1,self.pos[1]))
 
#in the future only eat a precentage of the time, model them being immune comprimesd by macropheges not always working and less max amount then in the Lab 6 for not going into immmune overload.
#rn its based on percentage of time and based on biofilm health

    #what happens each step
    def step(self):
        # if  (self.pos[0] ==0): 
        #     self.remove() #assumption theyre only moving out but not in for now 
        # else:
        #     self.move_cilia() 
        self.move_cilia()
        self.move_macrophage()
        self.energy-=5
        if self.energy <= 0:
            self.model.grid.remove_agent(self)
            self.remove()
            return
        if self.model.random.random() < 0.4: 
            self.macro_feed()
            return


#This cell is used for the base class of the mucin, which are particles of mucus
class Mucin(mesa.Agent):
    def __init__(self, model, pos,start_mucus_thinner=5, mucus_thinner= 0, out_bound = False):
        super().__init__(model)
        self.pos = pos
        self.mucus_thinner = mucus_thinner
        self.out_bound = out_bound
        self.replenish_rate=0
        self.start_mucus_thinner=start_mucus_thinner
        #viscosity as parameter to multiple stuff by? or we set it as a probablity and timestep of killing rando, mucus
    #mucus acts as a medium for the antibiotics, pathogens, and macrophages to travel

    #Movement of mucus through cilia
    def move_cilia(self):
        #viscosity affected by the number of mucins in the space
        muc_space = self.model.grid.get_cell_list_contents([self.pos])
        muc_no = 0
        muc_no = sum(1 for obj in muc_space if isinstance(obj, Mucin) == True)
        if muc_no >= 5:
            viscosity = 0.2
        elif muc_no == 4 :
            viscosity = 0.4
        elif muc_no == 3 :
            viscosity = 0.6
        elif muc_no == 2 :
            viscosity = 0.8
        elif muc_no == 1 :
            viscosity = 1
        else: 
            viscosity = 1 
    
        #bronchial health affects cilia movement
        bronch_list = list(self.model.agents_by_type.get(Bronchial,[]))
        total_health = 0 #total current health
        total_init_health = 0 #total initial health
        cilia_move = 1 #how health affects the movement
        for b in bronch_list:
            total_health += b.health
            total_init_health +=b.init_health
        if total_health < (0.75) * total_init_health:
            cilia_move = 0.5
        elif total_health < 0.5 * total_init_health: #if its less than half it'll stop moving
            return 

        #effect of mucus thinners and cilia strength on movement
        if self.pos[1] >= 9:
            return
        elif self.pos[1] > 7:
            height_move = 0.5
        else:
            height_move = 1
        
        #movement of cilia affected by Bronchial health, mucus thinners, and viscosity
        movement_strength = 5 #egular value of movement
        movement_strength = round(movement_strength * cilia_move * height_move * viscosity)

        #movement, removal and regeneration of mucin based on cilia pushing
        for i in range(movement_strength):
            if self.pos[0] == 0:
                self.out_bound = True
                # if self.random.random() <0.9: # relenishment of mucin
                y=self.model.random.randrange(3,5)
                x = self.model.grid.width - (movement_strength-i)
                #x=self.model.random.randrange(self.model.grid.width-movement_strength,self.model.grid.width)
                pos=(x,y)
                self.model.gen_cilia(pos) 
            self.model.grid.move_agent(self, (self.pos[0]-1,self.pos[1]))

            
    #Clearance of mucus through prodcuctive cough
    def move_cough(self):
        muc_space = self.model.grid.get_cell_list_contents([self.pos])
        muc_no = 0
        muc_no = sum(1 for obj in muc_space if isinstance(obj, Mucin) == True)
        if muc_no >= 5:
            viscosity = 0.2
        elif muc_no == 4 :
            viscosity = 0.4
        elif muc_no == 3 :
            viscosity = 0.6
        elif muc_no == 2 :
            viscosity = 0.8
        elif muc_no == 1 :
            viscosity = 1
        else: 
            viscosity = 1 
    
        #effect of mucus thinners and cilia strength on movement

        #movement of cilia affected by Bronchial health, mucus thinners, and viscosity
        movement_strength = 10 #regular value of movement
        movement_strength = round(movement_strength * viscosity)

        #movement, removal and regeneration of mucin based on cilia pushing
        for i in range(movement_strength):
            if self.pos[0] == 0:
                self.out_bound = True
                # if self.random.random() <0.9: # relenishment of mucin
                y=self.model.random.randrange(3,5)
                x = self.model.grid.width - 2*(movement_strength-i)
                pos=(x,y)
                self.model.gen_cilia(pos) 
            self.model.grid.move_agent(self, (self.pos[0]-1,self.pos[1]))


    #Spread of mucin limited by the number of mucins in each grid spot 
    def mucin_spread(self): 
        #set spread intensity based on mucus thinners
        spread_intensity=0
        if self.start_mucus_thinner >= self.model.step_count:
            if self.mucus_thinner ==20 :
                spread_intensity = 5
            elif self.mucus_thinner ==1 :
                spread_intensity = 1
            elif self.mucus_thinner <= 5:
                if self.random.random() <0.51:
                    spread_intensity = 1
                else:
                    spread_intensity = 2
            elif self.mucus_thinner <= 10:
                if self.random.random() <0.51:
                    spread_intensity = 2
                else:
                    spread_intensity = 3
            elif self.mucus_thinner <= 15:
                if self.random.random() <0.51:
                    spread_intensity = 3
                else:
                    spread_intensity = 4
            elif self.mucus_thinner <20:
                if self.random.random() <0.51:
                    spread_intensity = 4
                else:
                    spread_intensity = 5


        for i in range(spread_intensity + 1):
            muc_space = self.model.grid.get_cell_list_contents([self.pos])
            muc_no = 0
            muc_no = sum(1 for obj in muc_space if isinstance(obj, Mucin) == True)
            
            #Movement if limit of mucin is reached or random spread triggered
            if spread_intensity==0:
                percen_acti=.10
            else:
                percen_acti=.4
            if (i <= spread_intensity and self.random.random() <percen_acti ) or muc_no >= 5:
                muc_surround = self.model.grid.get_neighborhood(self.pos, moore = True)
                empty_space =[] # all the possible empty spaces around the agent
                bac_space =[]
                bac_biof_space=[]
                for obj in muc_surround:
                    if self.model.grid.is_cell_empty(obj):
                        empty_space.append(obj) 
                    if isinstance(obj, Pathogen):
                        bac_space.append(obj)
                for obj in bac_space:
                    if obj.biofilm_form ==True:
                        bac_biof_space.append(obj)

                if self.pos[1] == 3: #If above Bronchial, it cannot move down
                    x = self.pos[0]
                    y = self.pos[1]
                    possible_directions = [(x,y), (x+1,y), (x-1, y), (x+1, y+1), (x-1, y+1), (x,y+1)]
                    muc_spread_pos = self.random.choice(possible_directions)
                    self.model.grid.move_agent(self, muc_spread_pos)
                # elif self.pos[1] >= (self.model.grid.height-2):
                #     self.model.grid.move_agent(self, (self.pos[0], self.pos[1]-1 ))
                elif len(empty_space) > 1: # prioritize movement to an empty cell space
                    muc_spread_pos = self.random.choice(empty_space)
                    self.model.grid.move_agent(self, muc_spread_pos)
                elif len(bac_biof_space) > 1:
                    muc_spread_pos = self.random.choice(bac_biof_space)
                else: # random movement 
                    muc_spread_pos = self.random.choice(muc_surround)
                    self.model.grid.move_agent(self, muc_spread_pos)

                #If the "mucin went too far" if it dd it will "fall"
                muc_test = self.model.grid.get_neighbors(self.pos, moore = True, radius= 1)
                if (len(muc_test) < 10) and (self.pos[1] != 3):
                    self.model.grid.move_agent(self, (self.pos[0], self.pos[1]-1 ))



    #What happens each step
    def step(self):
        self.mucin_spread() #- im thinking add it at the end instead of the start (lol nvm its all those retrins wont lalow it)
        self.move_cilia()
        bronch_health_check = list(self.model.agents_by_type[Bronchial])
        for b in bronch_health_check: #change this so that it will trigger if any of them 
            if b.health < (b.init_health*0.75): #Infected state of body causes cough
                if self.model.step_count > 5: #only in infected state
                    if self.model.random.random() < 0.5:
                        if  (self.pos[0] == 1 or self.pos[0] == 0):
                            self.model.grid.remove_agent(self)
                            self.remove()
                            return
                        else:
                            self.move_cough()
                            break
                            #make cough work more if there is less viscosity or more empty cells between mucin
        if self.out_bound ==True:
            self.model.grid.remove_agent(self)
            self.remove()
            return
        

#This cell is used for the base class of the bacteria and biofilm formation
class Pathogen(mesa.Agent):
    def __init__(self, model, pos, health = 100, energy=100, strength = .5, bacteria_gain= 10, p_rep = 0.04, biofilm_form = False, p_unstick = 0.04, alive = True):
        super().__init__(model)
        self.pos = pos
        self.health = health #Lifespan of pathogen
        self.strength = strength #how much damage it deals to brocnhial
        self.bacteria_gain = bacteria_gain #how much "health" bacteria gains from bronchiol damage, did we even use this lowkey cause like they dont really gain from being 
        self.p_rep = p_rep #probability to trigger reproduction
        self.p_unstick = p_unstick #probability of bacteria in biofilm to "unstick" from biofilm
        self.energy=energy
        self.biofilm_form = biofilm_form
        self.alive = alive

    #Movement of pathogen is limited by mucus, and evasive of macrophages. Otherwise it is random
    def move_bacteria(self):
        #macrophage will move within mucin
        findneighbors = self.model.grid.get_neighbors(self.pos,True,False, radius =2)
        macro_free_list=[] #List of positions safe of macorphage
        distances=[] #List of possible mucin positions
        # maxmucin = [3] #default maxmucin value
#energy is increased when the bronchiales and gains every couple ticks and assumption of correct acmount nutrients, and divide loses energy and cant divide after a certian point. Health for the antibiotics, limitations parameter of how the bacteria heals or adapts to the antibiotic, but other than that once health is lost is isnt regain. 
#energy only gained during first attachtment, if we can add protional increases per step, if not ut in future directions, either losing energy when in conatact with antibiotic or a limit on the health you need for duplication or decrease the chances.


        
       #compiles positions that are macrophage and bronchial free, and the highest mucin position
        for agent in findneighbors: # Theres a chance that this is limiting it from moving up and only going left right and down
            if isinstance(agent,Mucin):
                distances.append(agent.pos[1])
            if not isinstance(agent,Macrophage) and not isinstance(agent,Bronchial):
                macro_free_found = agent.pos
                macro_free_list.append(macro_free_found)
        if len(distances) > 1:
            maxmucin=max(distances)
        else:
            maxmucin = 3

        if (self.pos[1])<=maxmucin: #this may have to be fixed
            

            for cells in findneighbors:
                #Check for bronchial neighbors to stick to
                if isinstance(cells,Bronchial):

                    #25% chance it doesn't move if it is in a biofilm (initial chance)
                    if (self.biofilm_form == True) and (self.random.random() > 0.25) : 
                        return 
                    
                    #count and limit the bacteria in one space
                    bac_space = self.model.grid.get_cell_list_contents([self.pos])
                    bac_no = 0
                    x,y = self.pos
                    bac_no = sum(1 for obj in bac_space if isinstance(obj, Pathogen) == True)
                    if bac_no>5: 
                        bron_free=[obj.pos for obj in findneighbors if not isinstance(obj,Bronchial)]
                        posible_free=[obj for obj in bron_free if obj in macro_free_list]
                        self.model.grid.move_agent_to_one_of(self,posible_free)
                        return
                        #will push it off but maintain the biofilm state and not move unless it detaches
                        
                    elif self.random.random() < 0.3: #Chance of pathogen detaching from Bronchiol and moving away
                        bron_free=[obj.pos for obj in findneighbors if not isinstance(obj,Bronchial)] 
                        posible_free=[obj for obj in bron_free if obj in macro_free_list]
                        self.model.grid.move_agent_to_one_of(self,posible_free)
                        self.biofilm_form = False
                        return #  confirmation that if it was on the biofilm it will be removed from biofilm state

                    elif self.biofilm_form ==True and self.random.random() > 0.90:
                        self.biofilm_form = False
            if self.biofilm_form ==True and self.random.random() > 0.60:
                self.biofilm_form = False

            if len(macro_free_list)>0: #not attached to bronchiol or part of biofilm = evasion of macrophages 
                self.model.grid.move_agent_to_one_of(self,macro_free_list) 
            else:
                return
        else:
            return
    #damaging the bronchiol - cell loses healt, brionchial gains health

    #Movement of pathogens affected by cilia
    def move_cilia(self):
        if self.pos[1] < 3 or self.biofilm_form == True:
            return
        1
        self.model.grid.move_agent(self, (self.pos[0]-1,self.pos[1]))
        #if biofilm is formed then we gotta lowkey limit the movement ig


    #Biofilm formation upon contact with other pathogens
    def biofilm_formation(self): # i lowkey dont think any oft his is right ehe
    #bacteria gain only here when in bioform gets to full in less time or something like that 
        #idea before implementation - model biofilm by just makeing them stick to each other and then increasing the health by a certain ffactor when x amount is present and maybe
        #we can also model it to have a certain step strength in a random direction that will decrease the more are connected? and we can have antibiotic deal damage exactly as large as the health or say it insta kills it vs deald this mich dMG when not insta kill
        #model prob of unstick with liek if random is (p sunstick then it will detach)
        #mucin within a one distance radius will begin to stick together
        #based on paper because cells are low motility when the are attached or .52 for slow nutrient comsuption ask maddie or .67 wtv
        
        
        neigh_test = self.model.grid.get_neighbors(self.pos, True, False,radius=2)
        bac_test = self.model.grid.get_neighbors(self.pos, True, True)
        if len(bac_test) <1:
            return
        for agent in bac_test:
            for obj in neigh_test:
                if isinstance(obj,Bronchial): 
                    if isinstance(agent, Pathogen) and self.random.random() <0.67: #test to see if the bacteria is connected to a pathogen
                        self.biofilm_form = True 
                else:
                    if isinstance(agent, Pathogen) and self.random.random() <0.52: #test to see if the bacteria is connected to a pathogen
                        self.biofilm_form = True 
  
                        
                                         
        #this isnt super great but rn its just a probability of it "becoming"part of the biofilm, and the detahcment false code is in the part of move

    #bacteria would not survive in the open air for to long, so if it has been in the open air for an hour it will remove (max 45 mins for Pseudomonas a)
    def position_test(self):
        findneighbors = self.model.grid.get_neighbors(self.pos,True,False, radius =2)
        for b in findneighbors: #looks through all possible neighrbors before killing
            if isinstance(b, Mucin):
                return
                
        self.alive = False
                           

    #Reproduction rate of pathogen
    def spawn_offspring(self):
        #using half of its health, it can spawn offspring
        self.energy /= 2
        new_bac= Pathogen(self.model, self.pos,self.health,self.energy, self.strength, self.bacteria_gain, self.p_rep)
        self.model.grid.place_agent(new_bac, self.pos)



#need to manipulate macrophage and pathogen so energy function is like lab 6

    #What happens each step
    def step(self):
        self.position_test()
        if self.health <= 0 or self.alive == False:
            self.model.grid.remove_agent(self)
            self.remove()
            return
        bac_space = self.model.grid.get_cell_list_contents([self.pos])
        bac_no = sum(1 for obj in bac_space if isinstance(obj, Pathogen) == True)
        if  self.biofilm_formation==False and (self.pos[0] ==0): #Cilia push pathogens out as a primary line of defense
            self.model.grid.remove_agent(self)
            self.remove()
            return
        elif bac_no < 3: 
            self.move_cilia() #Assumption of cilia only pushing pathogens out (not in )
        self.move_bacteria() 
        self.biofilm_formation() #formation of biofilm
        #Movement, does not move when touching Bronchial 
        #code for bacteria touching the 


        # # #self.biofilm_formation()r
        # self.energy-=1
        #     # self.alive = False
        if self.random.random() < self.p_rep :
            self.spawn_offspring()
        if self.model.step_count%3==1:
            if self.energy!=20:                       
                self.energy=20
        if self.energy<=0:
            self.model.grid.remove_agent(self)
            self.remove()
        
            #this is the assumption that every 3 steps all there are enough nutrients that bacteria regain 25% of there lost energy 


#This cell is used for the base class of bronchial
class Bronchial(mesa.Agent):
    def __init__(self, model, pos, health = 100, init_health=100, ): 
        super().__init__(model)
        self.init_health = init_health #initial health of bronchial
        self.health = health
        self.pos = pos
        #should we create a layer of underlaying cells that can be invaded
        #we are starting with higher mucin levels due to the types of conditions we are modeling 
    
        
    #Healing mechanism after injury state
    def healing(self):
        bronch_space = self.model.grid.get_neighbors(self.pos, moore= False)
        for obj in bronch_space:
            if isinstance(obj,Pathogen):
                continue
            elif self.health<self.init_health:
                self.health +=5
                break
    

    #Replenishment mechanism after death state
    def replacement(self):
        for i in range(len(self.model.death_step_list)):
            death_count=(self.model.step_count - self.model.death_step_list[i])
            if death_count>=21:
                deadpos = self.model.death_pos_list[i] #this way cells that are newly generated can fill in the the middle the same cell should be remade because theyre popped from the list
                #if the nieghboring cell has been dead for the full timepoint, assumption a full replacement cycle is 20hrs and it appear on the 21st hour, you dont count the first step because that step is where the death was happening, the next step is where the replacement can start to occur
                allpathogendeathpos =[obj for obj in self.model.grid.get_cell_list_contents(deadpos) if isinstance(obj,Pathogen)]
                if (deadpos[0]==(self.pos[0]+1) or deadpos[0]==(self.pos[0]-1)) and len(allpathogendeathpos)==0:
                    health=100
                    repbronch = Bronchial(self.model,deadpos,health,self.init_health,)
                    self.model.grid.place_agent(repbronch,deadpos)
                    self.model.death_step_list.pop(i)
                    self.model.death_pos_list.pop(i)
                    break
                elif len(allpathogendeathpos)>0: #assume the only thing that can be in that cell is a pathogen and itll push back healing by two and it can't heal with its there i think?
                    self.model.death_step_list[i]+=2 
                #should we check if its bronchiol or pathogen if the upper part eliminating it from the list once its replaced should prevent other nieghbor from replacing it 
                 

    #In infected state, macrophages get called as body's self defense system
    def call_macro(self):
    #Limit macrophage in the environment to 100 and in the bloodstream to 5
        tot_macro = 0 #total macrophages in grid
        tot_blood_macro = 0 #total macrophages in bloodstream
        for x in range(self.model.grid.width):
            for y in range(self.model.grid.height):
                pos = x,y
                grid_macro = self.model.grid.get_cell_list_contents(pos)
                for m in grid_macro:
                    if isinstance(m, Macrophage):
                        tot_macro += 1
            for y in range(2):
                pos = x,y
                blood_macro = self.model.grid.get_cell_list_contents(pos)
                for m in blood_macro:   
                    if isinstance(m, Macrophage):
                        tot_blood_macro += 1 
        while tot_macro < 50 and tot_blood_macro < 3: #Call macrophages into bloodstream 
            x = self.random.randrange(self.model.grid.width)
            y = self.random.randrange(2)
            pos = (x,y)
            self.model.call_macro(pos)
            tot_macro += 1
            tot_blood_macro += 1

    #Secretion of mucin in infected state, health of bronchial impacts amount secreted
    def call_mucin(self): 
        infect_int = 1 
        if self.health <= (self.init_health*0.25):
            infect_int = 5
        elif self.health <=(self.init_health*0.50):
            infect_int =  3
        pos=(self.pos[0],self.pos[1]+1)
        for i in range(infect_int):
            self.model.call_mucin(pos)


    
    #Injury of Bronchiol done by pathogens
    def health_loss(self):  
        bronch_space = self.model.grid.get_neighbors(self.pos, moore=False)
        bact_no = 0
        bact_no += sum(obj.strength for obj in bronch_space if (isinstance(obj, Pathogen) == True and obj.health>0))
        self.health= max(0, self.health - bact_no)

        

    #what happens each step
  
    def step(self):
        self.healing()
        if self.model.step_count>0:
            self.health_loss()
        
        if self.health < (self.init_health*0.75) and self.model.step_count%4==0 and (self.health!=0): #Health determines how much mucin is called, macrophages are predetermined
            self.call_macro()
        if self.health < (self.init_health*0.75) and (self.health!=0):
            self.call_mucin()
    
        if self.health <= 0:
            self.model.death_step_list.append(self.model.step_count)
            self.model.death_pos_list.append(self.pos)
        if self.health <= 0:
            self.model.grid.remove_agent(self)
            self.remove()
            return
        self.replacement()
        self.model.death_tracker()



