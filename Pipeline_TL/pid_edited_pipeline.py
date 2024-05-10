"""Script demonstrating the joint use of simulation and control.

The simulation is run by a `CtrlAviary` environment.
The control is given by the PID implementation in `DSLPIDControl`.

Example
-------
In a terminal, run as:

    $ python pid_edited.py

Notes
-----
The drones move, at different altitudes, along cicular trajectories 
in the X-Y plane, around point (0, -.3).
"""

import os
import time
import argparse
from datetime import datetime
import pdb
import math
import random
import numpy as np
import pybullet as p
import pybullet_data
import matplotlib.pyplot as plt

from gym_pybullet_drones.utils.enums import DroneModel, Physics
from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync, str2bool

DEFAULT_DRONES = DroneModel("cf2p")
DEFAULT_NUM_DRONES = 1
DEFAULT_PHYSICS = Physics("pyb")
DEFAULT_GUI = True
DEFAULT_RECORD_VISION = False
DEFAULT_PLOT = False
DEFAULT_USER_DEBUG_GUI = False
DEFAULT_OBSTACLES = False
DEFAULT_SIMULATION_FREQ_HZ = 240
DEFAULT_CONTROL_FREQ_HZ = 48
DEFAULT_DURATION_SEC = 120
DEFAULT_OUTPUT_FOLDER = 'results'
DEFAULT_COLAB = False

