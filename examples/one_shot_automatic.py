from basics.setup import One_shot_parameters
from main import main
from experiments.save_results import save_results
from basics.logger import color_text

scenario_name = "reach_avoid" # "treasure_hunt", or "treasure_hunt"
pars = One_shot_parameters(scenario_name = scenario_name) # Get the parameters
pars.GPT_model = "gpt-4o" # "gpt-4o", "gpt-3.5-turbo"
pars.spec_checker_enabled = True
pars.syntax_checker_enabled = True

N_experiments = 3 # Number of experiments to run

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