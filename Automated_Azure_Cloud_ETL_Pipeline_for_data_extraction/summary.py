import argparse
import json
import math
import os
from pathlib import Path
import pandas as pd
import re

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, desc=None, **kwargs):
        if desc:
            print(desc)
        return iterable if iterable is not None else []

    tqdm.write = print


PROJECT_DIR = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_DIR / "data"
HISTORICAL_DIR = DATA_ROOT / "historical_data"
MEDIA_DIR = DATA_ROOT / "media_stream"
SEC_DIR = DATA_ROOT / "sec_data"
DEFAULT_OUTPUT_FILE = DATA_ROOT / "final_esg_financial_dataset.csv"
EXTERNAL_DIR = DATA_ROOT / "external_sources"
KAGGLE_ESG_FILES = [
    DATA_ROOT / "kaggle_esg" / "sp500_esg_data.csv",
    DATA_ROOT / "kaggle_esg" / "SP 500 ESG Risk Ratings.csv",
    DATA_ROOT / "kaggle_esg" / "sp500_esg_ceo_info.csv",
    DATA_ROOT / "kaggle_esg" / "data.csv",
]
MISSING_VALUE = pd.NA


FUNDAMENTAL_FIELDS = {
    # Company profile
    "company_name": "longName",
    "company_short_name": "shortName",
    "sector": "sector",
    "industry": "industry",
    "country": "country",
    "website": "website",
    "exchange": "exchange",
    "currency": "currency",
    "financial_currency": "financialCurrency",
    "full_time_employees": "fullTimeEmployees",
    # Market and valuation
    "fin_market_cap": "marketCap",
    "fin_enterprise_value": "enterpriseValue",
    "fin_beta": "beta",
    "fin_trailing_pe": "trailingPE",
    "fin_forward_pe": "forwardPE",
    "fin_price_to_book": "priceToBook",
    "fin_price_to_sales_ttm": "priceToSalesTrailing12Months",
    "fin_enterprise_to_revenue": "enterpriseToRevenue",
    "fin_enterprise_to_ebitda": "enterpriseToEbitda",
    "fin_book_value_per_share": "bookValue",
    "fin_trailing_eps": "trailingEps",
    "fin_forward_eps": "forwardEps",
    # Profitability and growth
    "fin_total_revenue": "totalRevenue",
    "fin_gross_profit": "grossProfits",
    "fin_net_income_common": "netIncomeToCommon",
    "fin_ebitda": "ebitda",
    "fin_profit_margin": "profitMargins",
    "fin_gross_margin": "grossMargins",
    "fin_ebitda_margin": "ebitdaMargins",
    "fin_operating_margin": "operatingMargins",
    "fin_return_on_assets": "returnOnAssets",
    "fin_return_on_equity": "returnOnEquity",
    "fin_revenue_growth": "revenueGrowth",
    "fin_earnings_growth": "earningsGrowth",
    # Liquidity, leverage, and cash flow
    "fin_total_cash": "totalCash",
    "fin_total_cash_per_share": "totalCashPerShare",
    "fin_total_debt": "totalDebt",
    "fin_debt_to_equity": "debtToEquity",
    "fin_current_ratio": "currentRatio",
    "fin_quick_ratio": "quickRatio",
    "fin_free_cash_flow": "freeCashflow",
    "fin_operating_cash_flow": "operatingCashflow",
    # Dividends and analyst signal
    "fin_dividend_rate": "dividendRate",
    "fin_dividend_yield": "dividendYield",
    "fin_payout_ratio": "payoutRatio",
    "fin_recommendation_mean": "recommendationMean",
    "fin_recommendation_key": "recommendationKey",
    "fin_analyst_opinion_count": "numberOfAnalystOpinions",
    "fin_target_mean_price": "targetMeanPrice",
    # Governance fields available in Yahoo fundamentals
    "gov_audit_risk": "auditRisk",
    "gov_board_risk": "boardRisk",
    "gov_compensation_risk": "compensationRisk",
    "gov_shareholder_rights_risk": "shareHolderRightsRisk",
    "gov_overall_risk": "overallRisk",
}

ESG_FIELDS = {
    "esg_total_score": "totalEsg",
    "env_environment_score": "environmentScore",
    "soc_social_score": "socialScore",
    "gov_governance_score": "governanceScore",
    "esg_peer_group": "peerGroup",
    "esg_rating_year": "ratingYear",
    "esg_rating_month": "ratingMonth",
    "esg_highest_controversy": "highestControversy",
    "esg_percentile": "percentile",
    "env_peer_environment_performance": "peerEnvironmentPerformance",
    "soc_peer_social_performance": "peerSocialPerformance",
    "gov_peer_governance_performance": "peerGovernancePerformance",
}

