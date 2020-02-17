import numpy as np
from .spatial_func import project_pt_to_line


class DouglasPeucker:

    def __init__(self, epsilon):
        self.epsilon = epsilon

    def simplify(self, segment):
        if len(segment) <= 3:
            return segment
        projection_dists = [project_pt_to_line(segment[0], segment[-1], segment[i])[2]
                            for i in range(1, len(segment) - 1)]
        if len(projection_dists) <= 2:
            return segment
        max_idx = np.argmax(projection_dists)
        if projection_dists[max_idx] >= self.epsilon:
            left = self.simplify(segment[:max_idx + 2])
            right = self.simplify(segment[max_idx + 1:])
            return left[:-1] + right
        else:
            return [segment[0], segment[-1]]
