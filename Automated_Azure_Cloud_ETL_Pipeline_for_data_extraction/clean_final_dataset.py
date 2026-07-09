from pathlib import Path
import pandas as pd
INPUT_FILE = Path("./data/final_esg_financial_dataset.csv")
OUTPUT_FILE = Path("./data/final_esg_financial_dataset_cleaned.csv")

MISSING_TOKENS = [
    "",
    "N/A",
    "NA",
    "NaN",
    "nan",
    "None",
    "null",
    "Unknown",
    "UNKNOWN",
    "-",
]

def clean_numeric_column(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def main():
    df = pd.read_csv(INPUT_FILE)

    # 1. Remove duplicate tickers
    df = df.drop_duplicates(subset=["ticker"], keep="last")

    # 2. Standardize ticker formatting
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()

    # 3. Standardize missing values
    df = df.replace(MISSING_TOKENS, pd.NA)
    df = df.dropna(axis=1, how="all")

    # 4. Convert likely numeric columns
    non_numeric_columns = {
        "ticker",
        "company_name",
        "company_short_name",
        "sector",
        "industry",
        "country",
        "website",
        "exchange",
        "currency",
        "financial_currency",
        "fundamentals_latest_retrieval_date",
        "esg_latest_retrieval_date",
        "price_start_date",
        "price_end_date",
        "has_price_history",
        "has_sec_10k",
        "sec_latest_10k_file",
        "news_latest_published_at",
        "news_latest_headline",
        "fin_recommendation_key",
        "gov_ceo_name",
        "esg_peer_group",
        "alpha_latest_retrieval_date",
        "alpha_news_latest_retrieval_date",
        "sec_xbrl_latest_retrieval_date",
    }

    for col in df.columns:
        if col not in non_numeric_columns:
            converted = clean_numeric_column(df[col])
            if converted.notna().sum() > 0:
                df[col] = converted

    # 5. Remove companies with no useful data
    useful_data_cols = [
        "fundamentals_snapshot_count",
        "esg_snapshot_count",
        "price_observation_count",
        "sec_10k_filing_count",
        "news_controversy_count",
        "alpha_snapshot_count",
        "alpha_news_snapshot_count",
        "sec_xbrl_snapshot_count",
    ]

    useful_data_cols = [col for col in useful_data_cols if col in df.columns]

    df = df[df[useful_data_cols].fillna(0).sum(axis=1) > 0]

    # 6. Add quality flags
    fin_total_revenue = df["fin_total_revenue"] if "fin_total_revenue" in df.columns else pd.Series(pd.NA, index=df.index)
    fin_sec_revenue = df["fin_sec_revenue"] if "fin_sec_revenue" in df.columns else pd.Series(pd.NA, index=df.index)
    fin_market_cap = df["fin_market_cap"] if "fin_market_cap" in df.columns else pd.Series(pd.NA, index=df.index)
    df["quality_has_financials"] = (
		fin_total_revenue.notna()
		| fin_sec_revenue.notna()
		| fin_market_cap.notna()
	)

    df["quality_has_price_history"] = df.get("price_observation_count", 0).fillna(0) > 0

    sec_10k_count = df["sec_10k_filing_count"] if "sec_10k_filing_count" in df.columns else pd.Series(0, index=df.index)
    sec_xbrl_count = df["sec_xbrl_snapshot_count"] if "sec_xbrl_snapshot_count" in df.columns else pd.Series(0, index=df.index)
    df["quality_has_sec_data"] = (
		(sec_10k_count.fillna(0) > 0)
		| (sec_xbrl_count.fillna(0) > 0)
	)

    df["quality_has_esg_data"] = (
        df.filter(regex="^(env_|soc_|gov_|esg_)").notna().sum(axis=1) > 0
    )

    df["quality_non_null_column_count"] = df.notna().sum(axis=1)

    df["quality_completeness_pct"] = (
        df.notna().sum(axis=1) / len(df.columns) * 100
    ).round(2)

    # 7. Remove rows with extremely weak data
    df = df[
        df["quality_has_financials"]
        | df["quality_has_price_history"]
        | df["quality_has_sec_data"]
    ]

    # 8. Sort columns and rows
    df = df.sort_values(["sector", "ticker"], na_position="last")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned dataset saved to: {OUTPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Average completeness: {df['quality_completeness_pct'].mean():.2f}%")


if __name__ == "__main__":
    main()