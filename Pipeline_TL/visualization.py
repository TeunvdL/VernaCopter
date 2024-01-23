import matplotlib.pyplot as plt
import numpy as np

class Visualization:
    def __init__(self, x, objects):
        self.x = x
        self.objects = objects
    
    def visualize(self):
        """
        Visualize the trajectory.

        Returns
        -------
        None.

        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(self.x[3,:], self.x[4,:], self.x[5,:])

        for object in self.objects:
            center, length, width, height = self.get_clwh(object)
            X, Y, Z = shapes.make_cuboid(center, (length, width, height))
            # check if object name contains 'obstacle' or 'goal'
            if 'obstacle' in object:
                ax.plot_surface(X, Y, Z, color='r', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')
            elif 'goal' in object:
                ax.plot_surface(X, Y, Z, color='g', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')
            # show object names
            ax.text(center[0], center[1], center[2], object)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        # ax.set_xlim(-10, 10)
        # ax.set_ylim(-10, 10)
        # ax.set_zlim(-10, 10)


        plt.show()

    def get_clwh(self, object):
        # get center, length, width, height of object
        xmin, xmax, ymin, ymax, zmin, zmax = self.objects[object]
        center = ((xmin + xmax)/2, (ymin + ymax)/2, (zmin + zmax)/2)
        length = xmax - xmin
        width = ymax - ymin
        height = zmax - zmin
        return center, length, width, height

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