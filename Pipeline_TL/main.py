from STL_to_path import *
from GPT import *
from NL_to_STL import *
from visualization import *

solver = STLSolver()
T = 10


objects = {"goal1": (4, 6, 4, 6, 4, 6),
           "goal2": (-5, -4, -5, -4, -5, -4),
           "goal3": (-6,-5,4,5,4,5),
           "obstacle": (-1.5, -0.5, -1.5, -0.5, -1.5, -0.5)}
user_input = [{"role": "user", "content": "Go to goal 1, 2 and 3. Always avoid obstacles."}]


translator = NL_to_STL()
spec = translator.extract_STL_formula(user_input, objects, T)

x,u = solver.generate_trajectory(spec)

print("x: ", x)

print("u: ", u)

visualizer = Visualization(x, objects)
visualizer.visualize()