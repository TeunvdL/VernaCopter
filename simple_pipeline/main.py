import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from ChatGPT_move_to import ChatGPT_move_to
from simple_simulation import DroneSimulator

def get_target_position_from_chatgpt():
    # Initialize ChatGPT interaction
    chatgpt = ChatGPT_move_to()

    # Initial messages for ChatGPT
    init_messages = [{"role": "system", "content": "You are an assistant guiding a drone. Your goal is to provide the target position to the drone."}, 
                    {"role": "system", "content": "Please only respond with the target position as a tuple (x, y, z)."},
                    {"role": "system", "content": "Example: (1.5, 1.5, 1.5)"},
                    {"role": "system", "content": "The starting position is (0, 0, 0)."},
                    ]

    # User input to get target position
    user_input = [{"role": "user", "content": "Move the drone diagonally in the +x, +z-direction. The total displacement of the drone should be 5 units."},
                  ]

    # Generate target position from user input using ChatGPT
    target = chatgpt.chatcompletion(init_messages, user_input)
    print(target)

    # Extract target position from LTL (Assuming format: "Move the drone to position (x, y, z).")
    target_position_str = target.split("(")[1].split(")")[0]
    target_position = np.array([float(coord) for coord in target_position_str.split(",")])
    print(f"Target position: {target_position}")

    return target_position

def main():
    duration = 10  # seconds
    dt = 0.05  # time step
    max_velocity = 5.0
    kp = 1.0
    ki = 0.0
    kd = 0.5

    # Get target position from ChatGPT
    target_position = get_target_position_from_chatgpt()

    # Create DroneSimulator instance
    drone_simulator = DroneSimulator(duration, dt, max_velocity, kp, ki, kd)

    # Simulation
    x_traj, y_traj, z_traj, distances_to_target = drone_simulator.simulate_drone_with_pid_controller(target_position)

    # Plotting the 3D trajectory
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')
    target, = ax1.plot([target_position[0]], [target_position[1]], [target_position[2]], 'go', label='Target Position')

    # Initialize markers and lines for the drone representation
    marker, = ax1.plot([], [], [], 'ro', label='Drone Marker')
    heading_line, = ax1.plot([], [], [], 'r-', label='Heading Direction')

    ax1.set_xlabel('X-axis')
    ax1.set_ylabel('Y-axis')
    ax1.set_zlabel('Z-axis')
    ax1.legend()

    def update(frame):
        # Update marker representing the current position of the drone
        marker.set_data([x_traj[frame]], [y_traj[frame]])
        marker.set_3d_properties(z_traj[frame])

        # Update heading direction based on the velocity
        if frame < len(x_traj) - 1:
            delta_position = np.array([x_traj[frame + 1] - x_traj[frame], 
                                    y_traj[frame + 1] - y_traj[frame], 
                                    z_traj[frame + 1] - z_traj[frame]])
            heading_direction = delta_position / np.linalg.norm(delta_position)
        else:
            heading_direction = np.array([1.0, 0.0, 0.0])  # Default direction if at the last frame

        # Scale the heading direction for visualization
        heading_length = 0.3
        heading_vector = heading_length * heading_direction

        # Update line representing the heading direction
        heading_line.set_data([x_traj[frame], x_traj[frame] + heading_vector[0]],
                            [y_traj[frame], y_traj[frame] + heading_vector[1]])
        heading_line.set_3d_properties([z_traj[frame], z_traj[frame] + heading_vector[2]])

        # Adjust plot limits dynamically
        ax1.set_xlim([min(x_traj), max(x_traj)])
        ax1.set_ylim([min(y_traj), max(y_traj)])
        ax1.set_zlim([min(z_traj), max(z_traj)])

    # Animation
    frames = len(x_traj)
    ani = FuncAnimation(fig1, update, frames=frames, interval=dt * 1000, blit=False)

    # Save animation as a GIF
    ani.save('drone_simulation_pid.gif', writer='imagemagick', fps=1/dt)

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
