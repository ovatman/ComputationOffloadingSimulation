import numpy as np


def get_distribution(distr, params, size=100):
    if distr == "lognormal":
        return list(np.random.lognormal(params[0], params[1], size))
    if distr == "zipf":
        return list(np.random.zipf(params[0], size))
    if distr == "powerlaw":
        return list(np.random.power(params[0], size))
    if distr == "pareto":
        return list(np.random.pareto(params[0], size))
    else:
        return list(np.random.uniform(0., 1., size))
