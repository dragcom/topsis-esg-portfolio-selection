import numpy as np


def adjust_by_controversy(topsis_score, controversy_count, source_count, lam=0.25):
    # 1. Calculate Controversy Intensity
    controversy_count = np.array(controversy_count, dtype=float)
    source_count = np.array(source_count, dtype=float)
    controversy_intensity = (controversy_count / (source_count + 1))

    # 2. Normalize intensity
    CI_min = controversy_intensity.min()
    CI_max = controversy_intensity.max()
    if CI_max == CI_min:
        P = np.zeros_like(controversy_intensity)
    else:
        P = (controversy_intensity - CI_min) / (CI_max - CI_min)

    # 3. Apply penalty
    final_score = (np.array(topsis_score)*(1 - lam * P))
    return final_score, P, controversy_intensity