import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib import animation
from basics.scenarios import Scenarios

class Visualizer:
    def __init__(self, x, scenario, animate = False): 
        self.x = x[:3, :]                               # waypoints (only positions)
        self.scenario_name = scenario.scenario_name     # scenario name
        self.objects = scenario.objects                 # objects
        self.dt = 0.05                                  # time step
        self.dT = 1                                     # time to reach target
        n = int(self.dT/self.dt)                        # number of time steps between two targets
        self.n_points = self.x.shape[1]                 # number of targets
        self.times = np.linspace(0, self.dT, n)         # time array
        T = (self.n_points-1)*self.dT                   # total time
        self.N = int(T/self.dt)                         # number of time steps

        if animate:
            self.anim_fig = plt.figure(figsize=(6,6))
            self.anim_ax = self.anim_fig.add_subplot(111, projection='3d')
    
    def visualize_trajectory(self):
        """
        Visualize the trajectory.

        Returns
        -------
        None.

        """
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('Trajectory')
        ax.scatter(self.x[0,:], self.x[1,:], self.x[2,:], 'b', label='Trajectory')
        ax.scatter(self.x[0,0], self.x[1,0], self.x[2,0], c='g', label='Start', s=10)

        for object in self.objects:
            center, length, width, height = self.get_clwh(object)
            X, Y, Z = shapes.make_cuboid(center, (length, width, height))
            if self.scenario_name == "reach_avoid": 
                if 'obstacle' in object: # check if object name contains 'obstacle'
                    ax.plot_surface(X, Y, Z, color='r', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')
                elif 'goal' in object: # check if object name contains 'goal'
                    ax.plot_surface(X, Y, Z, color='#28d778', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')

                ax.set_xlim(-4.5, 4.5)
                ax.set_ylim(-4, 5)
                ax.set_zlim(0, 5)

            elif self.scenario_name == "treasure_hunt":
                if 'wall' in object:
                    ax.plot_surface(X, Y, Z, color='#a3a3a3', rstride=1, cstride=1, alpha=0.05, linewidth=1., edgecolor='k')
                elif 'key' in object:
                    ax.plot_surface(X, Y, Z, color='#28d778', rstride=1, cstride=1, alpha=0.5, linewidth=1., edgecolor='k')
                    ax.text(center[0], center[1], center[2] + 1.2, 'door key', horizontalalignment='center', verticalalignment='center') # show key name
                elif 'door' in object:
                    ax.plot_surface(X, Y, Z, color='#c2853d', rstride=1, cstride=1, alpha=0.5, linewidth=1., edgecolor='k')
                    ax.text(center[0], center[1] - 2, center[2] + 0.5, object, horizontalalignment='center', verticalalignment='center') # show door name
                elif 'chest' in object:
                    ax.plot_surface(X, Y, Z, color='#FFD700', rstride=1, cstride=1, alpha=0.5, linewidth=1., edgecolor='k')
                    ax.text(center[0] - 1.5, center[1], center[2] - 0.2, object, horizontalalignment='center', verticalalignment='center') # show chest name
                elif 'bounds' in object:
                    ax.plot_surface(X, Y, Z, color='#a3a3a3', rstride=1, cstride=1, alpha=0.02, linewidth=1., edgecolor='k')

                ax.set_xlim(-4.5, 4.5)
                ax.set_ylim(-4.5, 4.5)
                ax.set_zlim(0, 6.4)

        # disable axes
        ax.set_axis_off()

        return fig, ax


    def get_clwh(self, object):
        # get center, length, width, height of object
        xmin, xmax, ymin, ymax, zmin, zmax = self.objects[object]
        center = ((xmin + xmax)/2, (ymin + ymax)/2, (zmin + zmax)/2)
        length = xmax - xmin
        width = ymax - ymin
        height = zmax - zmin
        return center, length, width, height
    
    def min_jerk(self, x0, xT, T, t):
        """
        Generate a minimum jerk trajectory between two points. 

        Parameters
        ----------
        x0 : numpy.array
            initial state.
        xT : numpy.array
            final state.
        T : float
            time horizon.
        t : numpy.array
            time array.

        Returns
        -------
        s : numpy.array
            trajectory.

        """
        t = t/T
        a = xT - x0
        b = 10*np.power(t,3) - 15*np.power(t,4) + 6*np.power(t,5)
        s = np.tile(x0, (len(t),1)).T + np.outer(a,b)
        return s
    
    def animate_trajectory(self, gif_name):
        print("Animating trajectory...")
        # save all trajectories in one array
        t = 0
        self.trajectories = np.zeros((3, self.N))
        for i in range(self.n_points-1):
            trajectory = self.min_jerk(self.x[:,i], self.x[:,i+1], self.dT, self.times)
            self.trajectories[:,t:t+len(self.times)] = trajectory
            t += int(self.dT/self.dt)

        anim = animation.FuncAnimation(self.anim_fig, self.animate, frames=self.N, interval=50, blit=False)
        print("Saving animation...")
        anim.save(gif_name)

    def animate(self, i):
        self.anim_ax.clear()
        self.anim_ax.set_xlabel('x')
        self.anim_ax.set_ylabel('y')
        self.anim_ax.set_zlabel('z')
        self.anim_ax.set_xlim(-5,5)
        self.anim_ax.set_ylim(-5,5)
        self.anim_ax.set_zlim(-5,5)
        self.anim_ax.scatter(self.trajectories[0,i], self.trajectories[1,i], self.trajectories[2,i], s = 3, marker='o')
        
        for object in self.objects:
            center, length, width, height = self.get_clwh(object)
            X, Y, Z = shapes.make_cuboid(center, (length, width, height))
            # check if object name contains 'obstacle' or 'goal'
            if 'obstacle' in object:
                self.anim_ax.plot_surface(X, Y, Z, color='r', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')
            elif 'goal' in object:
                self.anim_ax.plot_surface(X, Y, Z, color='g', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')
            # show object names
            self.anim_ax.text(center[0], center[1], center[2], object)
        
        return self.anim_fig, self.anim_ax 
    
    def plot_distance_to_objects(self):
        distances = np.zeros((self.x.shape[1], len(self.objects)))
        for i in range(self.x.shape[1]):
            for j, obj in enumerate(self.objects.values()):
                distances[i,j] = self.distance_to_cuboid(self.x[:3,i], obj)
        
        distfig, ax = plt.subplots(figsize=(8,5))
        ax.set_title('Distance to objects')
        ax.set_xlabel('Time')
        ax.set_ylabel('Distance')
        ax.plot(distances)
        ax.legend(self.objects.keys()) 
        ax.grid()
    
    def distance_to_cuboid(self, coordinate, bounds):
        """
        Calculate the distance from a point to a cuboid.
        """
        x, y, z = coordinate
        xmin, xmax, ymin, ymax, zmin, zmax = bounds

        if x < xmin:
            a = xmin
        elif x > xmax:
            a = xmax
        else:
            a = x

        if y < ymin:
            b = ymin
        elif y > ymax:
            b = ymax
        else:
            b = y

        if z < zmin:
            c = zmin
        elif z > zmax:
            c = zmax
        else:
            c = z

        return np.sqrt((x-a)**2 + (y-b)**2 + (z-c)**2)


class shapes:
    def make_cuboid(center, size):
        """
        Create a data array for cuboid plotting.

        ============= ================================================
        Argument      Description
        ============= ================================================
        center        center of the cuboid, triple
        size          size of the cuboid, triple, (x_length,y_width,z_height)
        :type size: tuple, numpy.array, list
        :param size: size of the cuboid, triple, (x_length,y_width,z_height)
        :type center: tuple, numpy.array, list
        :param center: center of the cuboid, triple, (x,y,z)
        """

        # suppose axis direction: x: to left; y: to inside; z: to upper
        # get the (left, outside, bottom) point
        o = [a - b / 2 for a, b in zip(center, size)]
        # get the length, width, and height
        l, w, h = size
        x = [[o[0], o[0] + l, o[0] + l, o[0], o[0]],  # x coordinate of points in bottom surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],  # x coordinate of points in upper surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],  # x coordinate of points in outside surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]]]  # x coordinate of points in inside surface
        y = [[o[1], o[1], o[1] + w, o[1] + w, o[1]],  # y coordinate of points in bottom surface
            [o[1], o[1], o[1] + w, o[1] + w, o[1]],  # y coordinate of points in upper surface
            [o[1], o[1], o[1], o[1], o[1]],          # y coordinate of points in outside surface
            [o[1] + w, o[1] + w, o[1] + w, o[1] + w, o[1] + w]]    # y coordinate of points in inside surface
        z = [[o[2], o[2], o[2], o[2], o[2]],                        # z coordinate of points in bottom surface
            [o[2] + h, o[2] + h, o[2] + h, o[2] + h, o[2] + h],    # z coordinate of points in upper surface
            [o[2], o[2], o[2] + h, o[2] + h, o[2]],                # z coordinate of points in outside surface
            [o[2], o[2], o[2] + h, o[2] + h, o[2]]]                # z coordinate of points in inside surface
        return np.asarray(x), np.asarray(y), np.asarray(z)


    def make_sphere(center, radius):
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        px, py, pz = center
        r = radius

        x = px + r*np.outer(np.cos(u), np.sin(v))
        y = py + r*np.outer(np.sin(u), np.sin(v))
        z = pz + r*np.outer(np.ones(np.size(u)), np.cos(v))

        return x, y, z
    