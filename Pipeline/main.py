import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation, PillowWriter 
from ChatGPT_move_to import ChatGPT_move_to
from simple_simulation import DroneSimulator
from drone import Drone
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle

def get_target_position_from_chatgpt():
    # Initialize ChatGPT interaction
    chatgpt = ChatGPT_move_to()

    # Initial messages for ChatGPT
    init_messages = [{"role": "system", "content": "You are an assistant guiding a drone. Your goal is to provide the target position to the drone."}, 
                     {"role": "system", "content": "Positions are represented as a tuple <x, y, z>."},
                     {"role": "system", "content": "The starting position is <0, 0, 0>."},
                     {"role": "system", "content": "Only respond with the target position as a tuple <x, y, z>. No other text should be returned."},
                     {"role": "system", "content": "Only use floating point numbers for the position. Do not use any mathematical operators like \"sqrt()\", \"sin()\", etc."},
                     {"role": "system", "content": "Example: User: Move up by 1 in the x-direction. Response: <1.0, 0.0, 0.0>"},
                     {"role": "system", "content": "Example: User: Move to the coordinates (5, 4, 3). Response: <5.0, 4.0, 3.0>"},
                    ]

    # User input to get target position
    user_input = [{"role": "user", "content": "Move the drone to position (5, 5, 5)."},
                  ]

    # Generate target position from user input using ChatGPT
    target = chatgpt.chatcompletion(init_messages, user_input)
    print(f"ChatGPT says: \"{target}\"")

    # Extract target position from LTL (Assuming format: "Move the drone to position (x, y, z).")
    target_position_str = target.split("<")[1].split(">")[0]
    target_position = np.array([float(coord) for coord in target_position_str.split(",")])
    print(f"Target position, extracted: {target_position}")

    return target_position

def main():
    duration = 10  # seconds
    dt = 0.05  # time step
    max_velocity = 5.0
    kp = 1.0
    kd = 0.75
    ki = 0.0

    # Get target position from ChatGPT
    target_position = get_target_position_from_chatgpt()

    # Create DroneSimulator instance
    drone_simulator = DroneSimulator(duration, dt, max_velocity, kp, ki, kd)

    # Simulation with animation
    positions, distances_to_target, velocities = drone_simulator.simulate_drone(target_position, 
                                                                                start_position=np.array([0., 0., 0.]), 
                                                                                start_velocity=np.array([-5., -5., 0.]))
    
    # Animation of the drone 
    drone = Drone(positions[0], velocities[0], col="blue")

    # Plotting the 3D trajectory with animation
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.set_xlabel('X-axis')
    ax1.set_ylabel('Y-axis')
    ax1.set_zlabel('Z-axis')

    min_coord = np.min(positions)
    max_coord = np.max(positions)

    def update(frame):
        ax1.cla()  # Clear the previous frame

        # Adjust plot limits
        ax1.set_xlim(min_coord, max_coord)
        ax1.set_ylim(min_coord, max_coord)
        ax1.set_zlim(min_coord, max_coord)

        rotor_positions = drone.get_rotor_positions(positions[frame], velocities[frame])
        heading_direction = drone.get_heading_direction(positions[frame], velocities[frame])
        
        # Add drone body
        for rotor_position in [rotor_positions[0], rotor_positions[1], rotor_positions[2], rotor_positions[3]]:
            p = Circle((rotor_position[0], rotor_position[1]), drone.rotor_radius, facecolor=drone.col, edgecolor='black')
            ax1.add_patch(p)
            art3d.pathpatch_2d_to_3d(p, z=rotor_position[2], zdir="z")

        # Add vector for heading direction
        ax1.quiver(positions[frame,0], positions[frame,1], positions[frame,2], 
                heading_direction[0], heading_direction[1], heading_direction[2], 
                length=drone.size, normalize=True)
        
        # Add target position
        ax1.scatter(target_position[0], target_position[1], target_position[2], c='green', marker='o', s=50, alpha=0.5)

        # Trace trajectory
        ax1.plot(positions[:frame,0], positions[:frame,1], positions[:frame,2], c='red', linewidth=0.5)

    # Animation
    frames = len(positions[:,0])
    ani = FuncAnimation(fig1, update, frames=frames, interval=dt * 1000, blit=False)

    # Save animation as a GIF
    ani.save('drone_simulation_animation.gif', writer='imagemagick', fps=1/dt)


    # Plotting the distance plot
    fig2, ax2 = plt.subplots()
    ax2.plot(np.arange(0, duration + dt, dt), distances_to_target, label='Distance to Target')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Distance')
    ax2.legend()
    ax2.grid()
    ax2.set_ylim(0, 10)

    plt.show()

if __name__ == "__main__":
    main()