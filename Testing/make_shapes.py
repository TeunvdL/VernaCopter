import numpy as np

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