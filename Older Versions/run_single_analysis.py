import matplotlib.pyplot as plt
from Bronchioles_Infection import LungModel, ABMSimulator, AGENT_COLORS
 
# Change these parameters to experiment with the model!
MODEL_PARAMETERS = {
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
# Change this value to run the simulation for more or fewer steps
steps_to_run = 300
 
def run_single_analysis():
    print(f"Running simulation for {steps_to_run} steps...")
 
    backup_simulator = ABMSimulator()
 
    # New model instance separate from the one used in the SolaraViz
    backup_model = LungModel(
        simulator=backup_simulator,
        **MODEL_PARAMETERS
    )
 
    # for _ in range(steps_to_run):
    #     backup_model.step()
 
    backup_simulator.run_for(steps_to_run)
 
    df = backup_model.datacollector.get_model_vars_dataframe()
    df_agent = backup_model.datacollector.get_agent_vars_dataframe()
 
    #Graph of Overall Population
    plt.figure(figsize=(12, 6))
 
    plt.plot(df.index, df["Mucin"], color=AGENT_COLORS["Mucin"], label="Mucin", linewidth=2.5)
    plt.plot(df.index, df["Bronchial"], color=AGENT_COLORS["Bronchial"], label="Bronchiol", linewidth=2.5)
    plt.plot(df.index, df["Pathogen"], color=AGENT_COLORS["Pathogen"], label="Pathogen", linewidth=2.5)
    plt.plot(df.index, df["Macrophage"], color=AGENT_COLORS["Macrophage"], label="Macrophage", linewidth=2.5)
    plt.plot(df.index, df["Antibiotic"], color=AGENT_COLORS["Antibiotic"], label="Antibiotic", linewidth=2.5)
 
    #Formatting and Display
    plt.title("Pseudomonas Aeruginosa Bronchiole Infection: Population Dynamics")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Population Count")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1)) # Puts legend outside the plot
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Population_Dynamics.png", dpi=300)
 
    # TIP: To save this image for your PDF, right-click the plot and select "Save image as..."
    # Alternatively, uncomment the line below to save it directly to your folder:
    # plt.savefig("my_time_series.png", dpi=300)
 
 
     # lol this is the only thing i can think of to make it easier to read for now esp if we r working with so many types 
 
    #Graph of Bronchial Health
    plt.figure(figsize=(12, 6))
    # agents_df = df_agent.index.get_level_values("AgentID").unique()
    # for i in agents_df:
    #     health_b = df_agent.xs(i, level="AgentID")
    #     plt.plot(health_b.index, health_b["Bronch_health"], color=random.choice(random_color), linewidth=2.5)
    df_health_b = df_agent.groupby("Step")["Bronch_health"].mean()
    plt.plot(df_health_b.index, df_health_b.values, color="red", linewidth=2.5)
 
    # Formatting
    plt.title("Health Tracker of Bronchiole")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Bronchial Health")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Bronchiole_Health.png", dpi=300)
 
    #Graph of Biofilm formation
    plt.figure(figsize=(12, 6))
 
    # bact_biofilm = sum(1 for i in agents_df if i.biofilm_form == True)
    df_biof = df_agent.groupby(level = "Step")["Biofilm_formed"].sum()
    plt.plot(df_biof.index, df_biof.values, color="blue", linewidth=2.5)
 
    # Formatting
    plt.title("Biofilm")
    plt.xlabel("Time (Steps)")
    plt.ylabel("Pathogens with Biofilm Formed")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("Graphs/Biofilm_Formation.png", dpi=300)
 
 
if __name__ == "__Allfilerun__":
    run_single_analysis()