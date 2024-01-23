import numpy as np
import matplotlib.pyplot as plt
from stlpy.systems import LinearSystem
from stlpy.STL import LinearPredicate
from stlpy.solvers import GurobiMICPSolver

class drone_dynamics:
    def __init__(self, mass=20, max_thrust=200):
        self.m = mass # mass of the drone
        self.max_thrust = max_thrust # absolute maximum thrust
        self.u_min = -self.max_thrust*np.ones(3,) # minimum thrust
        self.u_max = self.max_thrust*np.ones(3,) # maximum thrust

        # State space model

        # x_dot = Ax + Bu
        #     y = Cx + Du

        # x = [u, v, w, x, y, z]
        # u = [Fx, Fy, Fz]

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
    def __init__(self, x0 = np.zeros(6,)):
        self.x0 = x0

    def get_specification(self, T=10):
        goal1_bounds = (4, 5, 4, 5, 4, 5)
        goal2_bounds = (-5, -4, -5, -4, -5, -4)
        goal3_bounds = (-6,-5,-5,-4,-5,-4)
        obstacle_bounds = (-1.5, -0.5, -1.5, -0.5, -1.5, -0.5)

        pi1 = STL_formulas.inside_cuboid(goal1_bounds)
        pi2 = STL_formulas.inside_cuboid(goal2_bounds)
        pi3 = STL_formulas.inside_cuboid(goal3_bounds)
        pi4 = STL_formulas.outside_cuboid(obstacle_bounds)
        spec = pi1.eventually(0, T) & pi2.eventually(0, T)& pi3.eventually(0,T) & pi4.always(0, T)
        
        return spec

    def generate_trajectory(self, spec, T=10):
        dynamics = drone_dynamics()
        sys = dynamics.getSystem()
        spec = STLSolver.get_specification(self)

        Q = np.zeros((6,6))
        R = np.eye(3)

        solver = GurobiMICPSolver(spec, sys, self.x0, T, verbose=False)
        solver.AddQuadraticCost(Q=Q, R=R)
        solver.AddControlBounds(dynamics.u_min, dynamics.u_max)
        x, u, _, _ = solver.Solve()

        return x, u