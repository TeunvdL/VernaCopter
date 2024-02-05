from STL_to_path import *
from GPT import *
from NL_to_STL import *
from visualization import *

max_T = 10          # time horizon in seconds 
max_acc = 10        # maximum acceleration in m/s^2

objects = {"goal1": (4, 6, 4, 6, 4, 6),
           "goal2": (-5, -4, -5, -4, -5, -4),
           "goal3": (-6, -5, 4, 5, 4, 5),
           "obstacle1": (-1.5, -0.5, -1.5, -0.5, -1.5, -0.5),
           "obstacle2": (1.0, 2.0, 1.0, 2.0, 1.5, 2.5),
           "obstacle3": (1.0, 2.0, 0.0, 1.0, -1.0, 1.0),}

x0 = np.array([0.,0.,0.,0.,0.,0.]) # initial state: x, y, z, vx, vy, vz

user_input = [{"role": "user", "content": "Go to goal 1, 2 and 3. Avoid all obstacles."}]


translator = NL_to_STL()
spec = translator.extract_STL_formula(user_input, objects, max_T)

solver = STLSolver(spec, x0, max_T)

x,u = solver.generate_trajectory(max_acc, verbose=True)

print("x: ", x)

print("u: ", u)

animate = False
visualizer = Visualization(x, objects, animate=animate)

if animate:
    gif_name = input("Enter name of GIF file: ")
    visualizer.animate_trajectory(gif_name + ".gif")

visualizer.visualize()
visualizer.plot_distance_to_objects()

plt.show()