def create_cube(pybullet_client, bounds, color, alpha=1.0):
    """
    This function creates a cube object in the PyBullet scene with specified properties.

    Args:
        pybullet_client: The PyBullet client object used for interacting with the simulation.
        position: A list of three numbers specifying the center position of the cube (x, y, z).
        size: A list of three numbers specifying the half extents of the cube (width/2, height/2, depth/2).
        color: A list of three numbers specifying the RGB color of the cube (red, green, blue). Values should be between 0 and 1.
        alpha: The opacity of the cube (0.0 for transparent, 1.0 for opaque).

    Returns:
        The ID of the created cube object in the simulation.
    """

    # Transform x_min, x_max, y_min, y_max, z_min, z_max into half extents
    x_min, x_max, y_min, y_max, z_min, z_max = bounds
    position = [(x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2]
    size = [(x_max - x_min) / 2, (y_max - y_min) / 2, (z_max - z_min) / 2]

    # Create the visual shape
    visualShapeId = pybullet_client.createVisualShape(
        shapeType=pybullet_client.GEOM_BOX,
        halfExtents=size,
        rgbaColor=color + [alpha]  # Append alpha to color list
    )

    # # Create the collision shape (optional)
    # collisionShapeId = pybullet_client.createCollisionShape(
    #     shapeType=pybullet_client.GEOM_BOX,
    #     halfExtents=size
    # )

    # Create the multi-body for the cube with mass and fixed base (optional)
    cubeId = pybullet_client.createMultiBody(
        baseMass=0,
        # baseCollisionShapeIndex=collisionShapeId,
        baseVisualShapeIndex=visualShapeId,
        basePosition=position,
    )

    return cubeId


def run(waypoints,          # waypoints to follow, shape (N, 3)
        initial_rpys=None,  # initial rpy of drones, shape (num_drones, 3)
        objects=None,       # dictionary of objects in the scene
        drone=DEFAULT_DRONES,
        num_drones=DEFAULT_NUM_DRONES,
        physics=DEFAULT_PHYSICS,
        gui=DEFAULT_GUI,
        record_video=DEFAULT_RECORD_VISION,
        plot=DEFAULT_PLOT,
        user_debug_gui=DEFAULT_USER_DEBUG_GUI,
        obstacles=DEFAULT_OBSTACLES,
        simulation_freq_hz=DEFAULT_SIMULATION_FREQ_HZ,
        control_freq_hz=DEFAULT_CONTROL_FREQ_HZ,
        duration_sec=DEFAULT_DURATION_SEC,
        output_folder=DEFAULT_OUTPUT_FOLDER,
        colab=DEFAULT_COLAB
        ):
    
    ### Initialize the simulation #############################
    INIT_XYZS = waypoints[0,:].reshape(1,3)
    INIT_RPYS = initial_rpys
    
    NUM_WP = waypoints.shape[0]
    wp_counters = np.array([0 for i in range(num_drones)])

    #### Create the environment ################################
    env = CtrlAviary(drone_model=drone,
                        num_drones=num_drones,
                        initial_xyzs=INIT_XYZS,
                        initial_rpys=INIT_RPYS,
                        physics=physics,
                        neighbourhood_radius=10,
                        pyb_freq=simulation_freq_hz,
                        ctrl_freq=control_freq_hz,
                        gui=gui,
                        record=record_video,
                        obstacles=obstacles,
                        user_debug_gui=user_debug_gui
                        )
    
    #### Add animation of the target trajectory ################
    # videopath = "Video/"
    # os.makedirs(videopath, exist_ok=True)
    # p.configureDebugVisualizer(p.COV_ENABLE_GUI,0) # remove GUI layout from screen
    # p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, videopath+"test.mp4")

    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()

    #### Set the camera at a fixed position ####################
    ### Set camera view
    p.resetDebugVisualizerCamera(cameraDistance=7.5, cameraYaw=15, cameraPitch=-50, cameraTargetPosition=[0,-2,1.5])

    #### Initialize the logger #################################
    logger = Logger(logging_freq_hz=control_freq_hz,
                    num_drones=num_drones,
                    output_folder=output_folder,
                    colab=colab
                    )

    #### Initialize the controllers ############################
    if drone in [DroneModel.CF2X, DroneModel.CF2P]:
        ctrl = [DSLPIDControl(drone_model=drone) for i in range(num_drones)]

    #### Customize the envionment ##############################
    cube_color = [0.8, 0.2, 0.3]        # Set the desired RGB color for the cube (red, green, blue)
    cube_alpha = 0.4                    # Set the transparency of the cube (0.0 for fully transparent, 1.0 for opaque)
    for key in objects.keys():
        cube_bounds = objects[key]
        cubeId = create_cube(p, cube_bounds, cube_color, cube_alpha)

    #### Run the simulation ####################################
    action = np.zeros((num_drones,4))
    START = time.time()
    for i in range(0, int(duration_sec*env.CTRL_FREQ)):

        #### Step the simulation ###################################
        obs, reward, terminated, truncated, info = env.step(action)

        #### Compute control for the current way point #############
        for j in range(num_drones):
            action[j, :], _, _ = ctrl[j].computeControlFromState(control_timestep=env.CTRL_TIMESTEP,
                                                                    state=obs[j],
                                                                    # target_pos=INIT_XYZS[j, :] + waypoints[wp_counters[j], :],
                                                                    target_pos=waypoints[wp_counters[j], :],
                                                                    target_rpy=INIT_RPYS[j, :]
                                                                    )
            #print("j: ", j, "wp_counters[j]: ", wp_counters[j], "target_pos=waypoints[wp_counters[j], :]: ", waypoints[wp_counters[j], :])

        #### Go to the next way point and loop #####################
        for j in range(num_drones):
            wp_counters[j] = wp_counters[j] + 1 if wp_counters[j] < (NUM_WP-2) else wp_counters[j]

        #### Log the simulation ####################################
        for j in range(num_drones):
            logger.log(drone=j,
                       timestamp=i/env.CTRL_FREQ,
                       state=obs[j],
                       control=np.hstack([waypoints[wp_counters[j], 0:2], INIT_XYZS[j, 2], INIT_RPYS[j, :], np.zeros(6)])
                       # control=np.hstack([INIT_XYZS[j, :]+waypoints[wp_counters[j], :], INIT_RPYS[j, :], np.zeros(6)])
                       )

        #### Printout ##############################################
        env.render()

        #### Sync the simulation ###################################
        if gui:
            sync(i, START, env.CTRL_TIMESTEP)

    #### Close the environment #################################
    env.close()

    #### Save the simulation results ###########################
    # logger.save()
    # logger.save_as_csv("pid") # Optional CSV save

    #### Plot the simulation results ###########################
    if plot:
        logger.plot()

if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Helix flight script using CtrlAviary and DSLPIDControl')
    parser.add_argument('--drone',              default=DEFAULT_DRONES,     type=DroneModel,    help='Drone model (default: CF2X)', metavar='', choices=DroneModel)
    parser.add_argument('--num_drones',         default=DEFAULT_NUM_DRONES,          type=int,           help='Number of drones (default: 3)', metavar='')
    parser.add_argument('--physics',            default=DEFAULT_PHYSICS,      type=Physics,       help='Physics updates (default: PYB)', metavar='', choices=Physics)
    parser.add_argument('--gui',                default=DEFAULT_GUI,       type=str2bool,      help='Whether to use PyBullet GUI (default: True)', metavar='')
    parser.add_argument('--record_video',       default=DEFAULT_RECORD_VISION,      type=str2bool,      help='Whether to record a video (default: False)', metavar='')
    parser.add_argument('--plot',               default=DEFAULT_PLOT,       type=str2bool,      help='Whether to plot the simulation results (default: True)', metavar='')
    parser.add_argument('--user_debug_gui',     default=DEFAULT_USER_DEBUG_GUI,      type=str2bool,      help='Whether to add debug lines and parameters to the GUI (default: False)', metavar='')
    parser.add_argument('--obstacles',          default=DEFAULT_OBSTACLES,       type=str2bool,      help='Whether to add obstacles to the environment (default: True)', metavar='')
    parser.add_argument('--simulation_freq_hz', default=DEFAULT_SIMULATION_FREQ_HZ,        type=int,           help='Simulation frequency in Hz (default: 240)', metavar='')
    parser.add_argument('--control_freq_hz',    default=DEFAULT_CONTROL_FREQ_HZ,         type=int,           help='Control frequency in Hz (default: 48)', metavar='')
    parser.add_argument('--duration_sec',       default=DEFAULT_DURATION_SEC,         type=int,           help='Duration of the simulation in seconds (default: 5)', metavar='')
    parser.add_argument('--output_folder',      default=DEFAULT_OUTPUT_FOLDER, type=str,           help='Folder where to save logs (default: "results")', metavar='')
    parser.add_argument('--colab',              default=DEFAULT_COLAB, type=bool,           help='Whether example is being run by a notebook (default: "False")', metavar='')
    ARGS = parser.parse_args()

    run(**vars(ARGS))
