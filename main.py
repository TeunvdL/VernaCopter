from STL_to_path import *
from LLM.GPT import *
from LLM.NL_to_STL import *
from visualization import *
from logger import color_text
from scenarios import *
from spec_check import *
from simulation.pid_edited_pipeline import run
from setup import setup_parameters
from experiments.save_results import save_results

pars = setup_parameters()

# Set up scenario
scenario = Scenarios(pars.scenario_name)
objects = scenario.objects
x0 = scenario.starting_state
if pars.show_map: scenario.show_map()
pars.T_initial = scenario.get_time_horizon()

# Initializations
T = pars.T_initial                      # Initial time horizon in seconds
N = int(T/pars.dt)                      # total number of time steps
previous_messages = []                  # Initialize the conversation
status = "active"                       # Initialize the status of the conversation
all_x = np.expand_dims(x0, axis=1)      # Initialize the full trajectory
processing_feedback = False             # Initialize the feedback processing flag
spec_accepted = False                   # Initialize the specification acceptance flag
trajectory_accepted = False             # Initialize the trajectory acceptance flag
syntax_checked_spec = None              # Initialize the syntax checked specification
spec_checker_iteration = 0              # Initialize the specification check iteration
syntax_checker_iteration = 0            # Initialize the syntax check iteration

translator = NL_to_STL(objects, N, pars.dt, print_instructions=pars.print_ChatGPT_instructions, GPT_model = pars.GPT_model)

### Main loop ###
while status == "active":
    if syntax_checked_spec is None:
        messages, status = translator.gpt_conversation(previous_messages=previous_messages, processing_feedback=processing_feedback, status=status)
        processing_feedback = False

        if status == "exited":
            break
        spec = translator.get_specs(messages)
    else:
        spec = syntax_checked_spec
        syntax_checked_spec = None
    print("Extracted specification: ", spec)

    solver = STLSolver(spec, objects, x0, T)

    if pars.dynamicless_check_enabled and not spec_accepted: # Check the specification without dynamics
        print(color_text("Checking the specification without dynamics...", 'yellow'))
        try:
            no_dynamics_x, no_dynamics_u = solver.generate_trajectory(pars.dt, pars.max_acc, pars.max_speed, verbose=pars.solver_verbose, include_dynamics=False)
            spec_checker = Spec_checker(objects, no_dynamics_x, N, pars.dt)
            inside_objects_array = spec_checker.get_inside_objects_array()
            visualizer = Visualizer(no_dynamics_x, objects, animate=False)
            fig, ax = visualizer.visualize_trajectory()
            plt.pause(1)
            fig, ax = spec_checker.visualize_spec(inside_objects_array)
            plt.pause(1)

            if pars.spec_checker_enabled and spec_checker_iteration < pars.spec_check_limit:
                spec_check_response = spec_checker.GPT_spec_check(objects, inside_objects_array, messages)
                spec_accepted = spec_checker.spec_accepted_check(spec_check_response)
                if not spec_accepted:
                    print(color_text("The specification is rejected by the checker. Processing feedback...", 'yellow'))
                    spec_checker_message = {"role": "system", "content": f"Specification checker: {spec_check_response}"}
                    messages.append(spec_checker_message)
                    processing_feedback = True
                spec_checker_iteration += 1

            if pars.manual_spec_check_enabled:
                while True:
                    response = input("Accept the specification? (y/n): ")
                    if response.lower() == 'y':
                        print(color_text("The specification is accepted.", 'yellow'))
                        spec_accepted = True
                        processing_feedback = False
                        break
                    elif response.lower() == 'n':
                        print(color_text("The specification is rejected.", 'yellow'))
                        spec_accepted = False
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")

        except:
            print(color_text("The specification is infeasible.", 'yellow'))
            if pars.syntax_checker_enabled and syntax_checker_iteration < pars.syntax_check_limit:
                T = T + 5
                N = int(T/pars.dt)
                print(color_text(f"The time horizon is increased by 5 seconds. New T_max = {T}. N_max = {N}.", 'yellow'))
                print(color_text("Checking the syntax of the specification...", 'yellow'))
                syntax_checked_spec = translator.gpt_syntax_checker(spec)
                syntax_checker_iteration += 1

    if not pars.dynamicless_check_enabled or spec_accepted:
        print(color_text("Generating the trajectory...", 'yellow'))
        try:
            x,u = solver.generate_trajectory(pars.dt, pars.max_acc, pars.max_speed, verbose=pars.solver_verbose, include_dynamics=True)
            spec_checker = Spec_checker(objects, x, N, pars.dt)
            inside_objects_array = spec_checker.get_inside_objects_array()
            visualizer = Visualizer(x, objects, animate=False)
            fig, ax = visualizer.visualize_trajectory()
            plt.pause(1)
            fig, ax = spec_checker.visualize_spec(inside_objects_array)
            plt.pause(1)
            if pars.spec_checker_enabled and spec_checker_iteration < pars.spec_check_limit:
                spec_check_response = spec_checker.GPT_spec_check(objects, inside_objects_array, messages)
                trajectory_accepted = spec_checker.spec_accepted_check(spec_check_response)
                if not trajectory_accepted:
                    print(color_text("The trajectory is rejected by the checker. Processing feedback...", 'yellow'))
                    spec_checker_message = {"role": "system", "content": f"Specification checker: {spec_check_response}"}
                    messages.append(spec_checker_message)
                    processing_feedback = True
                spec_checker_iteration += 1

            if np.isnan(x).all():
                raise Exception("The trajectory is infeasible.")
        
            if pars.manual_trajectory_check_enabled:
                # Ask the user to accept or reject the trajectory
                while True:
                    response = input("Accept the trajectory? (y/n): ")
                    if response.lower() == 'y':
                        print(color_text("The trajectory is accepted.", 'yellow'))
                        all_x = np.hstack((all_x, x[:,1:]))
                        x0 = x[:, -1]
                        print("Current position: ", x0)
                        processing_feedback = False
                        # reset the flags
                        spec_accepted = False
                        trajectory_accepted = False
                        break  # Exit the loop since the trajectory is accepted
                    elif response.lower() == 'n':
                        print(color_text("The trajectory is rejected.", 'yellow'))
                        break  # Exit the loop since the trajectory is rejected
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")

        except:
            print(color_text("The trajectory is infeasible.", 'yellow'))
            if pars.syntax_checker_enabled and syntax_checker_iteration < pars.syntax_check_limit:
                T = T + 5
                N = int(T/pars.dt)
                print(color_text(f"The time horizon is increased by 5 seconds. New T_max = {T}. N_max = {N}.", 'yellow'))
                print(color_text("Checking the syntax of the specification...", 'yellow'))
                syntax_checked_spec = translator.gpt_syntax_checker(spec)
                syntax_checker_iteration += 1

    previous_messages = messages
    
