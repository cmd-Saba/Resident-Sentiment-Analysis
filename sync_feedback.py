import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# STEP 1: Set up Google Sheets API access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# STEP 2: Connect to your Google Sheet
SHEET_ID = "1dHS-IZz8BUbnWGlq9jF5-b2QEjZHCNeceTbbaKs-Xv8"  # <-- Replace this
SHEET_NAME = "Form responses 1"  # <-- Replace this if you've renamed it

worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# STEP 3: Get all records as a list of dictionaries
records = worksheet.get_all_records()

# STEP 4: Convert to pandas DataFrame
df = pd.DataFrame(records)

# (Optional) Rename columns if needed
# df.rename(columns={"Your Name": "Full Name", "Your Feedback": "Feedback", ...}, inplace=True)

# STEP 5: Save to CSV
df.to_csv("resident_feedback.csv", index=False)

print("✅ Synced latest Google Form responses to resident_feedback.csv")
