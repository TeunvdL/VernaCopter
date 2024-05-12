from basics.logger import color_text
import numpy as np
from .pid_edited_pipeline import run

def simulate(pars, objects, all_x, T):
    """
    Generate waypoints for the final trajectory animation.
    """
    if pars.animate_final_trajectory:
            try:
                waypoints = all_x[:3].T
                N_waypoints = waypoints.shape[0]
                N_extra_points = 5 # extra waypoints to add between waypoints linearly

                # Add extra waypoints
                total_points = N_waypoints + (N_waypoints-1)*N_extra_points
                TARGET_POS = np.zeros((total_points,3))
                TARGET_POS[0] = waypoints[0]
                for i in range(N_waypoints-1):
                    TARGET_POS[(1+N_extra_points)*i] = waypoints[i]
                    for j in range(N_extra_points+1):
                        k = (j+1)/(N_extra_points+1)
                        TARGET_POS[(1+N_extra_points)*i + j] = (1-k)*waypoints[i] + k*waypoints[i+1]

                INIT_RPYS = np.array([[0, 0, 0]])

                # start simulation when the user presses enter
                input("Press Enter to start the simulation.")

                run(waypoints=TARGET_POS, 
                initial_rpys=INIT_RPYS,    
                objects=objects,
                duration_sec=T-10)

            except:
                print(color_text("Failed to animate the final trajectory.", 'yellow'))
                pass