from basics.setup import Default_parameters
from main import main
from experiments.save_results import save_results
from basics.logger import color_text

scenario_name = "treasure_hunt"                             # "reach_avoid", "narrow_maze", or "treasure_hunt"
pars = Default_parameters(scenario_name = scenario_name)    # Get the parameters
pars.save_results = True                                    # Save the results to a file

try:
    messages, task_accomplished = main(pars)                # Run the experiment
except Exception as e:
    print(e)
    task_accomplished = False

if pars.save_results:
        save_results(pars, messages, task_accomplished)