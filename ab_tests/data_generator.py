import numpy as np


def generate_views(mean: int, sigma: float, sample_size: int) -> np.array:
    """Generating views out of lognormal distribution"""
    views = np.random.lognormal(mean, sigma, sample_size).round()

    return views


def generate_ctrs(beta: float, success_rate: float,
                  sample_size: int) -> np.array:
    """
    Generating CTRs out of beta distribution

    We control mean (success rate) and beta, calculating alpha.
    """
    alpha = success_rate * beta / (1 - success_rate)
    ctrs = np.random.beta(alpha, beta, sample_size)

    return ctrs


def generate_clicks(views: np.array, ctr: np.array) -> np.array:
    """Generating clicks using info about views and conversion (CTR)"""
    clicks_list = [np.random.binomial(v, ctr[i]) for i, v in enumerate(views)]

    return np.array(clicks_list)

