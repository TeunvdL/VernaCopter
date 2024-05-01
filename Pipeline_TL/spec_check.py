import numpy as np
import matplotlib.pyplot as plt
from GPT import GPT
from NL_to_STL import NL_to_STL
from logger import *

class Spec_checker:
    def __init__(self, objects, x, N, dt):
        self.objects = objects
        self.x = x
        self.N = N
        self.dt = dt


    def spec_accepted_check(self, response):
        # check for <accepted> or <rejected> in the response
        if "<accepted>" in response:
            return True
        elif "<rejected>" in response:
            return False
        else:
            return None


    def GPT_spec_check(self, objects, inside_objects_array, previous_messages):
        gpt = GPT()
        translator = NL_to_STL(objects, self.N, self.dt, print_instructions=True)
        messages=previous_messages[1:-1] # all previous messages except the instructions and final message
    
        instructions_template = translator.load_chatgpt_instructions('spec_check_instructions.txt') # load the instructions template
        instructions = translator.insert_instruction_variables(instructions_template) # insert variables into the instructions template
        messages.insert(0, {"role": "system", "content": instructions}) # insert the instructions at the beginning of the messages

        inside_objects_text = self.get_inside_objects_text(inside_objects_array) # get text description of the inside objects array
        messages.append({"role": "system", "content": inside_objects_text}) # append the inside objects text to the messages  

        print("Instruction messages:", messages)
        response = gpt.chatcompletion(messages) # get response from GPT

        messages.append({"role": "assistant", "content": f"{response}"})

        print(logger.color_text("Specification checker:", 'purple'), response)

        return response
    
    def get_inside_objects_text(self, inside_objects_array):
        # For each object, check if the drone is inside the object at all times, outside the object at all times, or both inside and outside the object
        # Outputs a string with a return between each object

        N = inside_objects_array.shape[0]
        T = inside_objects_array.shape[1]
        output = ""
        for i, object in enumerate(self.objects.keys()):
            if np.all(inside_objects_array[i,:] == 1):
                output += f"The drone is always inside the {object}.\n"
            elif np.all(inside_objects_array[i,:] == 0):
                output += f"The drone is never inside the {object}.\n"
            else:
                output += f"The drone is inside the {object} at some point, but not always.\n"
        return output

    def visualize_spec(self, inside_objects_array):
        # Show black and white image of the points inside the objects
        N = inside_objects_array.shape[0]
        T = inside_objects_array.shape[1]
        fig, ax = plt.subplots(figsize=(10,6))
        ax.imshow(inside_objects_array, aspect='auto', cmap='gray')
        ax.set_xlabel('Time Steps')
        # set yticks to object names
        ax.set_yticks(range(N))
        ax.set_yticklabels(self.objects.keys())
        # show color bar
        cbar = ax.figure.colorbar(ax.imshow(inside_objects_array, aspect='auto', cmap='gray'))
        cbar.set_label('Inside Object')
        #show lines between the objects
        for i in range(N-1):
            ax.axhline(i+0.5, color='gray', linewidth=0.5)
        # show vertical lines for every 5 time steps
        for i in range(0,T,5):
            ax.axvline(i, color='gray', linewidth=0.5)

        return fig, ax
    
    def task_accomplished_check(self, inside_objects_array, scenario_name):
        objects_inside = {}
        for i, object in enumerate(self.objects.keys()):
            objects_inside[object] = inside_objects_array[i,:]
        objects_inside

        if scenario_name == "reach_avoid":
            pass
        elif scenario_name == "narrow_maze":
            pass
        elif scenario_name == "treasure_hunt":
            # test if chest is reached
            chest_reached = 1 in objects_inside['chest']
            
            # test if all the walls are avoided
            walls_avoided = True
            for object in self.objects.keys():
                if 'wall' in object:
                    wall_crossed = 1 in objects_inside[object]
                    if wall_crossed: walls_avoided = False

            # test if the door is crossed before the key is reached
            key_time = np.where(objects_inside['door_key'] == 1)[0]
            if key_time.size != 0:
                key_crossed = True
                key_time = key_time[0]
            else: 
                key_crossed = False

            door_time = np.where(objects_inside['door'] == 1)[0]
            if door_time.size != 0:
                door_crossed = True
                door_time = door_time[0]
            else:
                door_crossed = False

            door_before_key = door_crossed and key_crossed and door_time < key_time

            task_accomplished = False
            if chest_reached and walls_avoided and not door_before_key:
                print(logger.color_text("Task accomplished:", 'green'), "All conditions are met.")
                task_accomplished = True
            elif not chest_reached:
                print(logger.color_text("Task failed:", 'red'), "The chest was not reached.")
            elif not walls_avoided:
                print(logger.color_text("Task failed:", 'red'), "A wall was crossed.")
            elif door_before_key:
                print(logger.color_text("Task failed:", 'red'), "The door was crossed before the key was reached.")
            else:
                print(logger.color_text("Task failed:", 'red'), "Unknown failure.")

            return task_accomplished

    def get_inside_objects_array(self):
        T = self.x.shape[1]
        N = len(self.objects)
        inside_array = np.zeros((N,T))
        for i, object in enumerate(self.objects.values()):
            for j in range(T):
                inside_array[i,j] = self.is_inside(self.x[:3,j], object)

        return inside_array

    def is_inside(self, point, object):
        x, y, z = point[:3]
        xmin, xmax, ymin, ymax, zmin, zmax = object
        inside_boolean = x >= xmin and x <= xmax and y >= ymin and y <= ymax and z >= zmin and z <= zmax
        return inside_boolean*1