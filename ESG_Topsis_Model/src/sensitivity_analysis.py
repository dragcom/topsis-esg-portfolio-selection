import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def controversy_sensitivity(df, lambda_values=None):
    if lambda_values is None:
        lambda_values = np.arange(0.1, 0.41, 0.05)

    results = []

    for lam in lambda_values:
        temp = df.copy()

        # Adjusted score
        temp["adjusted_score"] = (temp["topsis_score"]*(1 - lam *temp["penalty"]))

        # Ranking
        temp["rank"] = (temp["adjusted_score"].rank(ascending=False, method="min"))
        temp["lambda"] = lam
        results.append(temp[["company", "adjusted_score", "rank", "lambda"]])

    sensitivity_df = pd.concat(results, ignore_index=True)
    return sensitivity_df


def plot_lambda_sensitivity(sensitivity_df, top_n=5):
    plt.figure(figsize=(10, 6))

    # select top companies under baseline lambda
    baseline = (sensitivity_df[sensitivity_df["lambda"] == 0.25].sort_values("rank").head(top_n))
    companies = baseline["company"]
    for company in companies:
        temp = sensitivity_df[sensitivity_df["company"] == company]
        plt.plot(temp["lambda"], temp["rank"], marker="o", label=company)
    plt.gca().invert_yaxis()
    plt.xlabel("Controversy Penalty Parameter λ")
    plt.ylabel("Investment Rank")
    plt.title("Sensitivity Analysis of Controversy Penalty")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig('output/Sensitivity Analysis of Controversy Penalty.png',
                dpi=300, bbox_inches="tight")
    plt.show()