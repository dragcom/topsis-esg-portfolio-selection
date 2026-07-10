import pandas as pd

from src.preprocess import preprocess_data
from src.entropy_weight import entropy_weight, save_weights
from src.topsis_model import normalize, topsis
from src.controversy_adjustment import adjust_by_controversy
from src.visualization import ranking_plot, weight_dimension_plot
from src.sensitivity_analysis import controversy_sensitivity, plot_lambda_sensitivity

df, indicators = preprocess_data("data/dataset.xlsx")

criteria = list(indicators.keys())

criteria = [c for c in criteria if c in df.columns]

directions = [indicators[c] for c in criteria]

X = df[criteria].values

# normalization
X_norm = normalize(X, directions)

print("NaN after normalization:", pd.DataFrame(X_norm).isna().sum().sum())

# entropy
weights = entropy_weight(X_norm)
save_weights(criteria, weights)

# topsis
score = topsis(X_norm, weights)
df["topsis_score"] = score

# controversy penalty
final_score, penalty, intensity = adjust_by_controversy(
    df["topsis_score"],
    df["news_controversy_count"],
    df["news_unique_source_count"],
    lam=0.25
)
df["penalty"] = penalty
df["final_score"] = final_score
result = df.sort_values("final_score", ascending=False)
result["rank"] = range(1, len(result) + 1)

result.to_csv("output/final_ranking.csv", index=False)
print(result.head(10))

# visualization
ranking_plot(result)
dimension_weights = weight_dimension_plot("output/entropy_weights.csv")

# Sensitivity Analysis
sensitivity_result = controversy_sensitivity(result,
                                             lambda_values=[0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40])

sensitivity_result.to_csv("output/lambda_sensitivity.csv", index=False)

plot_lambda_sensitivity(sensitivity_result, top_n=5)

