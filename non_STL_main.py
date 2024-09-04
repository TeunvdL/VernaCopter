from LLM.GPT import GPT
from LLM.NL_to_STL import *
from STL.STL_to_path import *
from STL.spec_check import *
from basics.logger import color_text
from basics.scenarios import *
from basics.setup import Default_parameters
from visuals.simulation.simulation import simulate
from visuals.visualization import *

def main(pars=Default_parameters()): 
    # Set up scenario
    scenario = Scenarios(pars.scenario_name)    # Set up the scenario
    if pars.show_map: scenario.show_map()       # Show the map if the flag is set

    # Initializations
    T = scenario.T_initial                      # Initial time horizon in seconds
    N = int(T/pars.dt)                          # total number of time steps
    previous_messages = []                      # Initialize the conversation
    status = "active"                           # Initialize the status of the conversation
    x0 = scenario.x0                            # Initial position
    all_x = np.expand_dims(x0, axis=1)          # Initialize the full trajectory
    processing_feedback = False                 # Initialize the feedback processing flag
    spec_checker_iteration = 0                  # Initialize the specification check iteration

    translator = NL_to_STL(scenario.objects, N, pars.dt, print_instructions=pars.print_ChatGPT_instructions, GPT_model = pars.GPT_model)

    ### Main loop ###
    while status == "active":

        # Initialize/reset the flags
        spec_accepted = False
        trajectory_accepted = False

        # Get the specification
        messages, status = translator.gpt_conversation(instructions_file=pars.instructions_file, 
                                                        previous_messages=previous_messages, 
                                                        processing_feedback=processing_feedback, 
                                                        status=status, automated_user=pars.automated_user, 
                                                        automated_user_input=scenario.automated_user_input)
        
        if status == "exited": # If the user exits the conversation, break the loop
            break

        # get the waypoints
        x = translator.get_waypoints(messages)
        # append 3 extra axes to the waypoints to account for empty x, y, z velocities
        x = np.vstack((x, np.zeros((3, x.shape[1]))))

    # try:
        # spec_checker = Spec_checker(scenario.objects, x, N, pars.dt)
        # inside_objects_array = spec_checker.get_inside_objects_array()
        visualizer = Visualizer(x, scenario, animate=False)
        fig, ax = visualizer.visualize_trajectory()
        # plt.pause(1)
        # fig, ax = spec_checker.visualize_spec(inside_objects_array)
        plt.pause(1)
        if pars.spec_checker_enabled and spec_checker_iteration < pars.spec_check_limit:
            spec_check_response = spec_checker.GPT_spec_check(scenario.objects, inside_objects_array, messages)
            trajectory_accepted = spec_checker.spec_accepted_check(spec_check_response)
            if not trajectory_accepted:
                print(color_text("The trajectory is rejected by the checker.", 'yellow'))
                spec_checker_message = {"role": "system", "content": f"Specification checker: {spec_check_response}"}
                messages.append(spec_checker_message)
                processing_feedback = True
            spec_checker_iteration += 1
        elif spec_checker_iteration > pars.spec_check_limit:
            print(color_text("The program is terminated.", 'yellow'), "Exceeded the maximum number of spec check iterations.")
            break

        if np.isnan(x).all():
            raise Exception("The trajectory is infeasible.")
    
        if pars.manual_trajectory_check_enabled:
            # Ask the user to accept or reject the trajectory
            while True:
                response = input("Accept the trajectory? (y/n): ")
                if response.lower() == 'y':
                    print(color_text("The trajectory is accepted.", 'yellow'))
                    trajectory_accepted = True
                    break  # Exit the loop since the trajectory is accepted
                elif response.lower() == 'n':
                    print(color_text("The trajectory is rejected.", 'yellow'))
                    trajectory_accepted = False
                    break  # Exit the loop since the trajectory is rejected
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        if trajectory_accepted:
            all_x = np.hstack((all_x, x[:,1:]))
            x0 = x[:, -1]
            print("New position after trajectory: ", x0)

        # except:
        #     print(color_text("The trajectory is infeasible.", 'yellow'))
        #     break

        previous_messages = messages

        if pars.automated_user and (trajectory_accepted or not pars.spec_checker_enabled):
            all_x = np.hstack((all_x, x[:,1:]))
            break
        
    # Visualize the full trajectory
    plt.close('all')
    if all_x.shape[1] == 1:
        print(color_text("No trajectories were accepted. Exiting the program.", 'yellow'))
    else:
        print(color_text("The full trajectory is generated.", 'yellow'))
        simulate(pars, scenario, all_x) # Animate the final trajectory

    spec_checker = Spec_checker(scenario.objects, all_x, N, pars.dt)
    inside_objects_array = spec_checker.get_inside_objects_array()
    task_accomplished = spec_checker.task_accomplished_check(inside_objects_array, pars.scenario_name)

    print(color_text("The program is completed.", 'yellow'))

    return messages, task_accomplished, all_x

if __name__ == "__main__":
    pars = Default_parameters()
    main()