# Visualize the full trajectory
plt.close('all')
if all_x.shape[1] == 1:
    print(color_text("No trajectories were accepted. Exiting the program.", 'yellow'))
else:
    print(color_text("The full trajectory is generated.", 'yellow'))
    if pars.animate_final_trajectory:
        try:
            waypoints = all_x[:3].T
            N_waypoints = waypoints.shape[0]
            N_extra_points = 5 # extra waypoints to add between waypoints linearly

            # Add extra waypoints
            total_points = N_waypoints + (N_waypoints-1)*N_extra_points
            TARGET_POS = np.zeros((total_points,3))
            TARGET_POS[0] = waypoints[0]
            for i in range(N_waypoints-1):
                TARGET_POS[(1+N_extra_points)*i] = waypoints[i]
                for j in range(N_extra_points+1):
                    k = (j+1)/(N_extra_points+1)
                    TARGET_POS[(1+N_extra_points)*i + j] = (1-k)*waypoints[i] + k*waypoints[i+1]

            INIT_RPYS = np.array([[0, 0, 0]])

            # start simulation when the user presses enter
            input("Press Enter to start the simulation.")

            run(waypoints=TARGET_POS, 
            initial_rpys=INIT_RPYS,    
            objects=objects,
            duration_sec=T-10)

        except:
            print(color_text("Failed to animate the final trajectory.", 'yellow'))
            pass

spec_checker = Spec_checker(objects, all_x, N, pars.dt)
inside_objects_array = spec_checker.get_inside_objects_array()
task_accomplished = spec_checker.task_accomplished_check(inside_objects_array, pars.scenario_name)

# Save the results (optional, user input required)
save_results(pars, messages, task_accomplished)

print(color_text("The program is completed.", 'yellow'))