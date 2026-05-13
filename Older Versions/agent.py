#this cell is used for the base class of antibiotics
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
            
        # if muc_no >= 5:
        #     limit_move = 0.5
        # # elif muc_no >=3:
        # #     limit_move = 0.75
        # # move_mag = round(3*limit_move) #right now limiting movement to float values will break pos, i think instead we need flat values
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
        
        # elif len(biofilm_bac) > 1: #formation of biofilm will decrease effectiveness and will keep it stuck on it and decrease health
        #     bac_atk = self.random.choice(bac)
        #     bac_atk.health -= 75
        #     self.health -=5

        # elif len(biofilm_bac) > 3: #formation of biofilm will decrease effectiveness and will keep it stuck on it and decrease health
        #     bac_atk = self.random.choice(bac)
        #     bac_atk.health -= 50
        #     self.health -=5
            
        # elif len(biofilm_bac) > 5: #formation of stronger biofilm will decrease further
        #     bac_atk = self.random.choice(bac)
        #     bac_atk.health -= 25
        #     self.health -=5
        # #baes on trur or nor``

        elif len(biofilm_bac) > 1: #formation of stronger biofilm will decrease further
            bac_atk = self.random.choice(bac)
            bac_atk.health -= 25
            self.health -=5
        #baes on trur or nor``

            


            #the antibiotic slowly dealing damage to the bacteria not immediate and the bacteria can keep functioning while being attack (find paper) and then eventually randomize and sometimes they ust weaken alot
#set up that bioflim attracts mucin so that antibiotic diffuses slower, and once in the bioflim itll diffuse slowest.
#schedule event for when the cells starts attacking not immediate in biofilm
#right now it only attacks one even if theres 5, we can run a for loop to make it attack all w indexing

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
        