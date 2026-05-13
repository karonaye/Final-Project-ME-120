import argparse
import subprocess
 
from agents import Antibiotic, Macrophage, Mucin, Pathogen, Bronchial
from Bronchioles_Infection import LungModel, AGENT_COLORS
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import Slider, SolaraViz, make_plot_component, make_space_component
 
from single_run_analysis import run_single_analysis
from comparison_analysis import run_comparison_analysis
 
 

MODEL_PARAMETERS = {
"width": 40, # Grid width
    "height": 20, # Grid height
    "seed": 100, # Random seed for reproducibility
    #this is wher eu would put the parameter s(if we had any)
    "init_health_Bronchial": 100, # heaalth of bironchil
    "a_radius":1.4, #Raidius of Antibiotic in Meter(multiplied by 10**-10)
    "mucus_thinner":5,  #% of mucus thinner concentration
    "start_pathogen":16, #no of starter pathgens
    "start_macrophage": 5, #starter macro
    "start_anti" : 35, # how much antibiotics spawn pet teusn
    "call_anti": 40, #turn that starts calling anirbiotics
    "anti_doses": 8, #turn that starts calling anirbiotics
    "call_mucus_thinner":100, # turn for mucus thinner to start working
}
 
def lung_portrayal(agent):
    if agent is None:
        return
    p = {"size": 25}
    if isinstance(agent, Mucin):
        p.update({"color": AGENT_COLORS["Mucin"], "marker": "o", "zorder": 3, "size": 45})
    elif isinstance(agent, Bronchial):
        p.update({"color": AGENT_COLORS["Bronchial"], "marker": "o", "zorder": 60})
    elif isinstance(agent, Pathogen):
        p.update({"color": AGENT_COLORS["Pathogen"], "marker": "o", "zorder": 61, "size": 25})
    elif isinstance(agent, Antibiotic):
        p.update({"color": AGENT_COLORS["Antibiotic"], "marker": "o", "zorder": 4, "size": 25})
    elif isinstance(agent, Macrophage):
        p.update({"color": AGENT_COLORS["Macrophage"], "marker": "o", "zorder": 5, "size": 25})
    return p
 
model_params = {
    "width": Slider("Width", MODEL_PARAMETERS["width"], 10, 100),
    "height": 20,
    "init_health_Bronchial": Slider("Initial Health of Bronchiol", MODEL_PARAMETERS["init_health_Bronchial"], 10, 300),
    "a_radius": Slider("Radius of Antibiotic", MODEL_PARAMETERS["a_radius"], 0.3, 5),
    "mucus_thinner": Slider("% dosage of mucus thinner", MODEL_PARAMETERS["mucus_thinner"], 3, 20),
    "start_pathogen": Slider("Initial Pathogen Count", MODEL_PARAMETERS["start_pathogen"], 1, 300),
    "start_macrophage": Slider("Initial Macrophage count", MODEL_PARAMETERS["start_macrophage"], 5, 50),
    "start_anti": Slider("Antibiotic concentration", MODEL_PARAMETERS["start_anti"], 5, 100),
    "call_anti": Slider("Turn to call Antibiotics", MODEL_PARAMETERS["call_anti"], 4, 200),
    "anti_doses": Slider("Time to redose Antibiotics", MODEL_PARAMETERS["anti_doses"], 4, 200),
    "call_mucus_thinner": Slider("Turn to call Mucus Thinner", MODEL_PARAMETERS["call_mucus_thinner"], 4, 200),
}
 
 
def run_viz():
    simulator = ABMSimulator()
    model_instance = LungModel(simulator=simulator, **MODEL_PARAMETERS)
    space_component = make_space_component(lung_portrayal, draw_grid=True)
    lineplot_component = make_plot_component({
        "Bronchial": AGENT_COLORS["Bronchial"],
        "Mucin": AGENT_COLORS["Mucin"],
        "Pathogen": AGENT_COLORS["Pathogen"],
        "Antibiotic": AGENT_COLORS["Antibiotic"],
        "Macrophage": AGENT_COLORS["Macrophage"]
    })
    page = SolaraViz(
        model_instance,
        components=[space_component, lineplot_component],
        model_params=model_params,
        name="Lung Infection Model",
        simulator=simulator,
    )
    return page
 
 
page = run_viz()

if __name__ == "__main__":
    import sys
    # Only run argparse if NOT being called by solara
    if "solara" not in sys.argv[0]:
        parser = argparse.ArgumentParser(description="Lung ABM Runner")
        parser.add_argument(
            "--mode",
            choices=["single", "compare", "viz"],
            default="single",
        )
        args = parser.parse_args()

        if args.mode == "single":
            print("Running single simulation...")
            run_single_analysis()

        elif args.mode == "compare":
            print("Running comparison simulation...")
            run_comparison_analysis()
