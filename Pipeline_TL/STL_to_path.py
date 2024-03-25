import numpy as np
from stlpy.systems import LinearSystem
from stlpy.STL import LinearPredicate, NonlinearPredicate
from stlpy.solvers import GurobiMICPSolver

class drone_dynamics:
    """
    A class representing the dynamics of a drone.

    Parameters:
    - max_acc (float): Absolute maximum acceleration of the drone. Default is 10.

    Attributes:
    - max_thrust (float): Absolute maximum acceleration of the drone.
    - u_min (numpy.ndarray): Minimum acceleration of the drone.
    - u_max (numpy.ndarray): Maximum acceleration of the drone.
    - A (numpy.ndarray): State space matrix A for the drone dynamics.
    - B (numpy.ndarray): State space matrix B for the drone dynamics.
    - C (numpy.ndarray): Output matrix C for the drone dynamics.
    - D (numpy.ndarray): Feedforward matrix D for the drone dynamics.

    State space model

    x_dot = Ax + Bu
        y = Cx + Du

    x = [x, y, z, vx, vy, vz]
    u = [ax, ay, az]

    A =    [[0., 0., 0., 1., 0., 0.],   B = [[0., 0., 0.],
            [0., 0., 0., 0., 1., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 1.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [1., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [0., 1., 0.],
            [0., 0., 0., 0., 0., 0.]]        [0., 0., 1.]]

    C =    [[1., 0., 0., 0., 0., 0.],   D = [[0., 0., 0.],
            [0., 1., 0., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 1., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.]]        [0., 0., 0.]]
    """

    def __init__(self, dt=0.1, max_acc=10):
        self.dt = dt                            # time step
        self.max_acc = max_acc                  # absolute maximum acceleration

        self.A = np.zeros((6,6))
        self.A[0,3] = 1
        self.A[1,4] = 1
        self.A[2,5] = 1

        self.B = np.zeros((6,3))
        self.B[3,0] = 1
        self.B[4,1] = 1
        self.B[5,2] = 1

        self.C = np.zeros((6,6))
        for i in range(3):  
            self.C[i,i] = 1

        self.D = np.zeros((6,3))

        self.A_tilde = np.eye(6) + self.A*self.dt
        self.B_tilde = self.B*self.dt
    
    def getSystem(self):
        sys = LinearSystem(self.A_tilde,self.B_tilde,self.C,self.D)
        return sys
    

class STLSolver:
    def __init__(self, specs, objects, x0 = np.zeros(6,), T=10):
        self.objects = objects
        self.specs = specs
        self.x0 = x0
        self.T = T

    def generate_trajectories(self, dt, max_acc, max_speed, verbose = False):
        self.dt = dt
        self.max_acc = max_acc
        self.max_speed = max_speed
        self.verbose = verbose
        objects = self.objects
        N = int(self.T/self.dt)
        N_specs = len(self.specs)

        all_x = np.zeros((6, N_specs*(N+1)))
        all_u = np.zeros((3, N_specs*(N+1)))

        x0 = self.x0
        for i in range(N_specs):
            print("Solving for spec ", i+1, " of ", N_specs)
            #print("Current x0: ", x0)
            print("Current spec: ", self.specs[i])
            x, u = self.generate_trajectory(eval(self.specs[i]), x0)
            all_x[:,i*(N+1):(i+1)*(N+1)] = x
            all_u[:,i*(N+1):(i+1)*(N+1)] = u
            #print("x: ", x)
            #x0 = x[:,-1]
            #print("New x0: ", x0)

        return all_x, all_u

    def generate_trajectory(self, spec, x0):
        dynamics = drone_dynamics(dt=self.dt, max_acc=self.max_acc)
        sys = dynamics.getSystem()

        Q = np.zeros((6,6))     # state cost   : penalize position error
        R = np.eye(3)           # control cost : penalize control effort

        N = int(self.T/dynamics.dt)
        solver = GurobiMICPSolver(spec, sys, x0, N, verbose=self.verbose)
        solver.AddQuadraticCost(Q=Q, R=R)
        u_min = -dynamics.max_acc*np.ones(3,)  # minimum acceleration
        u_max = dynamics.max_acc*np.ones(3,)   # maximum acceleration
        solver.AddControlBounds(u_min, u_max)
        state_bounds = np.array([np.inf, np.inf, np.inf, self.max_speed, self.max_speed, self.max_speed])
        solver.AddStateBounds(-state_bounds, state_bounds)
        x, u, _, _ = solver.Solve()

        return x, u


