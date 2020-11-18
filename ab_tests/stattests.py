import numpy as np


def poisson_bootstrap(size: int) -> np.array:
    """
    Poisson bootstrap - generating number of occurences from
    Poisson distribution with lambda = 1 for each sample
    size - sample size
    :return:
    Numpy array of length "size"
    """
    return np.random.poisson(lam=1, size=size)

