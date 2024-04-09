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


    def GPT_spec_check(self, objects, inside_objects_array):
        gpt = GPT()
        translator = NL_to_STL(objects, self.N, self.dt, print_instructions=True)
        inside_objects_text = self.get_inside_objects_text(inside_objects_array)
        messages = []
        instructions_template = translator.load_chatgpt_instructions('spec_check_instructions.txt')
        instructions = translator.insert_instruction_variables(instructions_template)
        messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": inside_objects_text})
        #print("messages", messages)
        response = gpt.chatcompletion(messages)
        messages.append({"role": "assistant", "content": f"Specification checker: {response}"})
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
                output += f"The drone is inside the {object} at all times.\n"
            elif np.all(inside_objects_array[i,:] == 0):
                output += f"The drone is outside the {object} at all times.\n"
            else:
                output += f"The drone passes through the {object} at some point during the time window, but not at all times.\n"
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