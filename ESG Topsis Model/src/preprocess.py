import pandas as pd
import numpy as np


def preprocess_data(path):
    df = pd.read_excel(path)
    df["company"] = df["company_short_name"]

    # Governance Quality
    gov_cols = [
        "gov_board_risk",
        "gov_audit_risk",
        "gov_compensation_risk",
        "gov_shareholder_rights_risk"
    ]

    df["governance_quality"] = (1 - df[gov_cols].mean(axis=1) / 10)

    # Indicators
    indicators = {
        # ESG
        "env_kaggle_score": "benefit",
        "soc_kaggle_score": "benefit",
        "governance_quality": "benefit",

        # Profitability
        "fin_return_on_equity": "benefit",
        "fin_return_on_assets": "benefit",
        "fin_profit_margin": "benefit",

        # Growth
        "fin_revenue_growth": "benefit",
        "fin_earnings_growth": "benefit",

        # Financial health
        "fin_debt_to_equity": "cost",
        "fin_current_ratio": "benefit",

        # Market performance
        "price_1y_return_pct": "benefit",
        "fin_market_cap": "benefit",

        # Risk
        "fin_beta": "cost",
        "price_30d_volatility_pct": "cost"
    }

    selected = []
    for c in indicators:
        if c in df.columns:
            selected.append(c)
    data = df[["company"] + selected + ["news_controversy_count"] + ["news_unique_source_count"]].copy()

    # Numeric conversion
    for c in selected:
        data[c] = pd.to_numeric(data[c], errors="coerce")

        # median fill
        data[c] = (data[c].fillna(data[c].median()))

    data["news_controversy_count"] = (data["news_controversy_count"].fillna(0))
    data["news_unique_source_count"] = (data["news_unique_source_count"].fillna(0))

    return data, indicators
