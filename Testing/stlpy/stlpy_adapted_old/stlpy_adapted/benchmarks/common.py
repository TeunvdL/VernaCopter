##
#
# Common helper functions for defining STL specifications.
#
##

import numpy as np
from stlpy.STL import LinearPredicate, NonlinearPredicate
from matplotlib.patches import Rectangle, Circle

def inside_sphere_formula(center, radius, y1_index, y2_index, y3_index, d, name=None):
    """
    Create an STL formula representing being inside a
    sphere with the given center and radius.

    :param center:      Triple ``(y1, y2, y3)`` specifying the center of the
                        sphere.
    :param radius:      Radius of the sphere.
    :param y1_index:    index of the first (``y1``) dimension
    :param y2_index:    index of the second (``y2``) dimension
    :param y3_index:    index of the second (``y3``) dimension
    :param d:           dimension of the overall signal
    :param name:        (optional) string describing this formula

    :return inside_sphere:   A ``NonlinearPredicate`` specifying being inside the
                             sphere at time zero.
    """
    # Define the predicate function g(y) >= 0
    def g(y):
        y1 = y[y1_index]
        y2 = y[y2_index]
        y3 = y[y3_index]
        return radius**2 - (y1-center[0])**2 - (y2-center[1])**2 - (y3-center[2])**2

    return NonlinearPredicate(g, d, name=name)


def inside_cuboid_formula(bounds, y1_index, y2_index, y3_index, d, name=None):
    """
    Create an STL formula representing being inside a
    cuboid with the given bounds:

    ::
                   +-------------------+ y3_max
                  / |                 /|
                 /  |                / |
                +-------------------+  |
         y2_max |   +               |  + y3_min
                |  /                | /
                | /                 |/
      y2_min    +-------------------+
                y1_min              y1_max

    :param bounds:      Tuple ``(y1_min, y1_max, y2_min, y2_max, y3_min, y3_max)`` 
                        containing the bounds of the rectangle. 
    :param y1_index:    index of the first (``y1``) dimension
    :param y2_index:    index of the second (``y2``) dimension
    :param y3_index:    index of the second (``y3``) dimension
    :param d:           dimension of the overall signal
    :param name:        (optional) string describing this formula

    :return inside_rectangle:   An ``STLFormula`` specifying being inside the
                                rectangle at time zero.
    """
    assert y1_index < d , "index must be less than signal dimension"
    assert y2_index < d , "index must be less than signal dimension"
    assert y3_index < d , "index must be less than signal dimension"

    # Unpack the bounds
    y1_min, y1_max, y2_min, y2_max, y3_min, y3_max = bounds

    # Create predicates a*y >= b for each side of the rectangle
    a1 = np.zeros((1,d)); a1[:,y1_index] = 1
    right = LinearPredicate(a1, y1_min)
    left = LinearPredicate(-a1, -y1_max)

    a2 = np.zeros((1,d)); a2[:,y2_index] = 1
    top = LinearPredicate(a2, y2_min)
    bottom = LinearPredicate(-a2, -y2_max)

    a3 = np.zeros((1,d)); a2[:,y3_index] = 1
    front = LinearPredicate(a3, y3_min)
    back = LinearPredicate(-a3, -y3_max)

    # Take the conjuction across all the sides
    inside_cuboid = right & left & top & bottom & front & back

    # set the names
    if name is not None:
        right.name = "right of " + name
        left.name = "left of " + name
        top.name = "top of " + name
        bottom.name = "bottom of " + name
        front.name = "front of " + name
        back.name = "back of " + name
        inside_cuboid.name = name

    return inside_cuboid


