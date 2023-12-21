import numpy as np

class Drone:
    def __init__(self, start_position, start_velocity, col="red",size=0.3):
        self.size = size
        self.rotor_radius = self.size/2.5
        self.col = col
        self.position = start_position
        self.velocity = start_velocity
        self.heading_direction = self.velocity/np.linalg.norm(self.velocity)

    def rotate_z(self, vector, theta):
        rotation_matrix = np.array([[np.cos(theta), -np.sin(theta), 0.0],
                                    [np.sin(theta), np.cos(theta), 0.0],
                                    [0.0, 0.0, 1.0]])
        return np.matmul(rotation_matrix, vector)

    def get_rotor_positions(self):
        theta = np.arctan2(self.velocity[1], self.velocity[0])
        front_left_vector = np.array([0.5*self.size, 0.5*self.size, 0.0])
        front_right_vector = np.array([0.5*self.size, -0.5*self.size, 0.0])
        back_left_vector = np.array([-0.5*self.size, 0.5*self.size, 0.0])
        back_right_vector = np.array([-0.5*self.size, -0.5*self.size, 0.0])

        front_left_vector_rotated = self.rotate_z(front_left_vector, theta)
        front_right_vector_rotated = self.rotate_z(front_right_vector, theta)
        back_left_vector_rotated = self.rotate_z(back_left_vector, theta)
        back_right_vector_rotated = self.rotate_z(back_right_vector, theta)
        
        front_left_position = self.position + front_left_vector_rotated
        front_right_position = self.position + front_right_vector_rotated
        back_left_position = self.position + back_left_vector_rotated
        back_right_position = self.position + back_right_vector_rotated
    
        rotorpositions = np.array([front_left_position, front_right_position, back_right_position, back_left_position])

        return rotorpositions