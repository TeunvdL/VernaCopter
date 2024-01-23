from .base import BenchmarkScenario
from .common import (inside_cuboid_formula,
                     outside_cuboid_formula,
                     make_cuboid_data)
from ..systems import DoubleIntegrator

class NarrowPassage(BenchmarkScenario):
    r"""
    A 2D mobile robot with double integrator dynamics must navigate around
    several obstacles (:math:`\mathcal{O}_i`) before reaching one of two
    goals (:math:`\mathcal{G}_i`).

    .. math::

        \varphi = F_{[0,T]}(\mathcal{G}_1 \lor \mathcal{G}_2) \land
            G_{[0,T]} \left( \bigwedge_{i=1}^4 \lnot \mathcal{O}_i \right)

    :param T:   The time horizon of the specification.
    """
    def __init__(self, T):
        # Define obstacle and goal regions by their bounds,
        # (xmin, xmax, ymin, ymax, zmin, zmax)
        self.obstacles = [(2,5,4,6,4,6),
                          (5.5,9,3.8,5.7,3.8,5.7),
                          (4.6,8,0.5,3.5,0.5,3.5),
                          (2.2,4.4,6.4,11,6.4,11)]
        self.goals = [(7,8,8,9,8,9),
                      (9.5,10.5,1.5,2.5,1.5,2.5)]
        self.T = T

    def GetSpecification(self):
        # Goal Reaching
        goal_formulas = []
        for goal in self.goals:
            goal_formulas.append(inside_cuboid_formula(goal, 0, 1, 2, 6))

        at_any_goal = goal_formulas[0]
        for i in range(1,len(goal_formulas)):
            at_any_goal = at_any_goal | goal_formulas[i]

        # Obstacle Avoidance
        obstacle_formulas = []
        for obs in self.obstacles:
            obstacle_formulas.append(outside_cuboid_formula(obs, 0, 1, 2, 6))

        obstacle_avoidance = obstacle_formulas[0]
        for i in range(1, len(obstacle_formulas)):
            obstacle_avoidance = obstacle_avoidance & obstacle_formulas[i]

        # Put all of the constraints together in one specification
        specification = at_any_goal.eventually(0, self.T) & \
                        obstacle_avoidance.always(0, self.T)

        return specification

    def GetSystem(self):
        return DoubleIntegrator(3)

    def add_to_plot(self, ax):
        # Make and add cuboid patches
        for obstacle in self.obstacles:
            center = (obstacle[0] + obstacle[1])/2, (obstacle[2] + obstacle[3])/2, (obstacle[4] + obstacle[5])/2
            length = obstacle[1] - obstacle[0]
            width = obstacle[3] - obstacle[2]
            height = obstacle[5] - obstacle[4]
            X, Y, Z = make_cuboid_data(center, (length, width, height))
            ax.plot_surface(X, Y, Z, color='b', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')
        for goal in self.goals:
            center = (goal[0] + goal[1])/2, (goal[2] + goal[3])/2, (goal[4] + goal[5])/2
            length = goal[1] - goal[0]
            width = goal[3] - goal[2]
            height = goal[5] - goal[4]
            X, Y, Z = make_cuboid_data(center, (length, width, height))
            ax.plot_surface(X, Y, Z, color='g', rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')

        # set the field of view
        ax.set_xlim((0,12))
        ax.set_ylim((0,12))
        ax.set_aspect('equal')
