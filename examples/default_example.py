from basics.config import Default_parameters
from main import main
from experiments.save_results import save_results

scenario_name = "treasure_hunt"                             # "reach_avoid", or "treasure_hunt"
pars = Default_parameters(scenario_name = scenario_name)    # Get the parameters

try:
    messages, task_accomplished, waypoints = main(pars)     # Run the main program
except Exception as e:
    print(e)
    task_accomplished = False
    messages = []

if pars.save_results:
        save_results(pars, messages, task_accomplished, waypoints)