from STL_to_path import *
from GPT import *
from NL_to_STL import *
from visualization import *

T_max = 20          # time horizon in seconds 
dt = 0.5            # time step in seconds
N = int(T_max/dt)   # number of time steps
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

x0 = np.array([0.,0.,0.,0.,0.,0.]) # initial state: x, y, z, vx, vy, vz

translator = NL_to_STL(objects, T_max, dt, print_instructions=True)
specs = translator.generate_specs()
print("specs: ", specs)

solver = STLSolver(specs, objects, x0, T_max)

x,u = solver.generate_trajectories(dt, max_acc, max_speed, verbose=True)

print("x: ", x)

print("u: ", u)

animate = False
visualizer = Visualizer(x, objects, animate=animate)

if animate:
    gif_name = input("Enter name of GIF file: ")
    visualizer.animate_trajectory(gif_name + ".gif")

visualizer.visualize_trajectory()
visualizer.plot_distance_to_objects()
plt.show()