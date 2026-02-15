"""
Google Drive Sync for AI Research Engine
=========================================

This script syncs PDF files from a Google Drive folder to your local data folder.
New files added to Google Drive will automatically be downloaded and indexed.

Setup:
1. Create a Google Cloud project and enable Drive API
2. Download credentials.json and place in project root
3. Share your Drive folder with the service account email
4. Set GOOGLE_DRIVE_FOLDER_ID in .env
"""

import os
import io
import pickle
from pathlib import Path
from dotenv import load_dotenv

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️  Google Drive libraries not installed. Run: pip install google-api-python-client google-auth-oauthlib")

load_dotenv()

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DATA_DIR = Path("data")
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"


def get_drive_service():
    """Authenticate and return Google Drive service."""
    creds = None
    
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ {CREDENTIALS_FILE} not found!")
                print("   Download it from Google Cloud Console")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for future use
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)


def list_pdfs_in_folder(service, folder_id):
    """List all PDF files in a Google Drive folder."""
    query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    
    results = service.files().list(
        q=query,
        pageSize=1000,
        fields="files(id, name, modifiedTime)"
    ).execute()
    
    return results.get('files', [])


def download_pdf(service, file_id, file_name, destination_folder):
    """Download a PDF file from Google Drive."""
    destination = destination_folder / file_name
    
    # Skip if already exists (can add modified time check for updates)
    if destination.exists():
        return False
    
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    destination.write_bytes(fh.getvalue())
    return True


def sync_from_drive(folder_id=None):
    """Sync all PDFs from Google Drive folder to local data folder."""
    if not GOOGLE_AVAILABLE:
        print("❌ Google Drive libraries not installed")
        return 0
    
    folder_id = folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    
    if not folder_id:
        print("❌ GOOGLE_DRIVE_FOLDER_ID not set in .env")
        return 0
    
    print("\n🔄 Syncing from Google Drive...")
    
    service = get_drive_service()
    if not service:
        return 0
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # List and download PDFs
    files = list_pdfs_in_folder(service, folder_id)
    print(f"📂 Found {len(files)} PDF(s) in Drive folder")
    
    new_count = 0
    for file in files:
        if download_pdf(service, file['id'], file['name'], DATA_DIR):
            print(f"  ✅ Downloaded: {file['name']}")
            new_count += 1
        else:
            print(f"  ⏭️  Skipped (exists): {file['name']}")
    
    print(f"\n📊 Sync complete: {new_count} new file(s) downloaded")
    return new_count


def setup_drive_folder():
    """Interactive setup for Google Drive folder."""
    print("\n" + "="*50)
    print("🗂️  Google Drive Setup")
    print("="*50)
    print("""
Steps to set up Google Drive sync:

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "Google Drive API"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json to project folder
6. Create a folder in Google Drive for your PDFs
7. Copy the folder ID from the URL:
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
8. Add to .env:
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here

Then run: python drive_sync.py
""")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_drive_folder()
    else:
        new_files = sync_from_drive()
        
        if new_files > 0:
            print("\n💡 New files downloaded! Run 'python app.py' to rebuild the index.")
            print("   (Delete 'vector_store/' folder first to force rebuild)")