COLUMN_ORDER = [
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
    "fundamentals_snapshot_count",
    "fundamentals_latest_retrieval_date",
    "esg_snapshot_count",
    "esg_latest_retrieval_date",
    "has_price_history",
    "price_observation_count",
    "price_start_date",
    "price_end_date",
    "price_latest_close",
    "price_latest_volume",
    "price_return_since_start_pct",
    "price_1y_return_pct",
    "price_30d_volatility_pct",
    "has_sec_10k",
    "sec_10k_filing_count",
    "sec_latest_10k_file",
    "sec_latest_10k_size_mb",
    "news_controversy_count",
    "news_latest_published_at",
    "news_latest_headline",
    "news_unique_source_count",
]

def normalize_column_name(column):
    column = str(column).strip()
    column = re.sub(r"(?<!^)(?=[A-Z])", "_", column)
    column = column.lower()
    column = column.replace(" ", "_")
    column = column.replace("-", "_")
    column = column.replace(".", "_")
    column = re.sub(r"_+", "_", column)
    return column.strip("_")

def load_kaggle_esg_lookup():
    lookup = {}

    for file_path in KAGGLE_ESG_FILES:
        if not file_path.exists():
            continue

        df = pd.read_csv(file_path)
        df.columns = [normalize_column_name(c) for c in df.columns]

        ticker_col = next((c for c in df.columns if c in ["ticker", "symbol"]), None)
        if not ticker_col:
            continue

        df[ticker_col] = df[ticker_col].astype(str).str.upper().str.strip()

        source_name = normalize_column_name(file_path.stem)

        for _, row in df.iterrows():
            ticker = row[ticker_col]
            if ticker not in lookup:
                lookup[ticker] = {}

            for col, value in row.to_dict().items():
                if col == ticker_col:
                    continue
                lookup[ticker][f"{source_name}_{col}"] = value

    return lookup


def clean_scalar(value):
    if value is MISSING_VALUE:
        return MISSING_VALUE
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (str, int, float, bool)) and pd.isna(value):
        return MISSING_VALUE
    if value in (None, "", "N/A", "Unknown", "NaN"):
        return MISSING_VALUE
    if isinstance(value, float) and math.isnan(value):
        return MISSING_VALUE
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, ensure_ascii=False)


