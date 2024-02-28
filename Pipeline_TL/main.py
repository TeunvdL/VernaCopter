from STL_to_path import *
from GPT import *
from NL_to_STL import *
from visualization import *

T = 20              # time horizon in seconds 
dt = 0.5            # time step in seconds
N = int(T/dt)       # number of time steps
max_acc = 50        # maximum acceleration in m/s^2
max_speed = 1       # maximum speed in m/s

objects = {"key" : (3.75, 4.75, 3.75, 4.75, 1., 2.),
           "chest": (-4.25, -3, -4.5, -3.75, 0., 0.75),
           "door": (0., 0.5, -2.5, -1, 0., 2.5),
           "bounds": (-5., 5., -5., 5., 0., 3.),
           "NE_inside_wall": (2., 5., 3., 3.5, 0., 3.),
           "south_mid_inside_wall": (0., 0.5, -5., -2.5, 0., 3.),
           "north_mid_inside_wall": (0., 0.5, -1., 5., 0., 3.),
           "west_inside_wall": (-2.25, -1.75, -5., 3.5, 0., 3.),
           "above_door_wall": (0., 0.5, -2.5, -1, 2.5, 3.),
           }

x0 = np.array([3.,-4.,0.5,0.,0.,0.]) # initial state: x, y, z, vx, vy, vz
animate_final_trajectory = False

translator = NL_to_STL(objects, N, dt, print_instructions=True)

previous_messages = []
status = "active"
#all_x = x0

while status == "active":
    messages, status = translator.gpt_conversation(previous_messages=previous_messages)
    if status == "exited":
        break
    spec = translator.get_specs(messages)
    solver = STLSolver(spec, objects, x0, T)
    try:
        x,u = solver.generate_trajectories(dt, max_acc, max_speed, verbose=True)
        print("x: ", x)
        print("u: ", u)
        #all_x = np.hstack((all_x, x))

        visualizer = Visualizer(x, objects, animate=False)
        fig, ax = visualizer.visualize_trajectory()
        visualizer.plot_distance_to_objects()
        
        plt.pause(1)
        
        while True:
            response = input("Accept the trajectory? (y/n): ")
            if response.lower() == 'y':
                print("The trajectory is accepted.")
                x0 = x[:, -1]
                print("x0: ", x0)
                break  # Exit the loop since the trajectory is accepted
            elif response.lower() == 'n':
                print("The trajectory is rejected.")
                break  # Exit the loop since the trajectory is rejected
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    except Exception as e:
        print(e)
        print("The trajectory is infeasible. Please try again.")
        continue

    previous_messages = messages
    


#visualizer = Visualizer(all_x, objects, animate=animate_final_trajectory)
#visualizer.visualize_trajectory()
#visualizer.plot_distance_to_objects()

#if animate_final_trajectory:
#    gif_name = input("Enter name of GIF file: ")
#    visualizer.animate_trajectory(gif_name + ".gif")

#plt.show()