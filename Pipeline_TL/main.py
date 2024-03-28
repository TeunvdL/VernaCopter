from STL_to_path import *
from GPT import *
from NL_to_STL import *
from visualization import *
from logger import *
from scenarios import *

max_acc = 50                # maximum acceleration in m/s^2
max_speed = 1               # maximum speed in m/s
T = 40                      # time horizon in seconds 
dt = 0.8                    # time step in seconds
N = int(T/dt)               # total number of time steps

print(logger.color_text(f"dt = {dt}s.", 'yellow'))

scenarios = Scenarios()
scenario = "treasure_hunt" # "reach_avoid", "narrow_maze", "treasure_hunt"
objects = scenarios.get_objects(scenario)
x0 = scenarios.get_starting_state(scenario)

syntax_check_enabled = False
animate_final_trajectory = False

translator = NL_to_STL(objects, N, dt, print_instructions=True)

previous_messages = []
status = "active"
all_x = np.expand_dims(x0, axis=1)

# Main loop
while status == "active":
    messages, status = translator.gpt_conversation(previous_messages=previous_messages)
    if status == "exited":
        break
    spec = translator.get_specs(messages)
    
    if syntax_check_enabled:
        spec = translator.gpt_syntax_checker(spec)

    solver = STLSolver(spec, objects, x0, T)
    try:
        x,u = solver.generate_trajectories(dt, max_acc, max_speed, verbose=True)

        if np.isnan(x).all():
            raise Exception("The trajectory is infeasible.")
        
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