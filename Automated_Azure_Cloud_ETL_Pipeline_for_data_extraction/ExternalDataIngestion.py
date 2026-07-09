import os
import json
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

TICKERS = """
COHR LITE SATS CIEN APP TTD DDOG WDAY DELL PLTR
CRWD GDDY SMCI JBL UBER PANW FICO ON PTC NXPI
MPWR TRMB TER TDY TYL ZBRA NOW CDW LDOS JKHY
KEYS FTNT ANET CPAY BR TTWO CDNS IT AMD SNPS
FTV HPE SWKS AVGO GRMN STX LRCX AAPL MSFT NVDA
GOOGL GOOG META ORCL CSCO IBM TXN QCOM AMAT MU
KLAC HPQ NTAP ADBE ADP ADSK ANSS PAYX
"""

BASE_OUTPUT_DIR = Path("./data/external_sources")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

HEADERS = {
    "User-Agent": "NUS ESG Financial Research research@example.com"
}

def save_snapshot(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)

    history = []
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = [history]
        except Exception:
            history = []

    history.append({
        "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": payload
    })

    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def get_sec_ticker_cik_map():
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    raw = response.json()
    return {
        item["ticker"].upper(): str(item["cik_str"]).zfill(10)
        for item in raw.values()
    }


def fetch_sec_companyfacts(ticker, cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    save_snapshot(BASE_OUTPUT_DIR / ticker / "sec_companyfacts.json", response.json())


def fetch_alpha_vantage_company_overview(ticker):
    if not ALPHA_VANTAGE_API_KEY:
        return

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if payload and "Note" not in payload and "Information" not in payload:
        save_snapshot(BASE_OUTPUT_DIR / ticker / "alpha_company_overview.json", payload)


def fetch_alpha_vantage_news_sentiment(ticker):
    if not ALPHA_VANTAGE_API_KEY:
        return

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "limit": 50,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if payload and "feed" in payload:
        save_snapshot(BASE_OUTPUT_DIR / ticker / "alpha_news_sentiment.json", payload)


def run_external_ingestion(raw_tickers):
    tickers = [t.strip().upper() for t in raw_tickers.split() if t.strip()]
    cik_map = get_sec_ticker_cik_map()

    for idx, ticker in enumerate(tickers, start=1):
        print(f"[{idx}/{len(tickers)}] Fetching external data for {ticker}")

        try:
            cik = cik_map.get(ticker)
            if cik:
                fetch_sec_companyfacts(ticker, cik)
                print("SEC companyfacts saved")
            else:
                print("No SEC CIK found")
        except Exception as e:
            print(f"   SEC failed: {e}")

        try:
            fetch_alpha_vantage_company_overview(ticker)
            fetch_alpha_vantage_news_sentiment(ticker)
            if ALPHA_VANTAGE_API_KEY:
                print("Alpha Vantage saved")
            else:
                print("Skipped Alpha Vantage: missing ALPHA_VANTAGE_API_KEY")
        except Exception as e:
            print(f"Alpha Vantage failed: {e}")
            
        time.sleep(0.3)


if __name__ == "__main__":
    run_external_ingestion(TICKERS)