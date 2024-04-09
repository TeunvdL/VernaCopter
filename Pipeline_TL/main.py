from STL_to_path import *
from GPT import *
from NL_to_STL import *
from visualization import *
from logger import *
from scenarios import *
from spec_check import *

max_acc = 50                # maximum acceleration in m/s^2
max_speed = 1               # maximum speed in m/s
T = 25                      # time horizon in seconds 
dt = 0.8                    # time step in seconds
N = int(T/dt)               # total number of time steps

print(logger.color_text(f"dt = {dt}s.", 'yellow'))

scenarios = Scenarios()
scenario = "treasure_hunt" # "reach_avoid", "narrow_maze", "treasure_hunt"
objects = scenarios.get_objects(scenario)
x0 = scenarios.get_starting_state(scenario)

syntax_check_enabled =     False
animate_final_trajectory = False
dynamicless_spec_check =   True
solver_verbose =           False

translator = NL_to_STL(objects, N, dt, print_instructions=True)

previous_messages = []
status = "active"
all_x = np.expand_dims(x0, axis=1)
processing_feedback = False

# Main loop
while status == "active":
    messages, status = translator.gpt_conversation(previous_messages=previous_messages, processing_feedback=processing_feedback, status=status)

    if status == "exited":
        break
    spec = translator.get_specs(messages)
    print("Extracted spec: ", spec)

    solver = STLSolver(spec, objects, x0, T)

    if dynamicless_spec_check:
        spec_accepted = False
        print(logger.color_text("Checking the specification without dynamics...", 'yellow'))
        try:
            no_dynamics_x, no_dynamics_u = solver.generate_trajectory(dt, max_acc, max_speed, verbose=solver_verbose, include_dynamics=False)
            spec_checker = Spec_checker(objects, no_dynamics_x, N, dt)
            inside_objects_array = spec_checker.get_inside_objects_array()
            visualizer = Visualizer(no_dynamics_x, objects, animate=False)
            fig, ax = visualizer.visualize_trajectory()
            plt.pause(1)
            fig, ax = spec_checker.visualize_spec(inside_objects_array)
            plt.pause(1)
            spec_check_response = spec_checker.GPT_spec_check(objects, inside_objects_array)
            spec_accepted = spec_checker.spec_accepted_check(spec_check_response)

            if not spec_accepted:
                print(logger.color_text("The specification is rejected by the checker. Processing feedback...", 'yellow'))
                spec_checker_message = {"role": "system", "content": f"Specification checker: {spec_check_response}"}
                messages.append(spec_checker_message)
                processing_feedback = True

            while True:
                response = input("Accept the specification? (y/n): ")
                if response.lower() == 'y':
                    print(logger.color_text("The specification is accepted.", 'yellow'))
                    spec_accepted = True
                    break
                elif response.lower() == 'n':
                    print(logger.color_text("The specification is rejected.", 'yellow'))
                    spec_accepted = False
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        except:
            print(logger.color_text("The specification is infeasible.", 'yellow'))

    if not dynamicless_spec_check or spec_accepted:
        print(logger.color_text("Generating the trajectory...", 'yellow'))
        try:
            x,u = solver.generate_trajectory(dt, max_acc, max_speed, verbose=solver_verbose, include_dynamics=True)
            spec_checker = Spec_checker(objects, x, N, dt)
            inside_objects_array = spec_checker.get_inside_objects_array()
            GPT_spec_check = spec_checker.GPT_spec_check(objects, inside_objects_array)
            fig, ax = spec_checker.visualize_spec(inside_objects_array)
            plt.pause(1)

            if np.isnan(x).all():
                print(logger.color_text("The trajectory is infeasible.", 'yellow'))
                if syntax_check_enabled:
                    print(logger.color_text("Checking syntax...", 'yellow'))
            
            visualizer = Visualizer(x, objects, animate=False)
            print("x: ", x)
            fig, ax = visualizer.visualize_trajectory()
            visualizer.plot_distance_to_objects()
            plt.pause(1)
        
            # Ask the user to accept or reject the trajectory
            while True:
                response = input("Accept the trajectory? (y/n): ")
                if response.lower() == 'y':
                    print(logger.color_text("The trajectory is accepted.", 'yellow'))
                    all_x = np.hstack((all_x, x[:,1:]))
                    x0 = x[:, -1]
                    print("x0: ", x0)
                    break  # Exit the loop since the trajectory is accepted
                elif response.lower() == 'n':
                    print(logger.color_text("The trajectory is rejected.", 'yellow'))
                    break  # Exit the loop since the trajectory is rejected
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        except Exception as e:
            print(logger.color_text("The trajectory is infeasible. Please try again.", 'yellow'))

    previous_messages = messages
    
# Visualize the full trajectory
plt.close('all')
if all_x.shape[1] == 1:
    print(logger.color_text("No trajectories were accepted. Exiting the program.", 'yellow'))
else:
    print(logger.color_text("The full trajectory is generated.", 'yellow'))
    visualizer = Visualizer(all_x, objects, animate=animate_final_trajectory)
    visualizer.visualize_trajectory()
    visualizer.plot_distance_to_objects()

    if animate_final_trajectory:
       gif_name = input("Enter name of GIF file: ")
       visualizer.animate_trajectory(gif_name + ".gif")

    plt.show()