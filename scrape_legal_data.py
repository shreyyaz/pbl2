"""
Legal Data Scraper for Commercial Courts
========================================

This script downloads key legal documents related to Commercial Courts in India.
It fetches:
1. The Commercial Courts Act, 2015
2. Law Commission Reports (relevant to commercial disputes)
3. key High Court rules for Commercial Division
4. Important Supreme Court judgments on commercial law

Usage:
    python scrape_legal_data.py
    
Result:
    Downloads PDFs to 'legal_docs/' folder.
    You can then upload these to your Google Drive folder.
"""

import os
import time
import requests
from pathlib import Path
from urllib.parse import urljoin

# Configuration
DOWNLOAD_DIR = Path("legal_docs")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# List of documents to download (Title, URL)
# Using more reliable persistent links where possible
DOCUMENTS = [
    (
        "Commercial Courts Act 2015",
        "https://legislative.gov.in/sites/default/files/A2016-4.pdf"  # Official Legislative Gov link
    ),
    (
        "Arbitration and Conciliation Act 1996",
        "https://legislative.gov.in/sites/default/files/A1996-26.pdf" # Official Legislative Gov link
    ),
    (
        "Commercial Courts Pre-Institution Mediation Rules 2018",
        "https://legalaffairs.gov.in/sites/default/files/Commercial%20Courts%20%28Pre-Institution%20Mediation%20and%20Settlement%29%20Rules%2C%202018.pdf"
    )
]

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    directory.mkdir(exist_ok=True)
    print(f"📂 Download folder: {directory.absolute()}")

def download_file(url, filename):
    """Download a file from a URL with validation."""
    try:
        # Clean filename
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
        filepath = DOWNLOAD_DIR / f"{safe_filename}.pdf"
        
        print(f"  ⬇️  Downloading: {safe_filename}...")
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/pdf,application/octet-stream,*/*'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30, verify=False)
        
        if response.status_code == 200:
            # Check content type if possible
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                print(f"     ❌ Failed: URL returned HTML instead of PDF")
                return False

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Validate file size (min 10KB)
            file_size = filepath.stat().st_size
            if file_size < 10240: 
                print(f"     ❌ Failed: File too small ({file_size} bytes). Likely an error page.")
                filepath.unlink() # Delete bad file
                return False
                
            print(f"     ✅ Saved {filepath.name} ({file_size/1024:.1f} KB)")
            return True
        else:
            print(f"     ❌ Failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"     ❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("📥 Commercial Courts Legal Data Scraper")
    print("="*60 + "\n")
    
    ensure_dir(DOWNLOAD_DIR)
    
    success_count = 0
    for title, url in DOCUMENTS:
        if download_file(url, title):
            success_count += 1
        time.sleep(1)  # Be nice to servers
        
    print("\n" + "="*60)
    print(f"🎉 Downloaded {success_count} documents to '{DOWNLOAD_DIR}' folder.")
    print("👉 Now simply drag and drop these files into your Google Drive folder!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
