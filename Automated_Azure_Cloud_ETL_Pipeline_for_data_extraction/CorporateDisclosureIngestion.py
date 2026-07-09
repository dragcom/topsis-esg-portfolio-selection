import os
import time
import shutil
from sec_edgar_downloader import Downloader

TICKERS = """
COHR LITE SATS CIEN APP TTD DDOG WDAY DELL PLTR 
CRWD GDDY SMCI JBL UBER PANW FICO ON PTC NXPI 
MPWR TRMB TER TDY TYL ZBRA NOW CDW LDOS JKHY 
KEYS FTNT ANET CPAY BR TTWO CDNS IT AMD SNPS 
FTV HPE SWKS AVGO GRMN STX LRCX AAPL MSFT NVDA 
GOOGL GOOG META ORCL CSCO IBM TXN QCOM AMAT MU 
KLAC HPQ NTAP ADBE ADP ADSK ANSS PAYX
"""

TEMP_LOCAL_DIR = "./sec_raw_data"
BASE_OUTPUT_DIR = "./data/sec_data"

def download_and_local_save_pipeline(raw_input_text, temp_folder, output_folder):
    """
    Downloads SEC filings, extracts the primary document, and accumulates them 
    chronologically by accession number into per-ticker directories without overwriting.
    """
    # Clean and parse ticker text
    ticker_list = [t.strip().upper() for t in raw_input_text.replace(",", " ").split() if t.strip()]
    
    # SEC Compliance Identities (Required by SEC EDGAR)
    automated_identity = "DataPipelineEngine research@pipeline.internal"
    automated_email = "research@pipeline.internal"
    
    dl = Downloader(automated_identity, automated_email, temp_folder)
    print(f"🚀 Initializing Partitioned SEC Accumulation Engine for {len(ticker_list)} companies...")
    print(f"📁 Root Destination: {output_folder}\n")
    
    for idx, ticker in enumerate(ticker_list):
        print(f"[{idx + 1}/{len(ticker_list)}] Fetching 10-K raw document for: {ticker}")
        
        # Define and establish the dedicated raw storage folder for this specific ticker
        ticker_target_dir = os.path.join(output_folder, ticker)
        os.makedirs(ticker_target_dir, exist_ok=True)
        
        try:
            # Download the most recent 10-K filing to temporary scratchpad
            # Note: If you want to build historical history backwards, increase the limit (e.g., limit=5)
            dl.get("10-K", ticker, limit=1, download_details=False)
            
            ticker_filing_path = os.path.join(temp_folder, "sec-edgar-filings", ticker, "10-K")
            
            if os.path.exists(ticker_filing_path):
                file_found = False
                
                # Crawl the nested EDGAR folders to locate the true raw filing document
                for root, dirs, files in os.walk(ticker_filing_path):
                    for file in files:
                        if file.endswith((".txt", ".html")):
                            file_found = True
                            full_file_path = os.path.join(root, file)
                            
                            # Extract the SEC accession number from the path directory name
                            # Path pattern: .../10-K/{ACCESSION_NUMBER}/full-submission.txt
                            accession_number = os.path.basename(root)
                            
                            # If for some reason basename fails to yield the ID, fall back to timestamp
                            if not accession_number or accession_number == "10-K":
                                accession_number = str(int(time.time()))
                            
                            # Preserve file type extension (.html or .txt)
                            ext = os.path.splitext(file)[1]
                            
                            # DYNAMIC FILENAME: Incorporates unique SEC ID to prevent overwriting
                            destination_filename = f"10-K_{accession_number}{ext}"
                            destination_path = os.path.join(ticker_target_dir, destination_filename)
                            
                            # Check if we already have this exact filing saved
                            if os.path.exists(destination_path):
                                print(f"Filing {destination_filename} already archived for {ticker}. Skipping copy.")
                            else:
                                # Move and rename into the ticker's specific data folder
                                shutil.copy2(full_file_path, destination_path)
                                file_size_mb = os.path.getsize(destination_path) / (1024 * 1024)
                                print(f"Accumulated: {ticker}/{destination_filename} ({file_size_mb:.2f} MB)")
                
                if not file_found:
                    print(f"SEC directory generated, but no raw text/html files found.")
            else:
                print(f"SEC did not yield data for {ticker} (Invalid asset or missing filing).")
            
            # Clean up the specific ticker's temp raw workspace immediately
            specific_ticker_dir = os.path.join(temp_folder, "sec-edgar-filings", ticker)
            if os.path.exists(specific_ticker_dir):
                shutil.rmtree(specific_ticker_dir)
                
        except Exception as e:
            print(f"Pipeline break encountered for {ticker}: {e}")
        
        # Polite throttling gap for SEC rate limit constraints
        if idx < len(ticker_list) - 1:
            time.sleep(1.0)

    # Wipe the temporary scratch folder completely clean
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
        
    print(f"\nPartitioned accumulation sequence completed. Check your '{output_folder}' directory folders.")

if __name__ == "__main__":
    download_and_local_save_pipeline(TICKERS, TEMP_LOCAL_DIR, BASE_OUTPUT_DIR)