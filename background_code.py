# Written by: Michael Jenks
# Last update: 24/11/2025

import gspread

import streamlit as st
import pandas as pd

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
        
    def profile_creator(self, df_profiles, df_MSRs, MSR_name):
        df_MSR_profile = pd.DataFrame()
        df_MSR_profile["DATUM_TIJDSTIP_2024"] = df_profiles["DATUM_TIJDSTIP_2024"].copy()
        df_MSR_profile["DATUM_TIJDSTIP_2023"] = df_profiles["DATUM_TIJDSTIP_2023"].copy()
        df_MSR_profile["Woning [kW]"] = df_profiles["Woning_AZI"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Wo", df_MSRs)]
        df_MSR_profile["Appartement [kW]"] = df_profiles["Appartement_AZI"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ap", df_MSRs)]
        df_MSR_profile["Winkel [kW]"] = df_profiles["Winkelfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Wi", df_MSRs)]
        df_MSR_profile["Onderwijs [kW]"] = df_profiles["Onderwijsfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("On", df_MSRs)]
        df_MSR_profile["Kantoor [kW]"] = df_profiles["Kantoorfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ka", df_MSRs)]
        df_MSR_profile["Gezondsheid [kW]"] = df_profiles["Gezondheidszorgfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ge", df_MSRs)]
        df_MSR_profile["Industrie [kW]"] = df_profiles["Industriefunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("In", df_MSRs)]
        df_MSR_profile["Overig [kW]"] = df_profiles["Overig"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ov", df_MSRs)]
        df_MSR_profile["Logies [kW]"] = df_profiles["Logiesfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Lo", df_MSRs)]
        df_MSR_profile["Bijenkomst [kW]"] = df_profiles["Bijeenkomstfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Bi", df_MSRs)]
        df_MSR_profile["Sport [kW]"] = df_profiles["Sportfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Sp", df_MSRs)]
        df_MSR_profile["Zonnepanelen [kW]"] = df_profiles["ZP normalised energy [kWh/kWh]"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Zp", df_MSRs)]*0.88
        df_MSR_profile["Oplaad punten [kW]"] = df_profiles["Charge point energy_normalised [kWh/kWh]"].copy()*df_MSRs[MSR_name][self.building_type_to_num("CP", df_MSRs)]*12670
        
        
        return df_MSR_profile
    
    def building_type_to_num(self, letter, df_MSRs):
        # Find the row index where "MSR:" column equals "Woning [kWh/ year]"
        if letter == "Wo":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Woning [kWh/ year]"]

        if letter == "Ap":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Apartement [kWh/ year]"]

        if letter == "Wi":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Winkelfunctie [kWh/ year]"]

        if letter == "On":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Onderwijsfunctie [kWh/ year]"]

        if letter == "Ka":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Kantoorfunctie [kWh/ year]"]

        if letter == "Ge":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Gezondsheidszorgfunctie [kWh/ year]"]

        if letter == "In":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Industriefunctie [kWh/ year]"]

        if letter == "Ov":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Overig [kWh/ year]"]

        if letter == "Lo":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Logiesfunctie [kWh/ year]"]

        if letter == "Bi":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Bijenkomstfunctie [kWh/ year]"]

        if letter == "Sp":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Sportfunctie [kWh/ year]"]

        if letter == "Zp":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Watt peak zonnenpanelen [W]"]

        if letter == "CP":
            matches = df_MSRs.index[df_MSRs["MSR:"] == "Num_cps [-]"]

        if len(matches) == 0:
            # If not found, return 0 or raise an error
            return "Error, letter not found!"

        # Return the first matching row index
        return matches[0]


if __name__ == "__main__":
    main()