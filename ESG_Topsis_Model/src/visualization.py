import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 16


def ranking_plot(df):
    # Sort all companies by final_score descending
    df_sorted = df.sort_values("final_score", ascending=False).copy()

    # Select Top 5 and Bottom 5
    top5 = df_sorted.head(5).copy()
    bottom5 = df_sorted.tail(5).copy()

    # Keep bottom 5 also in descending order
    bottom5 = bottom5.sort_values("final_score", ascending=False)

    # Combine results
    plot_df = pd.concat([top5, bottom5], ignore_index=True)

    # create labels
    labels = plot_df["company"]
    scores = plot_df["final_score"]

    # Plot
    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(plot_df))

    # color assignment
    colors = (["green"] * len(top5) + ["red"] * len(bottom5))
    plt.barh(y_pos, scores, color=colors)
    plt.yticks(y_pos, labels)
    plt.gca().invert_yaxis()
    plt.xlabel("Adjusted TOPSIS Score")
    # plt.title("Top 5 vs Bottom 5 Technology Companies\nBased on Controversy-Adjusted TOPSIS Ranking")

    # add score labels
    for i, score in enumerate(scores):
        plt.text(score + 0.01, i, f"{score:.3f}", va="center", fontsize=16)

    # add separation line
    plt.axhline(y=len(top5) - 0.5, color="black", linestyle="--", linewidth=1)
    plt.tight_layout()
    plt.savefig('output/Top 5 vs Bottom 5 Technology Companies.png',
                dpi=300, bbox_inches="tight")
    plt.show()


def weight_dimension_plot(weight_file="entropy_weights.csv"):
    # Academic Color Palette
    academic_colors = [
        "#009E73",  # Environmental (green)
        "#56B4E9",  # Social (sky blue)
        "#0072B2",  # Governance (blue)
        "#E69F00",  # Profitability (orange)
        "#F0E442",  # Growth (yellow)
        "#CC79A7",  # Market performance (purple)
        "#999999",  # Financial health (grey)
        "#D55E00"  # Risk (red-orange)
    ]

    # Load entropy weights
    weights_df = pd.read_csv(weight_file)

    # Define dimension mapping
    dimension_map = {
        # ESG
        "env_kaggle_score": "Environmental",
        "soc_kaggle_score": "Social",
        "governance_quality": "Governance",

        # Financial
        "fin_return_on_equity": "Profitability",
        "fin_return_on_assets": "Profitability",
        "fin_profit_margin": "Profitability",
        "fin_revenue_growth": "Growth",
        "fin_earnings_growth": "Growth",
        "price_1y_return_pct": "Market performance",
        "fin_market_cap": "Market performance",
        "fin_debt_to_equity": "Financial health",
        "fin_current_ratio": "Financial health",

        # Risk
        "fin_beta": "Risk",
        "price_30d_volatility_pct": "Risk"
    }

    # map dimension
    weights_df["dimension"] = (weights_df["indicator"].map(dimension_map))

    # remove unmatched indicators
    weights_df = weights_df.dropna(subset=["dimension"])

    # aggregate weights
    dimension_weights = (weights_df.groupby("dimension")["weight"].sum())

    # normalize
    dimension_weights = (dimension_weights / dimension_weights.sum())

    # Plot pie chart
    plt.figure(figsize=(7, 7))

    plt.pie(
        dimension_weights.values,
        labels=dimension_weights.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=academic_colors,
        pctdistance=0.75,
        labeldistance=1.08,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
        textprops={"fontsize": 16, "fontname": "Times New Roman"}
    )

    # plt.title("Entropy-Weighted Contribution of ESG, Finance and Risk Dimensions", fontsize=14)
    plt.tight_layout()
    plt.savefig('output/Entropy-Weighted Contribution.png',
                dpi=300, bbox_inches="tight")
    plt.show()

    return dimension_weights
