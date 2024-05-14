from basics.setup import One_shot_parameters
from main import main
from experiments.save_results import save_results
from basics.logger import color_text

scenario_name = "treasure_hunt" # "reach_avoid", "narrow_maze", or "treasure_hunt"
pars = One_shot_parameters(scenario_name = scenario_name) # Get the parameters

N_experiments = 1

for i in range(N_experiments):
    print(color_text(f"Experiment {i+1}/{N_experiments}", "yellow"))
    try:
        messages, task_accomplished = main(pars) # Run the experiment
    except Exception as e:
        print(e)
        task_accomplished = False
        messages = []

    if pars.save_results:
            save_results(pars, messages, task_accomplished)