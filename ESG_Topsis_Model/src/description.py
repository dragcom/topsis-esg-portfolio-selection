import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Font setting
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["axes.unicode_minus"] = False


# Normalization Function
def minmax_normalize(df, indicators):
    normalized = pd.DataFrame()
    for indicator, direction in indicators.items():
        if indicator not in df.columns:
            continue
        x = pd.to_numeric(df[indicator], errors="coerce")

        # median filling
        x = x.fillna(x.median())
        max_v = x.max()
        min_v = x.min()

        # avoid constant variable
        if max_v == min_v:
            normalized[indicator] = 1
        else:
            if direction == "benefit":
                normalized[indicator] = (x - min_v) / (max_v - min_v)
            else:
                normalized[indicator] = (max_v - x) / (max_v - min_v)
    return normalized


# Boxplot Function
def boxplot_by_dimension(df, indicators, save_path="output/dimension_boxplot.png"):
    # 1. Normalization
    normalized_data = minmax_normalize(df, indicators)

    # 2. Dimension Mapping
    # =========================
    dimension_map = {
        # ESG
        "env_kaggle_score": "Env.",
        "soc_kaggle_score": "Soc.",
        "governance_quality": "Gov.",

        # Financial
        "fin_return_on_equity": "Profit.",
        "fin_return_on_assets": "Profit",
        "fin_profit_margin": "Profit",
        "fin_revenue_growth": "Growth",
        "fin_earnings_growth": "Growth",
        "price_1y_return_pct": "Market",
        "fin_market_cap": "Market",
        "fin_debt_to_equity": "Fin.health",
        "fin_current_ratio": "Fin.health",

        # Risk
        "fin_beta": "Risk",
        "price_30d_volatility_pct": "Risk"
    }

    # 3. Convert long format
    records = []
    for indicator, dimension in dimension_map.items():
        if indicator in normalized_data.columns:
            for value in normalized_data[indicator]:
                records.append(
                    {
                        "Dimension": dimension,
                        "Value": value
                    }
                )
    boxplot_data = pd.DataFrame(records)

    # 4. Order
    dimension_order = [
        "Env.",
        "Soc.",
        "Gov.",
        "Profit.",
        "Growth",
        "Fin.health",
        "Market",
        "Risk"
    ]
    plot_values = []
    labels = []
    for d in dimension_order:
        if d in boxplot_data["Dimension"].unique():
            plot_values.append(boxplot_data[boxplot_data["Dimension"] == d]["Value"])
            labels.append(d)

    # 5. Plot
    plt.figure(figsize=(12, 6))
    plt.boxplot(plot_values, labels=labels, showmeans=True)

    plt.ylabel("Normalized Indicator Values", fontsize=16)
    plt.xlabel("Evaluation Dimensions", fontsize=16)

    plt.title("Normalized Indicator Distribution Across ESG, Financial and Risk Dimensions", fontsize=16)
    plt.xticks(rotation=35, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()

    return boxplot_data


def indicator_dispersion_plot(data, save_path="output/data_dispersion.png"):
    # Indicator name mapping
    indicator_labels = {
        # ESG
        "env_kaggle_score": "Environmental Score",
        "soc_kaggle_score": "Social Score",
        "governance_quality": "Governance Quality",

        # Profitability
        "fin_return_on_equity": "ROE",
        "fin_return_on_assets": "ROA",
        "fin_profit_margin": "Profit Margin",

        # Growth
        "fin_revenue_growth": "Revenue Growth",
        "fin_earnings_growth": "Earnings Growth",

        # Financial Health
        "fin_debt_to_equity": "Debt-to-Equity Ratio",
        "fin_current_ratio": "Current Ratio",

        # Market Performance
        "price_1y_return_pct": "1-Year Stock Return",
        "fin_market_cap": "Market Capitalization",

        # Risk
        "fin_beta": "Beta",
        "price_30d_volatility_pct": "30-Day Volatility"
    }

    # Select indicators
    indicators = [c for c in data.columns if c in indicator_labels.keys()]

    # Calculate CV
    stats = []
    for c in indicators:
        mean = data[c].mean()
        std = data[c].std()
        cv = std / (abs(mean) + 1e-10)
        stats.append([c, mean, std, cv])

    dispersion = pd.DataFrame(
        stats,
        columns=["Indicator", "Mean", "Std", "CV"])

    dispersion = (dispersion.sort_values("CV", ascending=False))

    # Add display names

    dispersion["Indicator_Label"] = (dispersion["Indicator"].map(indicator_labels))

    # Plot
    plt.figure(figsize=(10, 6))

    bars = plt.barh(
        dispersion["Indicator_Label"],
        dispersion["CV"],
        color="#4E79A7"
    )
    # 在柱子末端标记 CV 数值
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 0.02,  # 文字位置（柱子右侧）
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f}",  # 保留两位小数
            va="center",
            ha="left",
            fontsize=16,
            fontname="Times New Roman"
        )

    plt.xlabel("Coefficient of Variation (CV)", fontsize=16)
    # plt.ylabel("Indicators", fontsize=16)
    plt.title("Indicator Dispersion Supporting Entropy-Based Weighting", fontsize=16)

    # highest CV at top
    plt.gca().invert_yaxis()
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
    return dispersion