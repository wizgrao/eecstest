"""
robust distribution function is modified from:
https://github.com/Spriteware/lt-codes-python/blob/master/distributions.py
"""
import numpy as np
import math
import random


def robust_distribution(N,loop):
    EPSILON = 0.0001
    ROBUST_FAILURE_PROBABILITY = 0.01
    """ Create the robust soliton distribution. 
    This fixes the problems of the ideal distribution
    Cf. https://en.wikipedia.org/wiki/Soliton_distribution
    """

    # The choice of M is not a part of the distribution ; it may be improved
    # We take the median and add +1 to avoid possible division by zero
    M = N // 2 + 1
    R = N / M

    extra_proba = [0] + [1 / (i * M) for i in range(1, M)]
    extra_proba += [math.log(R / ROBUST_FAILURE_PROBABILITY) / M]  # Spike at M
    extra_proba += [0 for k in range(M+1, N+1)]

    prob = [0, 1 / N]
    prob += [1 / (k * (k - 1)) for k in range(2, N + 1)]
    probabilities = np.add(extra_proba, prob)
    probabilities /= np.sum(probabilities)
    population = list(range(0, N + 1))
    return [1] + random.choices(population, probabilities, k=loop*N - 1)