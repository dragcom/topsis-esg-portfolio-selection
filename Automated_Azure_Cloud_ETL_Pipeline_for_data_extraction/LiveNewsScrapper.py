import os
import json
import time
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
if not API_KEY:
    raise ValueError("CRITICAL: NEWS_API_KEY not found in environment or .env file!")

NEWS_ENGINE = NewsApiClient(api_key=API_KEY) 

RAW_PASTED_TICKERS = """
COHR LITE SATS CIEN APP TTD DDOG WDAY DELL PLTR 
CRWD GDDY SMCI JBL UBER PANW FICO ON PTC NXPI 
MPWR TRMB TER TDY TYL ZBRA NOW CDW LDOS JKHY 
KEYS FTNT ANET CPAY BR TTWO CDNS IT AMD SNPS 
FTV HPE SWKS AVGO GRMN STX LRCX AAPL MSFT NVDA 
GOOGL GOOG META ORCL CSCO IBM TXN QCOM AMAT MU 
KLAC HPQ NTAP ADBE ADP ADSK ANSS PAYX
"""

BASE_OUTPUT_DIR = "./data/media_stream"

def ingest_and_save_controversies(raw_input_text, output_dir="./data/media_stream"):
    tickers, name_map = clean_and_map_tickers(raw_input_text)
    
    for idx, ticker in enumerate(tickers):
        company_name = name_map[ticker]
        ticker_target_dir = os.path.join(output_dir, ticker)
        os.makedirs(ticker_target_dir, exist_ok=True)
        json_file_path = os.path.join(ticker_target_dir, "news_controversies.json")
        
        # 1. Load existing historical archive if it exists
        existing_alerts = []
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as f:
                try:
                    existing_alerts = json.load(f)
                except json.JSONDecodeError:
                    existing_alerts = []
        
        # Create a set of URLs already in our archive to prevent duplicates
        existing_urls = {alert.get("url") for alert in existing_alerts}
        
        # 2. Query NewsAPI
        try:
            search_query = f'"{company_name}" AND (fine OR lawsuit OR settlement OR "class action" OR investigation)'
            raw_articles = NEWS_ENGINE.get_everything(q=search_query, language='en', sort_by='relevancy', page_size=5)
            
            new_count = 0
            if raw_articles.get('status') == 'ok':
                for art in raw_articles['articles']:
                    url = art['url']
                    if url not in existing_urls:
                        existing_alerts.append({
                            "source": art['source']['name'],
                            "author": art.get('author'),
                            "headline": art['title'],
                            "description": art.get('description'),
                            "url": url,
                            "published_at": art.get('publishedAt')
                        })
                        new_count += 1
            
            # 3. Write back to disk (Historical + New)
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(existing_alerts, f, indent=4, ensure_ascii=False)
                
            print(f"[{ticker}] Accumulated {new_count} new alerts. Total: {len(existing_alerts)}")
            
        except Exception as e:
            print(f"Media extraction hit an exception for {ticker}: {e}")
            
        time.sleep(1.0)

def clean_and_map_tickers(raw_text):
    clean_tickers = [t.strip().upper() for t in raw_text.replace(",", " ").split() if t.strip()]
    return clean_tickers, {t: t for t in clean_tickers}

if __name__ == "__main__":
    ingest_and_save_controversies(RAW_PASTED_TICKERS, BASE_OUTPUT_DIR)