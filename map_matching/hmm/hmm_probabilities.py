import math


class HMMProbabilities:
    def __init__(self, sigma, beta):
        self.sigma = sigma
        self.beta = beta

    def emission_log_probability(self, distance):
        """
        Returns the logarithmic emission probability density.
        :param distance: Absolute distance [m] between GPS measurement and map matching candidate.
        :return:
        """
        return log_normal_distribution(self.sigma, distance)

    def transition_log_probability(self, route_length, linear_distance):
        """
        Returns the logarithmic transition probability density for the given transition parameters.
        :param route_length: Length of the shortest route [m] between two consecutive map matching candidates.
        :param linear_distance: Linear distance [m] between two consecutive GPS measurements.
        :return:
        """
        transition_metric = math.fabs(linear_distance - route_length)
        return log_exponential_distribution(self.beta, transition_metric)


def log_normal_distribution(sigma, x):
    return math.log(1.0 / (math.sqrt(2.0 * math.pi) * sigma)) + (-0.5 * pow(x / sigma, 2))


def log_exponential_distribution(beta, x):
    return math.log(1.0 / beta) - (x / beta)