def read_json(path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        tqdm.write(f"Warning: could not read JSON file {path}: {exc}")
        return None


def latest_snapshot(payload):
    if isinstance(payload, list):
        snapshots = [item for item in payload if isinstance(item, dict)]
        if not snapshots:
            return {}, MISSING_VALUE, 0
        latest = snapshots[-1]
        data = latest.get("data", latest)
        return data if isinstance(data, dict) else {}, latest.get("retrieval_date", MISSING_VALUE), len(snapshots)
    if isinstance(payload, dict):
        return payload.get("data", payload), payload.get("retrieval_date", MISSING_VALUE), 1
    return {}, MISSING_VALUE, 0


def ticker_directories(*roots):
    tickers = set()
    for root in roots:
        if not root.exists():
            continue
        tickers.update(path.name.upper() for path in root.iterdir() if path.is_dir())
    return sorted(tickers)


def add_mapped_fields(record, payload, field_map):
    for output_name, source_name in field_map.items():
        record[output_name] = clean_scalar(payload.get(source_name))


def add_officer_features(record, fundamentals):
    officers = fundamentals.get("companyOfficers")
    if not isinstance(officers, list):
        record["gov_officer_count"] = MISSING_VALUE
        record["gov_ceo_name"] = MISSING_VALUE
        record["gov_ceo_compensation_usd"] = MISSING_VALUE
        return

    record["gov_officer_count"] = len(officers)
    ceo = next(
        (
            officer
            for officer in officers
            if isinstance(officer, dict) and "CEO" in str(officer.get("title", "")).upper()
        ),
        {},
    )
    record["gov_ceo_name"] = clean_scalar(ceo.get("name"))
    record["gov_ceo_compensation_usd"] = clean_scalar(ceo.get("totalPay"))


def add_price_features(record, ticker):
    price_path = HISTORICAL_DIR / ticker / "prices.csv"
    defaults = {
        "has_price_history": "No",
        "price_observation_count": 0,
        "price_start_date": MISSING_VALUE,
        "price_end_date": MISSING_VALUE,
        "price_latest_close": MISSING_VALUE,
        "price_latest_volume": MISSING_VALUE,
        "price_return_since_start_pct": MISSING_VALUE,
        "price_1y_return_pct": MISSING_VALUE,
        "price_30d_volatility_pct": MISSING_VALUE,
    }
    record.update(defaults)

    if not price_path.exists():
        return

    try:
        prices = pd.read_csv(price_path, parse_dates=["Date"])
        prices = prices.dropna(subset=["Date", "Close"]).sort_values("Date")
    except Exception as exc:
        tqdm.write(f"Warning: could not process prices for {ticker}: {exc}")
        return

    if prices.empty:
        return

    closes = prices["Close"].astype(float)
    latest = prices.iloc[-1]
    first_close = closes.iloc[0]
    latest_close = closes.iloc[-1]

    record["has_price_history"] = "Yes"
    record["price_observation_count"] = len(prices)
    record["price_start_date"] = prices["Date"].iloc[0].date().isoformat()
    record["price_end_date"] = latest["Date"].date().isoformat()
    record["price_latest_close"] = latest_close
    record["price_latest_volume"] = clean_scalar(latest.get("Volume"))

    if first_close:
        record["price_return_since_start_pct"] = (latest_close / first_close - 1) * 100

    one_year_cutoff = latest["Date"] - pd.Timedelta(days=365)
    one_year_prices = prices[prices["Date"] >= one_year_cutoff]
    if len(one_year_prices) > 1 and float(one_year_prices["Close"].iloc[0]) != 0:
        record["price_1y_return_pct"] = (
            float(one_year_prices["Close"].iloc[-1]) / float(one_year_prices["Close"].iloc[0]) - 1
        ) * 100

    daily_returns = closes.pct_change().dropna().tail(30)
    if not daily_returns.empty:
        record["price_30d_volatility_pct"] = daily_returns.std() * math.sqrt(252) * 100


def add_sec_features(record, ticker):
    ticker_dir = SEC_DIR / ticker
    filings = []
    if ticker_dir.exists():
        filings = sorted(
            [
                path
                for path in ticker_dir.iterdir()
                if path.is_file() and path.name.lower().startswith("10-k") and path.suffix.lower() in {".txt", ".html"}
            ],
            key=lambda path: path.stat().st_mtime,
        )

    latest = filings[-1] if filings else None
    record["has_sec_10k"] = "Yes" if filings else "No"
    record["sec_10k_filing_count"] = len(filings)
    record["sec_latest_10k_file"] = latest.name if latest else MISSING_VALUE
    record["sec_latest_10k_size_mb"] = round(latest.stat().st_size / (1024 * 1024), 3) if latest else MISSING_VALUE


def add_news_features(record, ticker):
    news_path = MEDIA_DIR / ticker / "news_controversies.json"
    articles = read_json(news_path)
    if not isinstance(articles, list):
        articles = []

    articles = [article for article in articles if isinstance(article, dict)]
    dated_articles = sorted(articles, key=lambda item: str(item.get("published_at") or ""))
    latest = dated_articles[-1] if dated_articles else {}
    sources = {article.get("source") for article in articles if article.get("source")}

    record["news_controversy_count"] = len(articles)
    record["news_latest_published_at"] = clean_scalar(latest.get("published_at"))
    record["news_latest_headline"] = clean_scalar(latest.get("headline"))
    record["news_unique_source_count"] = len(sources)

def latest_external_payload(ticker, filename):
    payload = read_json(EXTERNAL_DIR / ticker / filename)
    data, retrieval_date, count = latest_snapshot(payload)
    return data, retrieval_date, count


def latest_sec_usd_fact(companyfacts, tag):
    try:
        facts = companyfacts["facts"]["us-gaap"][tag]["units"]["USD"]
    except KeyError:
        return MISSING_VALUE

    annual = [
        item for item in facts
        if item.get("form") == "10-K" and item.get("fy") and item.get("val") is not None
    ]

    if not annual:
        annual = [item for item in facts if item.get("val") is not None]

    if not annual:
        return MISSING_VALUE

    latest = sorted(annual, key=lambda x: str(x.get("end", "")))[-1]
    return clean_scalar(latest.get("val"))


def add_external_features(record, ticker):
    sec_facts, sec_date, sec_count = latest_external_payload(ticker, "sec_companyfacts.json")
    record["sec_xbrl_snapshot_count"] = sec_count
    record["sec_xbrl_latest_retrieval_date"] = clean_scalar(sec_date)

    sec_fact_map = {
        "fin_sec_revenue": "Revenues",
        "fin_sec_net_income": "NetIncomeLoss",
        "fin_sec_assets": "Assets",
        "fin_sec_liabilities": "Liabilities",
        "fin_sec_stockholders_equity": "StockholdersEquity",
        "fin_sec_operating_income": "OperatingIncomeLoss",
        "fin_sec_cash": "CashAndCashEquivalentsAtCarryingValue",
        "fin_sec_r_and_d": "ResearchAndDevelopmentExpense",
    }

    for output_col, sec_tag in sec_fact_map.items():
        record[output_col] = latest_sec_usd_fact(sec_facts, sec_tag)

    alpha, alpha_date, alpha_count = latest_external_payload(ticker, "alpha_company_overview.json")
    record["alpha_snapshot_count"] = alpha_count
    record["alpha_latest_retrieval_date"] = clean_scalar(alpha_date)
    record["fin_alpha_market_cap"] = clean_scalar(alpha.get("MarketCapitalization"))
    record["fin_alpha_ebitda"] = clean_scalar(alpha.get("EBITDA"))
    record["fin_alpha_pe_ratio"] = clean_scalar(alpha.get("PERatio"))
    record["fin_alpha_profit_margin"] = clean_scalar(alpha.get("ProfitMargin"))
    record["fin_alpha_operating_margin"] = clean_scalar(alpha.get("OperatingMarginTTM"))
    record["fin_alpha_return_on_equity"] = clean_scalar(alpha.get("ReturnOnEquityTTM"))
    record["fin_alpha_revenue_ttm"] = clean_scalar(alpha.get("RevenueTTM"))
    record["fin_alpha_eps"] = clean_scalar(alpha.get("EPS"))
    record["fin_alpha_dividend_yield"] = clean_scalar(alpha.get("DividendYield"))

    news, news_date, news_count = latest_external_payload(ticker, "alpha_news_sentiment.json")
    feed = news.get("feed", []) if isinstance(news, dict) else []

    record["alpha_news_snapshot_count"] = news_count
    record["alpha_news_latest_retrieval_date"] = clean_scalar(news_date)
    record["alpha_news_article_count"] = len(feed)
    record["alpha_news_avg_sentiment"] = (
        sum(float(item.get("overall_sentiment_score", 0)) for item in feed) / len(feed)
        if feed else MISSING_VALUE
    )


def build_ticker_record(ticker, kaggle_esg_lookup=None):
    record = {"ticker": ticker}

    fundamentals_payload = read_json(HISTORICAL_DIR / ticker / "raw_fundamentals.json")
    fundamentals, fundamentals_date, fundamentals_count = latest_snapshot(fundamentals_payload)
    record["fundamentals_snapshot_count"] = fundamentals_count
    record["fundamentals_latest_retrieval_date"] = clean_scalar(fundamentals_date)
    add_mapped_fields(record, fundamentals, FUNDAMENTAL_FIELDS)
    add_officer_features(record, fundamentals)

    esg_payload = read_json(HISTORICAL_DIR / ticker / "raw_esg_scores.json")
    esg, esg_date, esg_count = latest_snapshot(esg_payload)
    record["esg_snapshot_count"] = esg_count
    record["esg_latest_retrieval_date"] = clean_scalar(esg_date)
    add_mapped_fields(record, esg, ESG_FIELDS)

    add_price_features(record, ticker)
    add_sec_features(record, ticker)
    add_news_features(record, ticker)
    add_external_features(record, ticker)
    
    kaggle_esg_lookup = kaggle_esg_lookup or {}
    kaggle_row = kaggle_esg_lookup.get(ticker, {})

    record["kaggle_esg_available"] = "Yes" if kaggle_row else "No"

    record["esg_kaggle_total_score"] = clean_scalar(
        kaggle_row.get("sp500_esg_data_total_esg")
        or kaggle_row.get("sp_500_esg_risk_ratings_total_esg_risk_score")
        or kaggle_row.get("sp500_esg_ceo_info_esg_score")
        or kaggle_row.get("data_total_score")
    )

    record["env_kaggle_score"] = clean_scalar(
        kaggle_row.get("sp500_esg_data_environment_score")
        or kaggle_row.get("sp_500_esg_risk_ratings_environment_risk_score")
        or kaggle_row.get("sp500_esg_ceo_info_environment_score")
        or kaggle_row.get("data_environment_score")
    )

    record["soc_kaggle_score"] = clean_scalar(
        kaggle_row.get("sp500_esg_data_social_score")
        or kaggle_row.get("sp_500_esg_risk_ratings_social_risk_score")
        or kaggle_row.get("sp500_esg_ceo_info_social_score")
        or kaggle_row.get("data_social_score")
    )

    record["gov_kaggle_score"] = clean_scalar(
        kaggle_row.get("sp500_esg_data_governance_score")
        or kaggle_row.get("sp_500_esg_risk_ratings_governance_risk_score")
        or kaggle_row.get("sp500_esg_ceo_info_governance_score")
        or kaggle_row.get("data_governance_score")
    )

    record["esg_kaggle_rating"] = clean_scalar(
        kaggle_row.get("sp_500_esg_risk_ratings_esg_risk_level")
        or kaggle_row.get("data_total_grade")
        or kaggle_row.get("data_total_level")
    )

    record["esg_kaggle_controversy_score"] = clean_scalar(
        kaggle_row.get("sp_500_esg_risk_ratings_controversy_score")
        or kaggle_row.get("sp500_esg_data_highest_controversy")
    )

    record["gov_kaggle_ceo_name"] = clean_scalar(
        kaggle_row.get("sp500_esg_ceo_info_ceo_full_name")
    )

    record["gov_kaggle_ceo_gender"] = clean_scalar(
        kaggle_row.get("sp500_esg_ceo_info_ceo_gender")
    )
    return record


def ordered_columns(dataframe):
    front = [column for column in COLUMN_ORDER if column in dataframe.columns]
    fin = sorted(column for column in dataframe.columns if column.startswith("fin_") and column not in front)
    env = sorted(column for column in dataframe.columns if column.startswith("env_") and column not in front)
    soc = sorted(column for column in dataframe.columns if column.startswith("soc_") and column not in front)
    gov = sorted(column for column in dataframe.columns if column.startswith("gov_") and column not in front)
    esg = sorted(column for column in dataframe.columns if column.startswith("esg_") and column not in front)
    remaining = sorted(
        column
        for column in dataframe.columns
        if column not in set(front + fin + env + soc + gov + esg)
    )
    return front + fin + env + soc + gov + esg + remaining


def build_final_csv(output_file=DEFAULT_OUTPUT_FILE):
    tickers = ticker_directories(HISTORICAL_DIR, MEDIA_DIR, SEC_DIR, EXTERNAL_DIR)
    if not tickers:
        raise FileNotFoundError(
            f"No ticker folders found under {HISTORICAL_DIR}, {MEDIA_DIR}, {SEC_DIR}, or {EXTERNAL_DIR}."
        )

    kaggle_esg_lookup = load_kaggle_esg_lookup()

    records = [
        build_ticker_record(ticker, kaggle_esg_lookup)
        for ticker in tqdm(tickers, desc="Building final ESG/financial CSV")
    ]

    dataframe = pd.DataFrame(records)

    has_any_data = (
        (dataframe["fundamentals_snapshot_count"] > 0)
        | (dataframe["esg_snapshot_count"] > 0)
        | (dataframe["has_price_history"] == "Yes")
        | (dataframe["has_sec_10k"] == "Yes")
        | (dataframe["news_controversy_count"] > 0)
        | (dataframe["sec_xbrl_snapshot_count"] > 0)
        | (dataframe["alpha_snapshot_count"] > 0)
        | (dataframe["alpha_news_snapshot_count"] > 0)
        | (dataframe["kaggle_esg_available"] == "Yes")
    )

    dataframe = dataframe[has_any_data]
    dataframe = dataframe[ordered_columns(dataframe)].sort_values("ticker")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)

    print(f"\nFinal dataset written to: {output_path}")
    print(f"Rows: {len(dataframe)}")
    print(f"Columns: {len(dataframe.columns)}")
    print(f"Tickers with fundamentals: {(dataframe['fundamentals_snapshot_count'] > 0).sum()}")
    print(f"Tickers with price history: {(dataframe['has_price_history'] == 'Yes').sum()}")
    print(f"Tickers with SEC 10-K files: {(dataframe['has_sec_10k'] == 'Yes').sum()}")
    print(f"Tickers with Kaggle ESG data: {(dataframe['kaggle_esg_available'] == 'Yes').sum()}")
    print(f"Total news controversy records: {int(dataframe['news_controversy_count'].sum())}")

    return dataframe


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create one high-quality CSV from historical, media, and SEC ingestion outputs."
    )
    parser.add_argument(
        "--output",
        default=os.environ.get("FINAL_DATASET_OUTPUT", str(DEFAULT_OUTPUT_FILE)),
        help="Path for the final consolidated CSV.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_final_csv(args.output)