def outside_cuboid_formula(bounds, y1_index, y2_index, y3_index, d, name=None):
    """
    Create an STL formula representing being outside a
    cuboid with the given bounds:

    ::
                   +-------------------+ y3_max
                  / |                 /|
                 /  |                / |
                +-------------------+  |
         y2_max |   +               |  + y3_min
                |  /                | /
                | /                 |/
      y2_min    +-------------------+
                y1_min              y1_max

    :param bounds:      Tuple ``(y1_min, y1_max, y2_min, y2_max, y3_min, y3_max)`` 
                        containing the bounds of the rectangle. 
    :param y1_index:    index of the first (``y1``) dimension
    :param y2_index:    index of the second (``y2``) dimension
    :param y3_index:    index of the second (``y3``) dimension
    :param d:           dimension of the overall signal
    :param name:        (optional) string describing this formula
    
    :return outside_rectangle:   An ``STLFormula`` specifying being outside the
                                 cuboid at time zero.
    """
    assert y1_index < d , "index must be less than signal dimension"
    assert y2_index < d , "index must be less than signal dimension"
    assert y3_index < d , "index must be less than signal dimension"

    # Unpack the bounds
    y1_min, y1_max, y2_min, y2_max, y3_min, y3_max = bounds

    # Create predicates a*y >= b for each side of the rectangle
    a1 = np.zeros((1,d)); a1[:,y1_index] = 1
    right = LinearPredicate(a1, y1_max)
    left = LinearPredicate(-a1, -y1_min)

    a2 = np.zeros((1,d)); a2[:,y2_index] = 1
    top = LinearPredicate(a2, y2_max)
    bottom = LinearPredicate(-a2, -y2_min)

    a3 = np.zeros((1,d)); a3[:,y3_index] = 1
    front = LinearPredicate(a3, y3_max)
    back = LinearPredicate(-a3, -y3_min)

    # Take the disjuction across all the sides
    outside_cuboid = right | left | top | bottom | front | back

    # set the names
    if name is not None:
        right.name = "right of " + name
        left.name = "left of " + name
        top.name = "top of " + name
        bottom.name = "bottom of " + name
        front.name = "front of " + name
        back.name = "back of " + name
        outside_cuboid.name = name

    return outside_cuboid


def make_rectangle_patch(xmin, xmax, ymin, ymax, **kwargs):
    """
    Convienience function for making a ``matplotlib.patches.Rectangle`` 
    patch for visualizing a rectangle:

    ::

       ymax   +-------------------+
              |                   |
              |                   |
              |                   |
       ymin   +-------------------+
              xmin                xmax

    :param xmin:        horizontal lower bound of the rectangle.
    :param xmax:        horizontal upper bound of the rectangle.
    :param ymin:        vertical lower bound of the rectangle.
    :param ymax:        vertical upper bound of the rectangle.
    :param kwargs:    (optional) keyword arguments passed to
                        the ``Rectangle`` constructor.

    :return patch:  a ``matplotlib.patches.Rectangle`` patch.

    """
    x = xmin
    y = ymin
    width = xmax-x
    height = ymax-y

    return Rectangle((x,y), width, height, **kwargs)

def make_cuboid_data(center, size):
    """
    Convienience function for generating data for visualizing a cuboid:

    ::
                   +-------------------+ y3_max
                  / |                 /|
                 /  |                / |
                +-------------------+  |
         y2_max |   +               |  + y3_min
                |  /                | /
                | /                 |/
      y2_min    +-------------------+
                y1_min              y1_max

    :param center:      center of the cuboid, triple
    :param size:        size of the cuboid, triple, (x_width,y_length,z_height)

    :return patch:  a ``matplotlib.patches.Rectangle`` patch.

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

def make_sphere_data(center, radius, **kwargs):
    """
    Convienience function for generating data for visualizing a sphere:

    :param center:      center of the sphere, triple
    :param radius:      radius of the sphere
    """
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    px, py, pz = center
    r = radius

    x = px + r*np.outer(np.cos(u), np.sin(v))
    y = py + r*np.outer(np.sin(u), np.sin(v))
    z = pz + r*np.outer(np.ones(np.size(u)), np.cos(v))

    return x, y, z
