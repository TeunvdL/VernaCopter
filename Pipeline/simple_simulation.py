import numpy as np

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

class DroneSimulator:
    def __init__(self, duration, dt, max_velocity=5.0, kp=1.0, ki=0.1, kd=0.01):
        self.duration = duration
        self.dt = dt
        self.max_velocity = max_velocity
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def update_position(self, position, velocity):
        return position + velocity * self.dt

    def simulate_drone(self, 
                       target_position, 
                       start_position = np.array([0., 0., 0.]), 
                       start_velocity = np.array([0., 0., 0.]),):
        
        position = start_position
        velocity = start_velocity

        num_steps = int(self.duration / self.dt)

        positions = position
        velocities = velocity

        distances_to_target = [np.linalg.norm(position - target_position)]

        # PID Controller for each axis
        pid_x = PIDController(self.kp, self.ki, self.kd)
        pid_y = PIDController(self.kp, self.ki, self.kd)
        pid_z = PIDController(self.kp, self.ki, self.kd)

        for _ in range(num_steps):
            # Compute error for each axis
            error_x = target_position[0] - position[0]
            error_y = target_position[1] - position[1]
            error_z = target_position[2] - position[2]

            # Update velocity using PID controller
            velocity[0] += pid_x.update(error_x, self.dt)
            velocity[1] += pid_y.update(error_y, self.dt)
            velocity[2] += pid_z.update(error_z, self.dt)

            # Limit velocity to a maximum value
            current_velocity_magnitude = np.linalg.norm(velocity)
            if current_velocity_magnitude > self.max_velocity:
                velocity = velocity * (self.max_velocity / current_velocity_magnitude)

            # Update position
            position = self.update_position(position, velocity)

            # Calculate distance to target
            distance_to_target = np.linalg.norm(position - target_position)

            # Store distances
            distances_to_target.append(distance_to_target)

            positions = np.vstack((positions, position))
            velocities = np.vstack((velocities, velocity))

        return positions, distances_to_target, velocities