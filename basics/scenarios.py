import numpy as np
from PIL import Image

class Scenarios:
    def __init__(self, scenario_name):
        self.scenario_name = scenario_name
        self.objects = self.get_objects()
        self.x0 = self.get_starting_state()
        self.T_initial = self.get_time_horizon()
        self.automated_user_input = self.get_automated_user_input()

    def get_starting_state(self):
        if self.scenario_name == "reach_avoid":
            x0 = np.array([-3.5,-3.5,0.5,0.,0.,0.])
        elif self.scenario_name == "narrow_maze":
            x0 = np.array([4.25,-4.25,0.5,0.,0.,0.])
        elif self.scenario_name == "treasure_hunt":
            x0 = np.array([3.,-4.,0.5,0.,0.,0.])
        return x0
    
    def get_objects(self):
        if self.scenario_name == "reach_avoid":
            objects = {"goal": (4., 5., 4., 5., 4., 5.),
                       "obstacle1": (-3., -1., -0.5, 1.5, 0.5, 2.5),
                       "obstacle2": (-4.5, -3., 0., 2.25, 0.5, 2.),
                       "obstacle3": (-2., -1., 4., 5., 3.5, 4.5),
                       "obstacle4": (3., 4., -3.5, -2.5, 1., 2.),
                       "obstacle5": (4., 5., 0., 1., 2., 3.5),
                       "obstacle6": (2., 3.5, 1.5, 2.5, 3.75, 5.),
                       "obstacle7": (-2., -1., -2., -1., 1., 2.),
                       }

        elif self.scenario_name == "narrow_maze":
            objects = {"goal1": (-0.25, 0.75, -0.25, 0.75, 1., 2.),
                       "goal2": (-2.75, -1.75, 1.75, 2.75, 1., 2.),
                       "goal3": (1.75, 2.75, 1.75, 2.75, 1., 2.),
                       "goal4": (3.75, 4.75, 1.75, 2.75, 1., 2.),
                       "room_bounds": (-5., 5., -5., 5., 0., 3.),
                       "SE_vertical_wall": (3., 3.5, -5., -0.5, 0., 3.),
                       "E_mid_vertical_wall": (1., 1.5, -3., 1., 0., 3.),
                       "SW_horizontal_wall": (-3.5, 1.5, -3.5, 3., 0., 3.),
                       "W_mid_vertical_wall": (-1., -0.5, -3., 1., 0., 3.),
                       "W_horizontal_wall": (-5., -2.5, -1.5, -1., 0., 3.),
                       "mid_horizontal_wall": (-3., 3., 1., 1.5, 0., 3.),
                       "NW_vertical_wall": (-3.5, -3., 1., 3.5, 0., 3.),
                       "NW_horizontal_wall": (-3., -1., 3., 3.5, 0., 3.),
                       "NW_mid_vertical_wall": (-1.5, -1., 1.5, 3., 0., 3.),
                       "N_vertical_wall": (0.5, 1., 3.5, 5., 0., 3.),
                       "NNE_horizontal_wall": (0.5, 3., 3., 3.5, 0., 3.),
                       "ENE_horizontal_wall": (3.5, 5., 1., 1.5, 0., 3.),
                       "NE_vertical_wall": (3., 3.5, 1., 3.5, 0., 3.),
                       }

        elif self.scenario_name == "treasure_hunt":
            objects = {"door_key" : (3.75, 4.75, 3.75, 4.75, 1., 2.),
                       "chest": (-4.25, -3, -4.5, -3.75, 0., 0.75),
                       "door": (0., 0.5, -2.5, -1, 0., 2.5),
                       "region_bounds": (-5., 5., -5., 5., 0., 3.),
                       "NE_inside_wall": (2., 5., 3., 3.5, 0., 3.),
                       "south_mid_inside_wall": (0., 0.5, -5., -2.5, 0., 3.),
                       "north_mid_inside_wall": (0., 0.5, -1., 5., 0., 3.),
                       "west_inside_wall": (-2.25, -1.75, -5., 3.5, 0., 3.),
                       "above_door_wall": (0., 0.5, -2.5, -1, 2.5, 3.),
                       }

        return objects
    
    def show_map(self):
        # show png of scenario
        path = 'Pipeline_TL/scenario_images/'
        if self.scenario_name == "reach_avoid":
            path += "reach_avoid.png"
        elif self.scenario_name == "narrow_maze":
            path += "narrow_maze.png"
        elif self.scenario_name == "treasure_hunt":
            path += "treasure_hunt.png"
        img = Image.open(path)
        img.show()

    def get_time_horizon(self):
        if self.scenario_name == "reach_avoid":
            T = 25
        elif self.scenario_name == "narrow_maze":
            T = 50
        elif self.scenario_name == "treasure_hunt":
            T = 70
        return T
    
    def get_automated_user_input(self):
        if self.scenario_name == "reach_avoid":
            automated_user_input = "Reach the goal while avoiding all obstacles."
        elif self.scenario_name == "narrow_maze":
            automated_user_input = "Navigate through the maze to reach the goal."
        elif self.scenario_name == "treasure_hunt":
            automated_user_input = "Go to the key in the first 30 seconds, then go to the chest. Avoid all walls and stay in the room at all times."
        return automated_user_input