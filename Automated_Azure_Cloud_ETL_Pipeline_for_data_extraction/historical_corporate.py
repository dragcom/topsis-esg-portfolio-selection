import os
import json
import time
from datetime import datetime
import requests
import pandas as pd
import yfinance as yf
from yahooquery import Ticker as YQ_Ticker
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def build_safe_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return session

def append_json_snapshot(file_path, new_payload):
    """
    Saves point-in-time metrics by appending them into a chronological tracking list
    rather than destroying past corporate entries.
    """
    history_records = []
    
    # 1. Pull the historical array forward if it exists
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history_records = json.load(f)
                if not isinstance(history_records, list):
                    # Fallback structural adjustment if the old file was a plain dictionary
                    history_records = [history_records]
        except Exception:
            history_records = []

    # 2. Add retrieval timestamp to track data trends
    snapshot = {
        "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": new_payload
    }
    history_records.append(snapshot)
    
    # 3. Stream back to disk safely
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history_records, f, indent=4, ensure_ascii=False)

def run_bulk_raw_extractor(ticker_list, start_date, end_date, output_dir="./data/historical_data"):
    session = build_safe_session()
    
    print(f"Executing batch price history download for {len(ticker_list)} assets...")
    historical_prices = yf.download(
        ticker_list, start=start_date, end=end_date, group_by='ticker', session=session, threads=True
    )
    
    for idx, ticker_symbol in enumerate(ticker_list):
        print(f"[{idx + 1}/{len(ticker_list)}] Processing accumulation streams for: {ticker_symbol}")
        
        ticker_dir = os.path.join(output_dir, ticker_symbol)
        os.makedirs(ticker_dir, exist_ok=True)
        
        try:
            if ticker_symbol in historical_prices.columns.levels[0]:
                ticker_prices = historical_prices[ticker_symbol].dropna(subset=['Close'])
                price_path = os.path.join(ticker_dir, "prices.csv")
                
                if os.path.exists(price_path):
                    # Load existing pricing tracker to pinpoint chronological cutoff
                    existing_df = pd.read_csv(price_path, index_col=0, parse_dates=True)
                    if not existing_df.empty:
                        last_saved_date = existing_df.index.max()
                        # Isolate only truly new chronological entries
                        ticker_prices.index = pd.to_datetime(ticker_prices.index)
                        new_rows = ticker_prices[ticker_prices.index > last_saved_date]
                        
                        if not new_rows.empty:
                            new_rows.to_csv(price_path, mode='a', header=False)
                            print(f"Appended {len(new_rows)} new day rows to: {price_path}")
                        else:
                            print(f"Price matrix already up-to-date for {ticker_symbol}.")
                else:
                    # Create if base file doesn't exist yet
                    ticker_prices.to_csv(price_path)
                    print(f"Base Build Complete: {price_path}")
        except Exception as e:
            print(f"Could not isolate or merge price slice for {ticker_symbol}: {e}")
            
        # --- B. Append Raw Fundamentals Snapshot (JSON) ---
        try:
            yf_asset = yf.Ticker(ticker_symbol, session=session)
            raw_info = yf_asset.info if yf_asset.info else {}
            
            if raw_info:
                info_path = os.path.join(ticker_dir, "raw_fundamentals.json")
                append_json_snapshot(info_path, raw_info)
                print(f"Logged Fundamentals snapshot to: {info_path}")
            else:
                print(f"No fundamentals payload found for {ticker_symbol}")
        except Exception as e:
            print(f"Fundamentals update skipped for {ticker_symbol}: {e}")
            
        # --- C. Append Raw ESG Scores Snapshot (JSON) ---
        try:
            yq_asset = YQ_Ticker(ticker_symbol, session=session)
            raw_esg_payload = yq_asset.esg_scores
            
            if ticker_symbol in raw_esg_payload and isinstance(raw_esg_payload[ticker_symbol], dict):
                ticker_raw_esg = raw_esg_payload[ticker_symbol]
                esg_path = os.path.join(ticker_dir, "raw_esg_scores.json")
                
                append_json_snapshot(esg_path, ticker_raw_esg)
                print(f"Logged ESG snapshot to: {esg_path}")
            else:
                print(f"No ESG payload structured for {ticker_symbol}")
        except Exception as e:
            print(f"ESG update skipped for {ticker_symbol}: {e}")

        time.sleep(1.0)

if __name__ == "__main__":
    TEST_TICKERS = """
    COHR LITE SATS CIEN APP TTD DDOG WDAY DELL PLTR 
    CRWD GDDY SMCI JBL UBER PANW FICO ON PTC NXPI 
    MPWR TRMB TER TDY TYL ZBRA NOW CDW LDOS JKHY 
    KEYS FTNT ANET CPAY BR TTWO CDNS IT AMD SNPS 
    FTV HPE SWKS AVGO GRMN STX LRCX AAPL MSFT NVDA 
    GOOGL GOOG META ORCL CSCO IBM TXN QCOM AMAT MU 
    KLAC HPQ NTAP ADBE ADP ADSK ANSS PAYX
    """
    target_portfolio = [t.strip().upper() for t in TEST_TICKERS.split() if t.strip()]
    
    run_bulk_raw_extractor(
        ticker_list=target_portfolio, 
        start_date="2016-01-01", 
        end_date="2026-07-09",
        output_dir="./data/historical_data"
    )
    print("\n Historical and Corporate Data downloaded successfully.")