from basics.setup import non_STL_default_parameters
from non_STL_main import main
from experiments.save_results import save_results
from basics.logger import color_text

scenario_name = "reach_avoid" # "reach_avoid", or "treasure_hunt"
pars = non_STL_default_parameters(scenario_name = scenario_name) # Get the parameters
pars.GPT_model = "gpt-4o" # "gpt-4o", "gpt-3.5-turbo"
pars.spec_checker_enabled = False
pars.syntax_checker_enabled = False
pars.STL_included = False

N_experiments = 1 # Number of experiments to run

for i in range(N_experiments):
    print(color_text(f"Experiment {i+1}/{N_experiments}", "yellow"))
    try:
        messages, task_accomplished, waypoints = main(pars) # Run the experiment
    except Exception as e:
        print(e)
        task_accomplished = False
        messages = []

    if pars.save_results:
            save_results(pars, messages, task_accomplished)