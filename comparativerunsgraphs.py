import matplotlib.pyplot as plt
from Bronchioles_Infection import LungModel, ABMSimulator, AGENT_COLORS
 
#Once you have chosen the ideal parameters, you can run this cell to compare the two values!
#This will run a comparison of the concentrations of Pathogens and Bronchials in the each trial
# Set the step value
steps_to_run = 60
 
def run_comparison_analysis():
    # Set the first parameters here!
    #Change these parameters to experiment with the model!
    MODEL_PARAMETERS_1 = {
        "width": 40, # Grid width
        "height": 20, # Grid height
        "seed": 100, # Random seed for reproducibility
        #this is wher eu would put the parameter s(if we had any)
        "init_health_Bronchial": 100, # heaalth of bironchil
        "a_radius":1.4, #Raidius of Antibiotic in Meter(multiplied by 10**-10)
        "mucus_thinner":1,  #% of mucus thinner concentration
        "start_pathogen":20, #no of starter pathgens
        "start_macrophage": 5, #starter macro
        "start_anti" : 15, # how much antibiotics spawn pet teusn
        "call_anti": 30, #turn that starts calling anirbiotics
        "anti_doses": 10, #turn that starts calling anirbiotics
        "call_mucus_thinner":100, # turn for mucus thinner to start working
    }
 
    print(f"First simulation running")
 
    first_simulator = ABMSimulator()
    # New model instance separate from the one used in the SolaraViz
    first_model = LungModel(
        simulator=first_simulator,
        **MODEL_PARAMETERS_1
    )
 
    # for _ in range(steps_to_run):
    #     backup_model.step()
    first_simulator.run_for(steps_to_run)
    t1 = first_model.datacollector.get_model_vars_dataframe()
 
 
    # Set the second parameters here!
    MODEL_PARAMETERS_2 = {
        "width": 40, # Grid width
        "height": 20, # Grid height
        "seed": 100, # Random seed for reproducibility
        #this is wher eu would put the parameter s(if we had any)
        "init_health_Bronchial": 100, # heaalth of bironchil
        "a_radius":1.4, #Raidius of Antibiotic in Meter(multiplied by 10**-10)
        "mucus_thinner":20,  #% of mucus thinner concentration
        "start_pathogen":20, #no of starter pathgens
        "start_macrophage": 5, #starter macro
        "start_anti" : 15, # how much antibiotics spawn pet teusn
        "call_anti": 30, #turn that starts calling anirbiotics
        "anti_doses": 10, #turn that starts calling anirbiotics
        "call_mucus_thinner":80, # turn for mucus thinner to start working
    }
 
    print(f"Second simulation running")
 
    second_simulator = ABMSimulator()
    # New model instance separate from the one used in the SolaraViz
    second_model = LungModel(
        simulator=second_simulator,
        **MODEL_PARAMETERS_2
    )
 
    # for _ in range(steps_to_run):
    #     backup_model.step()
    second_simulator.run_for(steps_to_run)
    t2 = second_model.datacollector.get_model_vars_dataframe()
 
 
 
    plt.figure(figsize=(12, 6))
 
    plt.plot(t1.index, t1["Pathogen"], color=AGENT_COLORS["Pathogen"], label="Pathogen 1", linewidth=2.5)
    plt.plot(t1.index, t1["Bronchial"], color=AGENT_COLORS["Bronchial"], label="Bronchiol 1", linewidth=2.5)
    plt.plot(t2.index, t2["Pathogen"], color=AGENT_COLORS["Pathogen"], label="Pathogen 2", linewidth=2.5, ls = '--')
    plt.plot(t2.index, t2["Bronchial"], color=AGENT_COLORS["Bronchial"], label="Bronchial 2", linewidth=2.5, ls = '--')
 
 
    # Formatting
    plt.title("Population Comparison Tracker")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Population Count")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1)) # Puts legend outside the plot
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Trial_Comparison_Populations.png", dpi=300)
 
    #note: if you would like to compare more values, it is possible to copy paste the code of the parameters and running said parameters in addition to adding the values into the plot!
 
    plt.figure(figsize=(12, 6))
 
    plt.plot(t1.index, t1["Mucin"], color=AGENT_COLORS["Mucin"], label="Mucin 1", linewidth=2.5)
    plt.plot(t2.index, t2["Mucin"], color=AGENT_COLORS["Mucin"], label="Mucin 2", linewidth=2.5, ls = '--')
 
 
    # Formatting
    plt.title("Mucin Comparison")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Mucin Count")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1)) # Puts legend outside the plot
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Graphs/Trial_Comparison_Mucin.png", dpi=300)
 
 
    #using t1 and t2 from above, the data of the bronchial health and biofilm is compiled
    t1_agent = first_model.datacollector.get_agent_vars_dataframe()
    t2_agent = second_model.datacollector.get_agent_vars_dataframe()
 
    t1_health = t1_agent.groupby("Step")["Bronch_health"].mean()#index the step, average the health value
    t2_health = t2_agent.groupby("Step")["Bronch_health"].mean()
    t1_biof = t1_agent.groupby("Step")["Biofilm_formed"].sum()#index the step, average the health value
    t2_biof = t2_agent.groupby("Step")["Biofilm_formed"].sum()
 
 
    plt.figure(figsize=(12, 6))
    plt.plot(t1_health.index, t1_health.values, color="red", linewidth=2.5, label ="Trial 1")
    plt.plot(t2_health.index, t2_health.values, color="blue", linewidth=2.5, label = "Trial 2")
 
    # Formatting
    plt.title("Comparison of Average Bronchial Health Profile")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Bronchial Health")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1)) # Puts legend outside the plot
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Graphs/Trial_Comparison_Bronchial_Health.png", dpi=300)
 
 
    plt.figure(figsize=(12, 6))
    plt.plot(t1_biof.index, t1_biof.values, color="red", linewidth=2.5, label ="Trial 1")
    plt.plot(t2_biof.index, t2_biof.values, color="blue", linewidth=2.5, label = "Trial 2")
 
    #Formatting
    plt.title("Comparison of Biofilm Formation")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Biofilm Formation")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1)) # Puts legend outside the plot
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Graphs/Trial_Comparison_Biofilm_Formation.png", dpi=300)
 
 
 
    #next is just a general comparison
    Trials = ["Trial 1", "Trial 2"]
    max_p_trials = [max(t1["Pathogen"]), max(t2["Pathogen"])]
    min_b_trials = [min(t1["Bronchial"]), min(t2["Bronchial"])]
    avg_health_range = [ (t1_health.max() - t1_health.min()), (t2_health.max() - t2_health.min())]
 
 
    print("Summary of Parameters")
    print("Trial 1")
    for i, data in MODEL_PARAMETERS_1.items():
        print(f"{i} = {data}")
 
    print("\nTrial 2")
    for i, data in MODEL_PARAMETERS_2.items():
        print(f"{i} = {data}")
 
    print("\nSummary of Data obtained")
    print(f"The higher pathogen count is found in {Trials[max_p_trials.index(max(max_p_trials))]} with a maximum count of {(max(max_p_trials))}")
    print(f"More Bronchial death is found in {Trials[min_b_trials.index(min(min_b_trials))]} with a minimum Bronchial count of {(min(min_b_trials))}")
    print(f"The first trial's average bronchial health profile has a range of {avg_health_range[0]}")
    print(f"The second trial's average bronchial health profile has a range of {avg_health_range[1]}")
    print(f"The Average bronchial Health Profile is more varied in {Trials[avg_health_range.index(max(avg_health_range))]}.")
 
 
if __name__ == "__Allfilerun__":
    run_comparison_analysis()