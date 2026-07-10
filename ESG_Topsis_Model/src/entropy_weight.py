import numpy as np
import pandas as pd


def entropy_weight(X):
    X = np.array(X, dtype=float)

    # avoid zero
    X = X + 1e-12
    P = X / X.sum(axis=0)
    n = X.shape[0]
    entropy = (-1 / np.log(n) * np.sum(P * np.log(P), axis=0))
    d = 1 - entropy
    weights = d / d.sum()

    return weights


def save_weights(cols, w):
    pd.DataFrame({"indicator": cols, "weight": w}).to_csv("output/entropy_weights.csv", index=False)
