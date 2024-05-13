import os
import json
from basics.logger import color_text

def save_results(pars, messages, task_accomplished):
    print(color_text("Saving the results...", 'yellow'))
    this_directory = os.path.dirname(os.path.abspath(__file__))
    experiments_directory = this_directory + f'/{pars.scenario_name}/'

    if not os.path.exists(experiments_directory):
        os.makedirs(experiments_directory)

    # check the highest experiment id in the folder and increment by 1
    experiment_id = 0
    for file in os.listdir(experiments_directory):
        if file.endswith(".json"):
            filename = file.split('.')[0] # remove the extension '.json'
            experiment_id = max(experiment_id, int(filename.split('_')[0])) # extract the experiment id from the filename '1_messages' -> 1
    experiment_id += 1

    messages_file_name = f'{experiment_id}_messages.json'
    messages_file_path = os.path.join(experiments_directory, messages_file_name)

    with open(messages_file_path, 'w') as f:
        json.dump(messages, f)


    ### Generate metadata file ###

    # find and count number of user messages
    user_message_count = 0
    for message in messages:
        if message['role'] == 'user':
            user_message_count += 1

    metadata = {
        "scenario_name": pars.scenario_name,
        "task_accomplished": task_accomplished,
        "user_message_count": user_message_count,
        "GPT_version": pars.GPT_model,
        "syntax_checker_enabled": pars.syntax_checker_enabled,
        "spec_checker_enabled": pars.spec_checker_enabled,
        "dynamicless_check_enabled": pars.dynamicless_check_enabled,
        "manual_spec_check_enabled": pars.manual_spec_check_enabled,
        "manual_trajectory_check_enabled": pars.manual_trajectory_check_enabled,
        "syntax_check_limit": pars.syntax_check_limit,
        "spec_check_limit": pars.spec_check_limit,
        "max_acc": pars.max_acc,
        "max_speed": pars.max_speed,
        "T_initial": pars.T_initial,
        "dt": pars.dt,
    }

    metadata_file_name = f'{experiment_id}_METADATA.json'
    metadata_file_path = os.path.join(experiments_directory, metadata_file_name)

    with open(metadata_file_path, 'w') as f:
        json.dump(metadata, f)