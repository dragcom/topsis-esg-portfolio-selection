import numpy as np


def normalize(X, directions):
    X = np.array(X, dtype=float)
    result = np.zeros_like(X)
    for i, d in enumerate(directions):
        col = X[:, i]
        max_v = col.max()
        min_v = col.min()
        if max_v == min_v:
            result[:, i] = 1
            continue
        if d == "benefit":
            result[:, i] = (col - min_v) / (max_v - min_v)
        else:
            result[:, i] = (max_v - col) / (max_v - min_v)

    return result + 1e-10


def topsis(X, w):
    V = X * w
    best = V.max(axis=0)
    worst = V.min(axis=0)
    d1 = np.sqrt(((V - best) ** 2).sum(axis=1))
    d2 = np.sqrt(((V - worst) ** 2).sum(axis=1))
    score = d2 / (d1 + d2)
    return score
