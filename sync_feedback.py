import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = None
    
    try:
        if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
            import json
            creds_dict = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        elif os.path.exists("credentials.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        else:
            logging.error("credentials.json not found! Please place your Google Service Account credentials file in the project root or set GOOGLE_CREDENTIALS_JSON env var.")
            sys.exit(1)
            
        client = gspread.authorize(creds)
    except Exception as e:
        logging.error(f"Failed to authorize with Google Sheets: {e}")
        sys.exit(1)

    # Connecting to Google Sheet
    SHEET_ID = "1dHS-IZz8BUbnWGlq9jF5-b2QEjZHCNeceTbbaKs-Xv8"  # <-- Replace this
    SHEET_NAME = "Form responses 1"  # <-- Replace this if you've renamed it

    try:
        worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        # Getting all records as a list of dictionaries
        records = worksheet.get_all_records()
    except Exception as e:
        logging.error(f"Failed to fetch data from Google Sheets: {e}")
        sys.exit(1)

    if not records:
        logging.warning("No records found in the Google Sheet.")
        sys.exit(0)

    # Converting to pandas DataFrame
    df = pd.DataFrame(records)

    try:
        # Save to CSV
        df.to_csv("resident_feedback.csv", index=False)
        logging.info("Synced latest Google Form responses to resident_feedback.csv")
    except Exception as e:
        logging.error(f"Failed to save to CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