class STL_formulas:
    def inside_cuboid(bounds, tolerance=0.1):
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
       a1 = np.zeros((1,6)); a1[:,0] = 1
       right = LinearPredicate(a1, x_min + tolerance)
       left = LinearPredicate(-a1, -x_max + tolerance)

       a2 = np.zeros((1,6)); a2[:,1] = 1
       front = LinearPredicate(a2, y_min + tolerance)
       back = LinearPredicate(-a2, -y_max + tolerance)

       a3 = np.zeros((1,6)); a3[:,2] = 1
       top = LinearPredicate(a3, z_min + tolerance)
       bottom = LinearPredicate(-a3, -z_max + tolerance)

       # Take the conjuction across all the sides
       inside_cuboid = right & left & front & back & top & bottom

       return inside_cuboid


    def outside_cuboid(bounds, tolerance=0.1):
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

       :param bounds:           Tuple ``(x_min, x_max, y_min, y_max, z_min, z_max)`` 
                                    containing the bounds of the rectangle. 
       
       :return outside_cuboid:  An ``STLFormula`` specifying being outside the
                                    cuboid at time zero.
       """

       # Unpack the bounds
       x_min, x_max, y_min, y_max, z_min, z_max = bounds

       # Create predicates a*y >= b for each side of the rectangle
       a1 = np.zeros((1,6)); a1[:,0] = 1
       right = LinearPredicate(a1, x_max + tolerance)
       left = LinearPredicate(-a1, -x_min + tolerance)

       a2 = np.zeros((1,6)); a2[:,1] = 1
       front = LinearPredicate(a2, y_max + tolerance)
       back = LinearPredicate(-a2, -y_min + tolerance)

       a3 = np.zeros((1,6)); a3[:,2] = 1
       top = LinearPredicate(a3, z_max + tolerance)
       bottom = LinearPredicate(-a3, -z_min + tolerance)

       # Take the disjuction across all the sides
       outside_cuboid = right | left | front | back | top | bottom

       return outside_cuboid
    
    def inside_sphere(params):
        """
        Create an STL formula representing being inside a
        sphere with the given center and radius:

        ::
                         *********
                   **                 **
               **                         **
            **                               **
          **                                   **
         **                 ___                 **
        **        *********     *********        **
        **  *****                    r    *****  **
        ***                  o----------------- ***  
        **  *****           C             *****  **
        **        ********* ___ *********        **
         **                                     **
          **                                  **
            **                               **
               **                         **  
                   **                 **                            
                         *********

        :param parameters:      Tuple ``(center_x, center_y, center_z, radius)`` containing
                                    the center and radius of the sphere.
        :return inside_sphere:  An ``STLFormula`` specifying being inside the
                                    sphere at time zero.
        """

        # Unpack the parameters
        x_center, y_center, z_center, radius = params
       
        # Define the predicate function g(y) >= 0
        def g(y):
            y1 = y[0]
            y2 = y[1]
            y3 = y[2]
            return radius**2 - (y1-x_center)**2 - (y2-y_center)**2 - (y3-z_center)**2

        return NonlinearPredicate(g, d=6)
    
    def outside_sphere(params):
        """
        Create an STL formula representing being outside a
        sphere with the given center and radius:

        ::
                         *********
                   **                 **
               **                         **
            **                               **
          **                                   **
         **                 ___                 **
        **        *********     *********        **
        **  *****                    r    *****  **
        ***                  o----------------- ***  
        **  *****           C             *****  **
        **        ********* ___ *********        **
         **                                     **
          **                                  **
            **                               **
               **                         **  
                   **                 **                            
                         *********

        :param params:      Tuple ``(center_x, center_y, center_z, radius)`` containing
                                    the center and radius of the sphere.
        :return outside_sphere: An ``STLFormula`` specifying being outside the
                                    sphere at time zero.
        """

        # Unpack the parameters
        x_center, y_center, z_center, radius = params
       
        # Define the predicate function g(y) >= 0
        def g(y):
            y1 = y[0]
            y2 = y[1]
            y3 = y[2]
            return (y1-x_center)**2 + (y2-y_center)**2 + (y3-z_center)**2 - radius**2

        return NonlinearPredicate(g, d=6)
    

