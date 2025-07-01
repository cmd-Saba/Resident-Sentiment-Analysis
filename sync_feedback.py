import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Setting up Google Sheets 
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Connecting to Google Sheet
SHEET_ID = "1dHS-IZz8BUbnWGlq9jF5-b2QEjZHCNeceTbbaKs-Xv8"  # <-- Replace this
SHEET_NAME = "Form responses 1"  # <-- Replace this if you've renamed it

worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Getting all records as a list of dictionaries
records = worksheet.get_all_records()

# Converting to pandas DataFrame
df = pd.DataFrame(records)


# Save to CSV
df.to_csv("resident_feedback.csv", index=False)

print("Synced latest Google Form responses to resident_feedback.csv")
