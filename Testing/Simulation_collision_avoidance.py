import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Function to update drone position based on velocity and time step
def update_position(position, velocity, dt):
    return position + velocity * dt

# Function to compute the gradient of the loss function
def compute_gradient_loss(current_position, target_position, current_velocity, obstacle_positions, target_velocity=0, attraction_gain=4.0, repulsion_gain=0.4, damping_gain=3.0):
    A = attraction_gain * np.linalg.norm(current_position - target_position) ** 2
    R = repulsion_gain * np.log(np.prod([np.linalg.norm(current_position - obstacle_position) ** 2 for obstacle_position in obstacle_positions]))

    # Gradient of A
    gradient_A = 2 * attraction_gain * (current_position - target_position)

    # Gradient of R
    gradient_R = np.zeros_like(current_position)
    for obstacle_position in obstacle_positions:
        diff = current_position - obstacle_position
        gradient_R += 2 * repulsion_gain * diff / np.linalg.norm(diff) ** 2

    # Damping term based on the difference of velocities
    damping_term = damping_gain * (current_velocity - target_velocity)

    # Gradient of the loss function
    gradient_loss = (gradient_A / R - A * gradient_R / R**2 + damping_term) / R

    return gradient_loss


# Function to simulate drone movement with the modified controller
def simulate_drone_with_modified_controller(duration, dt, target_position, obstacle_positions, max_velocity=5.0):
    position = np.array([1.5, 1.5, 1.5])
    velocity = np.array([-5.0, -5.0, 5.0])
    num_steps = int(duration / dt)

    x_traj, y_traj, z_traj = [position[0]], [position[1]], [position[2]]
    distances_to_target = [np.linalg.norm(position - target_position)]
    distances_to_obstacles = [np.linalg.norm(position - obstacle_positions[0]),
                              np.linalg.norm(position - obstacle_positions[1]),
                              np.linalg.norm(position - obstacle_positions[2])]

    for _ in range(num_steps):
        position = update_position(position, velocity, dt)

        # Compute the gradient of the loss function
        gradient_loss = compute_gradient_loss(position, target_position, velocity, obstacle_positions)

        # Update velocity using the computed gradient
        velocity += -gradient_loss * dt

        # Limit velocity to a maximum value
        current_velocity_magnitude = np.linalg.norm(velocity)
        if current_velocity_magnitude > max_velocity:
            velocity = velocity * (max_velocity / current_velocity_magnitude)

        # Calculate distances to target and obstacles
        distance_to_target = np.linalg.norm(position - target_position)
        distance_to_obstacle1 = np.linalg.norm(position - obstacle_positions[0])
        distance_to_obstacle2 = np.linalg.norm(position - obstacle_positions[1])
        distance_to_obstacle3 = np.linalg.norm(position - obstacle_positions[2])

        # Store distances
        distances_to_target.append(distance_to_target)
        distances_to_obstacles.append(distance_to_obstacle1)
        distances_to_obstacles.append(distance_to_obstacle2)
        distances_to_obstacles.append(distance_to_obstacle3)

        x_traj.append(position[0])
        y_traj.append(position[1])
        z_traj.append(position[2])

    return x_traj, y_traj, z_traj, distances_to_target, distances_to_obstacles


def main():
    duration = 10  # seconds
    dt = 0.1  # time step
    target_position = np.array([5.0, 5.0, 5.0])
    controller_gain = 1.5
    damping = 2.0

    # List of objects and their positions
    obstacle_positions = [(2.0, 2.0, 2.0), (4.0, 4.0, 4.0), (-1.0, 1.0, 4.0)]

    # Simulation
    x_traj, y_traj, z_traj, distances_to_target, distances_to_obstacles = simulate_drone_with_modified_controller(
        duration, dt, target_position, obstacle_positions
    )

    # Plotting the 3D trajectory
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')
    target, = ax1.plot([target_position[0]], [target_position[1]], [target_position[2]], 'go', label='Target Position')

    # Initialize markers and lines for the drone representation
    marker, = ax1.plot([], [], [], 'ro', label='Drone Marker')
    heading_line, = ax1.plot([], [], [], 'r-', label='Heading Direction')

    # Plot objects as points
    obstacle_positions = np.array(obstacle_positions).T  # Transpose the list of obstacles
    objects_plot, = ax1.plot(obstacle_positions[0], obstacle_positions[1], obstacle_positions[2], 'bo', label='Obstacles')

    ax1.set_xlabel('X-axis')
    ax1.set_ylabel('Y-axis')
    ax1.set_zlabel('Z-axis')
    ax1.legend()

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
        ax1.set_xlim([min(x_traj), max(x_traj)])
        ax1.set_ylim([min(y_traj), max(y_traj)])
        ax1.set_zlim([min(z_traj), max(z_traj)])

    # Animation
    frames = len(x_traj)
    ani = FuncAnimation(fig1, update, frames=frames, interval=dt * 1000, blit=False)

    # Save animation as a GIF
    ani.save('drone_simulation.gif', writer='imagemagick', fps=1/dt)

    # Plotting the distance plot
    fig2, ax2 = plt.subplots()
    ax2.plot(np.arange(0, duration + dt, dt), distances_to_target, label='Distance to Target')
    ax2.plot(np.arange(0, duration + dt, dt), distances_to_obstacles[0::3], label='Distance to Obstacle 1')
    ax2.plot(np.arange(0, duration + dt, dt), distances_to_obstacles[1::3], label='Distance to Obstacle 2')
    ax2.plot(np.arange(0, duration + dt, dt), distances_to_obstacles[2::3], label='Distance to Obstacle 3')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Distance')
    ax2.legend()
    ax2.grid()
    ax2.set_ylim(0, 10)

    plt.show()

if __name__ == "__main__":
    main()
