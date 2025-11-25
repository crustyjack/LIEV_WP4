# Written by: Michael Jenks
# Last update: 24/11/2025

import gspread

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from google.oauth2.service_account import Credentials
from datetime import timedelta

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
        df_MSR_profile["Woning [kW]"] = df_profiles["Woning_AZI"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Wo", df_MSRs)]*4
        df_MSR_profile["Appartement [kW]"] = df_profiles["Appartement_AZI"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ap", df_MSRs)]*4
        df_MSR_profile["Winkel [kW]"] = df_profiles["Winkelfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Wi", df_MSRs)]*4
        df_MSR_profile["Onderwijs [kW]"] = df_profiles["Onderwijsfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("On", df_MSRs)]*4
        df_MSR_profile["Kantoor [kW]"] = df_profiles["Kantoorfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ka", df_MSRs)]*4
        df_MSR_profile["Gezondsheid [kW]"] = df_profiles["Gezondheidszorgfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ge", df_MSRs)]*4
        df_MSR_profile["Industrie [kW]"] = df_profiles["Industriefunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("In", df_MSRs)]*4
        df_MSR_profile["Overig [kW]"] = df_profiles["Overig"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Ov", df_MSRs)]*4
        df_MSR_profile["Logies [kW]"] = df_profiles["Logiesfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Lo", df_MSRs)]*4
        df_MSR_profile["Bijenkomst [kW]"] = df_profiles["Bijeenkomstfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Bi", df_MSRs)]*4
        df_MSR_profile["Sport [kW]"] = df_profiles["Sportfunctie"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Sp", df_MSRs)]*4
        df_MSR_profile["Zonnepanelen [kW]"] = df_profiles["ZP normalised energy [kWh/kWh]"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Zp", df_MSRs)]*0.88*4
        df_MSR_profile["Oplaad punten [kW]"] = df_profiles["Charge point energy_normalised [kWh/kWh]"].copy()*df_MSRs[MSR_name][self.building_type_to_num("CP", df_MSRs)]*12670*4
        
        df_MSR_profile["Woningen totaal [kW]"] = df_MSR_profile["Woning [kW]"] + df_MSR_profile["Appartement [kW]"]
        df_MSR_profile["Utiliteit totaal [kW]"] = df_MSR_profile["Winkel [kW]"] + df_MSR_profile["Onderwijs [kW]"] + df_MSR_profile["Kantoor [kW]"] + df_MSR_profile["Gezondsheid [kW]"] + df_MSR_profile["Industrie [kW]"] + df_MSR_profile["Overig [kW]"] + df_MSR_profile["Logies [kW]"] + df_MSR_profile["Bijenkomst [kW]"] + df_MSR_profile["Sport [kW]"]
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
    
    def _add_sudo_year(self, df, year):
        df[f"Pseudo year {year}"] = df["DATUM_TIJDSTIP_2024"].copy()
        first_day_24 = df["DATUM_TIJDSTIP_2024"].min().date().isoweekday()
        first_day_yr = pd.to_datetime(f"{year}-01-01").date().isoweekday()
        day_difference = first_day_yr - first_day_24
        if day_difference >= 4:
            df[f"Pseudo year {year}"] = np.roll(df[f"Pseudo year {year}"], shift=-day_difference*96)
        else:
            df[f"Pseudo year {year}"] = np.roll(df[f"Pseudo year {year}"], shift=day_difference*96)
        return df

    def plot_df(self, start_date, end_date, df, year, cols_to_plot=["Woningen totaal [kW]", "Utiliteit totaal [kW]"]):
        df["DATUM_TIJDSTIP_2024"] = pd.to_datetime(df["DATUM_TIJDSTIP_2024"])
        mask = (df[f"DATE_{year}"] >= pd.to_datetime(start_date)) & (df[f"DATE_{year}"] <= pd.to_datetime(end_date))
        df_slice = df.loc[mask]

        # st.write("Filtered DataFrame", df_slice)

        # ---- PLOT ----
        st.session_state["df_plot_data"] = df_slice.set_index(f"DATE_{year}")[cols_to_plot]

        #return plot
    
    def _mask_maker(self, start_date, end_date, df):
        df["DATUM_TIJDSTIP_2024"] = pd.to_datetime(df["DATUM_TIJDSTIP_2024"])
        mask = (df["DATUM_TIJDSTIP_2024"] >= pd.to_datetime(start_date)) & (df["DATUM_TIJDSTIP_2024"] <= pd.to_datetime(end_date))

        return mask
    
    def _map_2024_to_year(self, df, target_year, date_col="DATUM_TIJDSTIP_2024"):
        """
        Takes 2024 timestamps and maps them into another year
        while preserving weekday alignment.
        """
        if df[date_col].dt.year.nunique() != 1 or df[date_col].dt.year.iloc[0] != 2024:
            raise ValueError("Input column must contain only dates from 2024")

        # Start with no shift
        shift_weeks = 0

        # Find the smallest number of weeks forward such that year == target_year
        while True:
            shifted = df[date_col] + timedelta(weeks=shift_weeks)
            if shifted.dt.year.iloc[0] == target_year:
                break
            shift_weeks += 1  # try next 7-day shift

        # Create the new column
        df[f"DATE_{target_year}"] = shifted
        df[f"DATE_{target_year}"] = pd.to_datetime(df[f"DATE_{target_year}"])

        return df

if __name__ == "__main__":
    main()