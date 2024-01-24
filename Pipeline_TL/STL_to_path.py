import numpy as np
import matplotlib.pyplot as plt
from stlpy.systems import LinearSystem
from stlpy.STL import LinearPredicate
from stlpy.solvers import GurobiMICPSolver

class drone_dynamics:
    """
    A class representing the dynamics of a drone.

    Parameters:
    - mass (float): Mass of the drone. Default is 20.
    - max_thrust (float): Absolute maximum thrust of the drone. Default is 200.

    Attributes:
    - m (float): Mass of the drone.
    - max_thrust (float): Absolute maximum thrust.
    - u_min (numpy.ndarray): Minimum thrust values for each axis.
    - u_max (numpy.ndarray): Maximum thrust values for each axis.
    - A (numpy.ndarray): State space matrix A for the drone dynamics.
    - B (numpy.ndarray): State space matrix B for the drone dynamics.
    - C (numpy.ndarray): Output matrix C for the drone dynamics.
    - D (numpy.ndarray): Feedforward matrix D for the drone dynamics.

    State space model

    x_dot = Ax + Bu
        y = Cx + Du

    x = [u, v, w, x, y, z]
    u = [Fx, Fy, Fz]

    A =    [[0., 0., 0., 0., 0., 0.],  B = 1/m [[1., 0., 0.],
            [0., 0., 0., 0., 0., 0.],           [0., 1., 0.],
            [0., 0., 0., 0., 0., 0.],           [0., 0., 1.],
            [1., 0., 0., 0., 0., 0.],           [0., 0., 0.],
            [0., 1., 0., 0., 0., 0.],           [0., 0., 0.],
            [0., 0., 1., 0., 0., 0.]]           [0., 0., 0.]]

    C =    [[1., 0., 0., 0., 0., 0.],      D = [[0., 0., 0.],
            [0., 1., 0., 0., 0., 0.],           [0., 0., 0.],
            [0., 0., 1., 0., 0., 0.],           [0., 0., 0.],
            [0., 0., 0., 1., 0., 0.],           [0., 0., 0.],
            [0., 0., 0., 0., 1., 0.],           [0., 0., 0.],
            [0., 0., 0., 0., 0., 1.]]           [0., 0., 0.]]
    """

    def __init__(self, mass=20, max_thrust=200):
        self.m = mass # mass of the drone
        self.max_thrust = max_thrust # absolute maximum thrust
        self.u_min = -self.max_thrust*np.ones(3,) # minimum thrust
        self.u_max = self.max_thrust*np.ones(3,) # maximum thrust

        """
        State space model

        x_dot = Ax + Bu
            y = Cx + Du

        x = [u, v, w, x, y, z]
        u = [Fx, Fy, Fz]

        A =    [[0., 0., 0., 0., 0., 0.],   B = 1/m [[1., 0., 0.],
                [0., 0., 0., 0., 0., 0.],            [0., 1., 0.],
                [0., 0., 0., 0., 0., 0.],            [0., 0., 1.],
                [1., 0., 0., 0., 0., 0.],            [0., 0., 0.],
                [0., 1., 0., 0., 0., 0.],            [0., 0., 0.],
                [0., 0., 1., 0., 0., 0.]]            [0., 0., 0.]]

        C =     [[1., 0., 0., 0., 0., 0.]       D = [[0., 0., 0.],
                 [0., 1., 0., 0., 0., 0.]            [0., 0., 0.],
                 [0., 0., 1., 0., 0., 0.]            [0., 0., 0.],
                 [0., 0., 0., 1., 0., 0.]            [0., 0., 0.],
                 [0., 0., 0., 0., 1., 0.]            [0., 0., 0.],
                 [0., 0., 0., 0., 0., 1.]]           [0., 0., 0.]]           
        """
        self.A = np.zeros((6,6))
        self.A[3,0] = 1
        self.A[4,1] = 1
        self.A[5,2] = 1

        self.B = np.zeros((6,3))
        self.B[0,0] = 1/self.m
        self.B[1,1] = 1/self.m
        self.B[2,2] = 1/self.m

        self.C = np.zeros((6,6))
        for i in range(6):  
            self.C[i,i] = 1

        self.D = np.zeros((6,3))
    
    def getSystem(self):
        sys = LinearSystem(self.A,self.B,self.C,self.D)
        return sys

