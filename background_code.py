import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

class BackgroundCode:

    def __init__(self):
        # to be completed
        
        pass
    
    def load_Gsheets(self, Gsheet_ID="1Hc45UijRaTwziEYwK2mXAWz4KTwWoOatef77_K4mSHg"):
        # Load service account info securely from Streamlit secrets
        
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=SCOPES)
        gc = gspread.authorize(creds)

        spreadsheet = gc.open_by_key(Gsheet_ID)

        return spreadsheet



    def get_sheet_dataframe(self, sheet_name, sheet):
        """Read a worksheet into a DataFrame."""
        try:
            worksheet = sheet.worksheet(sheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except gspread.WorksheetNotFound:
            st.warning(f"Worksheet '{sheet_name}' not found.")
            return pd.DataFrame()