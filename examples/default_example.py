from basics.setup import Default_parameters
from main import main
from experiments.save_results import save_results

scenario_name = "treasure_hunt"                             # "reach_avoid", or "treasure_hunt"
pars = Default_parameters(scenario_name = scenario_name)    # Get the parameters
pars.save_results = False                                   # Save the results to a file
pars.GPT_model = "gpt-3.5-turbo"                            # GPT model to use ("gpt-4o", "gpt-3.5-turbo")
pars.spec_checker_enabled = False                           # Enable the specification checker
pars.syntax_checker_enabled = False                         # Enable the syntax checker
pars.animate_final_trajectory = True                        # Animate the final trajectory

try:
    messages, task_accomplished = main(pars)                # Run the experiment
except Exception as e:
    print(e)
    task_accomplished = False
    messages = []

if pars.save_results:
        save_results(pars, messages, task_accomplished)