class STL_formulas:
    def inside_cuboid(bounds):
       """
       Create an STL formula representing being inside a
       cuboid with the given bounds:

       ::
                   +-------------------+ z_max
                  / |                 /|
                 /  |                / |
                +-------------------+  |
         y_max  |   +               |  + z_min
                |  /                | /
                | /                 |/
      y_min     +-------------------+
                x_min              x_max

       :param bounds:      Tuple ``(x_min, x_max, y_min, y_max, z_min, z_max)`` 
                            containing the bounds of the cuboid. 

       :return inside_cuboid:   An ``STLFormula`` specifying being inside the
                                   cuboid at time zero.
       """

       # Unpack the bounds
       x_min, x_max, y_min, y_max, z_min, z_max = bounds

       # Create predicates a*y >= b for each side of the cuboid
       a1 = np.zeros((1,6)); a1[:,3] = 1
       right = LinearPredicate(a1, x_min)
       left = LinearPredicate(-a1, -x_max)

       a2 = np.zeros((1,6)); a2[:,4] = 1
       front = LinearPredicate(a2, y_min)
       back = LinearPredicate(-a2, -y_max)

       a3 = np.zeros((1,6)); a3[:,5] = 1
       top = LinearPredicate(a3, z_min)
       bottom = LinearPredicate(-a3, -z_max)

       # Take the conjuction across all the sides
       inside_cuboid = right & left & front & back & top & bottom

       return inside_cuboid


    def outside_cuboid(bounds):
       """
       Create an STL formula representing being outside a
       cuboid with the given bounds:

       ::
                   +-------------------+ z_max
                  / |                 /|
                 /  |                / |
                +-------------------+  |
         y_max  |   +               |  + z_min
                |  /                | /
                | /                 |/
      y_min     +-------------------+
                x_min              x_max

       :param bounds:      Tuple ``(x_min, x_max, y_min, y_max, z_min, z_max)`` 
                            containing the bounds of the rectangle. 
       
       :return outside_cuboid:   An ``STLFormula`` specifying being outside the
                                   cuboid at time zero.
       """

       # Unpack the bounds
       x_min, x_max, y_min, y_max, z_min, z_max = bounds

       # Create predicates a*y >= b for each side of the rectangle
       a1 = np.zeros((1,6)); a1[:,3] = 1
       right = LinearPredicate(a1, x_max)
       left = LinearPredicate(-a1, -x_min)

       a2 = np.zeros((1,6)); a2[:,4] = 1
       front = LinearPredicate(a2, y_max)
       back = LinearPredicate(-a2, -y_min)

       a3 = np.zeros((1,6)); a3[:,5] = 1
       top = LinearPredicate(a3, z_max)
       bottom = LinearPredicate(-a3, -z_min)

       # Take the disjuction across all the sides
       outside_cuboid = right | left | front | back | top | bottom

       return outside_cuboid
    

class STLSolver:
    def __init__(self, spec, x0 = np.zeros(6,), T=10):
        self.x0 = x0
        self.spec = spec


    def generate_trajectory(self, T=10):
        dynamics = drone_dynamics()
        sys = dynamics.getSystem()

        Q = np.zeros((6,6))
        R = np.eye(3)

        solver = GurobiMICPSolver(self.spec, sys, self.x0, T, verbose=False)
        solver.AddQuadraticCost(Q=Q, R=R)
        solver.AddControlBounds(dynamics.u_min, dynamics.u_max)
        x, u, _, _ = solver.Solve()

        return x, u