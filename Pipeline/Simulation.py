import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Function to update drone position based on velocity and time step
def update_position(position, velocity, dt):
    return position + velocity * dt

# Modified Proportional Controller with Damping
def proportional_controller_modified(current_position, target_position, velocity, gain, damping):
    error = target_position - current_position
    damping_term = -damping * velocity  # Damping term proportional to velocity
    return gain * error + damping_term

# Function to simulate drone movement with modified controller
def simulate_drone_with_modified_controller(duration, dt, target_position, controller_gain, damping):
    # Initial position and velocity
    position = np.array([0.0, 0.0, 0.0])
    global velocity  # Make velocity global
    velocity = np.array([-10.0, -10.0, 15.0])

    # Number of time steps
    num_steps = int(duration / dt)

    # Lists to store the trajectory
    x_traj, y_traj, z_traj = [position[0]], [position[1]], [position[2]]

    # Simulation loop
    for _ in range(num_steps):
        # Update position
        position = update_position(position, velocity, dt)

        # Apply the modified controller
        velocity += proportional_controller_modified(position, target_position, velocity, controller_gain, damping) * dt

        # Store position in trajectory lists
        x_traj.append(position[0])
        y_traj.append(position[1])
        z_traj.append(position[2])

    return x_traj, y_traj, z_traj

# Main function to run the simulation and plot the trajectory with a modified controller
def main():
    # Simulation parameters
    duration = 10  # seconds
    dt = 0.1  # time step

    # Target position for the controller
    target_position = np.array([5.0, 5.0, 5.0])

    # Controller gains
    controller_gain = 1.5  # Adjust gain to control overshooting
    damping = 2.0  # Adjust damping to control overshooting

    # Run the simulation with the modified controller
    x_traj, y_traj, z_traj = simulate_drone_with_modified_controller(duration, dt, target_position, controller_gain, damping)

    # Plotting the 3D trajectory
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    target, = ax.plot([target_position[0]], [target_position[1]], [target_position[2]], 'go', label='Target Position')

    # Initialize markers and lines for the drone representation
    marker, = ax.plot([], [], [], 'ro', label='Drone Marker')
    heading_line, = ax.plot([], [], [], 'r-', label='Heading Direction')

    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    #ax.legend()

    def update(frame):
        # Update marker representing the current position of the drone
        marker.set_data(x_traj[frame], y_traj[frame])
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
        ax.set_xlim([min(x_traj), max(x_traj)])
        ax.set_ylim([min(y_traj), max(y_traj)])
        ax.set_zlim([min(z_traj), max(z_traj)])

    # Animation
    frames = len(x_traj)
    ani = FuncAnimation(fig, update, frames=frames, interval=dt * 1000, blit=False)

    # Save animation as a GIF
    ani.save('drone_simulation.gif', writer='imagemagick', fps=1/dt)

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()