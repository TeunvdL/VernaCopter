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


def run(waypoints,              # waypoints to follow, shape (N, 3)
        initial_rpys=None,      # initial rpy of drones, shape (num_drones, 3)
        scenario=None,          # scenario object to run    
        save_animation=False,   # whether to save the animation
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
        output_folder=DEFAULT_OUTPUT_FOLDER,
        colab=DEFAULT_COLAB
        ):
    
    ### Initialize the simulation #############################
    INIT_XYZS = waypoints[0,:].reshape(1,3)
    INIT_RPYS = initial_rpys
    
    NUM_WP = waypoints.shape[0]
    wp_counters = np.array([0 for i in range(num_drones)])

    if scenario.scenario_name == "reach_avoid":
        duration_sec = 15
    elif scenario.scenario_name == "treasure_hunt":
        duration_sec = 20
    else:
        duration_sec = DEFAULT_DURATION_SEC

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
    
    p.changeVisualShape(env.PLANE_ID, -1, rgbaColor=[0, 0, 0, 0])
    
    #### Add animation of the target trajectory ################
    if save_animation:
        videopath = "visuals/simulation/video/"
        os.makedirs(videopath, exist_ok=True)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI,0) # remove GUI layout from screen
        p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, videopath+f"{scenario.scenario_name}_trajectory.mp4")

    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()

    #### Set the camera at a fixed position ####################
    ### Set camera view
    if scenario.scenario_name == "reach_avoid":
        p.resetDebugVisualizerCamera(cameraDistance=9, cameraYaw=0, cameraPitch=-40, cameraTargetPosition=[0,0,1.5])
    elif scenario.scenario_name == "treasure_hunt":
        p.resetDebugVisualizerCamera(cameraDistance=7, cameraYaw=15, cameraPitch=-65, cameraTargetPosition=[0,-2,1.5])

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
    for object in scenario.objects:
        if scenario.scenario_name == "reach_avoid": 
            if 'obstacle' in object: # check if object name contains 'obstacle'
                cube_color = [1., 0., 0.]
                cube_alpha = 0.2
            elif 'goal' in object: # check if object name contains 'goal'
                cube_color = [0.1568627450980392, 0.8431372549019608, 0.47058823529411764]
                cube_alpha = 0.2

            cube_bounds = scenario.objects[object]
            create_cube(p, cube_bounds, cube_color, cube_alpha)

        elif scenario.scenario_name == "treasure_hunt":
            if 'wall' in object:
                cube_color = [0.9, 0.9, 0.9]
                cube_alpha = 0.3
            elif object == 'door_key':
                cube_color = [0.1568627450980392, 0.8431372549019608, 0.47058823529411764]
                cube_alpha = 0.9
                cube_bounds = scenario.objects[object]
                key_id = create_cube(p, cube_bounds, cube_color, cube_alpha)
            elif object == 'chest':
                cube_color = [1.,0.8431372549019608, 0.]
                cube_alpha = 0.9
            elif object == 'door':
                cube_color = [0.28627450980392155, 0.47843137254901963, 0.8235294117647058]
                cube_alpha = 0.9
                cube_bounds = scenario.objects[object]
                door_id = create_cube(p, cube_bounds, cube_color, cube_alpha)

            if object != "room_bounds" and object != "door" and object != "door_key":
                cube_bounds = scenario.objects[object]
                create_cube(p, cube_bounds, cube_color, cube_alpha)

            # make separate floor
            wall_thickness = 0.3
            floor_color = [0.4392156862745098, 0.2235294117647059, 0.15294117647058825]
            
            floor_bounds = (-5 - wall_thickness, 5 + wall_thickness, -5 - wall_thickness, 5 + wall_thickness, -0.5, 0)
            floor_alpha = 1.0
            floor_id = create_cube(p, floor_bounds, floor_color, floor_alpha)
            #p.changeVisualShape(floor_id, -1, textureUniqueId=p.loadTexture('WoodPallet.png'))

            # make saparate walls
            wall_alpha = 1.0
            wall_color = [0.9, 0.9, 0.9]

            west_wall_bounds = (-5 - wall_thickness, -5, -5 - wall_thickness, 5 + wall_thickness, 0, 3)
            create_cube(p, west_wall_bounds, wall_color, wall_alpha)

            east_wall_bounds = (5, 5 + wall_thickness, -5 - wall_thickness, 5 + wall_thickness, 0, 3)
            create_cube(p, east_wall_bounds, wall_color, wall_alpha)

            north_wall_bounds = (-5, 5, 5, 5 + wall_thickness, 0, 3)
            create_cube(p, north_wall_bounds, wall_color, wall_alpha)

            south_wall_bounds = (-5, 5, -5 - wall_thickness, -5, 0, 3)
            create_cube(p, south_wall_bounds, wall_color, wall_alpha)

    #### Run the simulation ####################################
    action = np.zeros((num_drones,4))
    START = time.time()
    last_pos = INIT_XYZS[0]
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
            wp_counters[j] = wp_counters[j] + 1 if wp_counters[j] < (NUM_WP-2) else wp_counters[j]

            #### Plot the trace #######################################
            cur_pos = obs[j][:3]
            p.addUserDebugLine(lineFromXYZ=last_pos, lineToXYZ=cur_pos, lineColorRGB=[1, 0, 0], lineWidth=4.0)
            
            if scenario.scenario_name == "treasure_hunt":
                #### remove door when key is reached #####################
                key_bounds = scenario.objects["door_key"]
                # check if drone is in the key bounds
                tolerance = 0.1
                key_reached = cur_pos[0] > key_bounds[0] - tolerance and cur_pos[0] < key_bounds[1] + tolerance and cur_pos[1] > key_bounds[2] - tolerance and cur_pos[1] < key_bounds[3] + tolerance and cur_pos[2] > key_bounds[4] - tolerance and cur_pos[2] < key_bounds[5] + tolerance
                if key_reached:
                    # remove door
                    p.removeBody(key_id)
                    p.removeBody(door_id)
                    
            last_pos = cur_pos

            #### Log the simulation ####################################
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
    parser.add_argument('--output_folder',      default=DEFAULT_OUTPUT_FOLDER, type=str,           help='Folder where to save logs (default: "results")', metavar='')
    parser.add_argument('--colab',              default=DEFAULT_COLAB, type=bool,           help='Whether example is being run by a notebook (default: "False")', metavar='')
    ARGS = parser.parse_args()

    run(**vars(ARGS))
