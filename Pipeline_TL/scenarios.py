import numpy as np

class Scenarios:
    def get_starting_state(self, scenario_name):
        if scenario_name == "reach_avoid":
            x0 = np.array([-3.5,-3.5,0.5,0.,0.,0.])
        elif scenario_name == "narrow_maze":
            x0 = np.array([4.25,-4.25,0.5,0.,0.,0.])
        elif scenario_name == "treasure_hunt":
            x0 = np.array([3.,-4.,0.5,0.,0.,0.])
        return x0
    
    def get_objects(self, scenario_name):
        if scenario_name == "reach_avoid":
            objects = {"goal": (4., 5., 4., 5., 4., 5.),
                       "obstacle1": (-3., -1., 1.5, -0.5, 0.5, 2.5),
                       "obstacle2": (-4.5, -3., 0., 2.25, 0.5, 2.),
                       "obstacle3": (-2., -1., 4., 5., 3.5, 4.5),
                       "obstacle4": (3., 4., -3.5, -2.5, 1., 2.),
                       "obstacle5": (4., 5., 0., 1., 2., 3.5),
                       "obstacle6": (2., 3.5, 1.5, 2.5, 3.75, 5.),
                       }

        elif scenario_name == "narrow_maze":
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

        elif scenario_name == "treasure_hunt":
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