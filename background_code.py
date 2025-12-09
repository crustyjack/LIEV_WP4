# Written by: Michael Jenks
# Last update: 24/11/2025

import gspread
import requests

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt

from google.oauth2.service_account import Credentials
from datetime import timedelta
from PIL import Image
from io import BytesIO

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
        df_MSR_profile["Zonnepanelen [kW]"] = -df_profiles["ZP normalised energy [kWh/kWh]"].copy()*df_MSRs[MSR_name][self.building_type_to_num("Zp", df_MSRs)]*0.88*4
        df_MSR_profile["Oplaad punten [kW]"] = df_profiles["Charge point energy_normalised [kWh/kWh]"].copy()*df_MSRs[MSR_name][self.building_type_to_num("CP", df_MSRs)]*12670*4 # 12670 is the average yearly usage per charging point
                
        df_MSR_profile["Woningen totaal [kW]"] = df_MSR_profile["Woning [kW]"] + df_MSR_profile["Appartement [kW]"]
        df_MSR_profile["Utiliteit totaal [kW]"] = df_MSR_profile["Winkel [kW]"] + df_MSR_profile["Onderwijs [kW]"] + df_MSR_profile["Kantoor [kW]"] + df_MSR_profile["Gezondsheid [kW]"] + df_MSR_profile["Industrie [kW]"] + df_MSR_profile["Overig [kW]"] + df_MSR_profile["Logies [kW]"] + df_MSR_profile["Bijenkomst [kW]"] + df_MSR_profile["Sport [kW]"]
        df_MSR_profile["MSR totaal [kW]"] = df_MSR_profile["Zonnepanelen [kW]"] + df_MSR_profile["Oplaad punten [kW]"] + df_MSR_profile["Woningen totaal [kW]"] + df_MSR_profile["Utiliteit totaal [kW]"]

        df_MSR_profile["DATUM_TIJDSTIP_2024"] = pd.to_datetime(df_MSR_profile["DATUM_TIJDSTIP_2024"], dayfirst=True)

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

    def prepare_plot_df(self, start_date, end_date, df, MSR_name, df_MSRs_measured):
        #df["DATUM_TIJDSTIP_2024"] = pd.to_datetime(df["DATUM_TIJDSTIP_2024"])

        df_MSR_measured_specific = df_MSRs_measured[["DATUM_TIJDSTIP_2024", f"MSR: {self._MSR_name_to_ID(MSR_name)} demand [kW]"]].copy()
        df_profiles = df.copy()
        df_merged = df_profiles.merge(df_MSR_measured_specific, on="DATUM_TIJDSTIP_2024", how="left")

        mask = (df["DATUM_TIJDSTIP_2024"] >= pd.to_datetime(start_date)) & (df["DATUM_TIJDSTIP_2024"] <= pd.to_datetime(end_date))
        
        df_slice = df_merged.loc[mask]

        # --- add to cols to plot ---
        cols_to_plot = [
            "Woningen totaal [kW]",
            "Utiliteit totaal [kW]",
            "Zonnepanelen [kW]",
            "Oplaad punten [kW]",
            "MSR totaal [kW]",
        ]

        # Add MSR demand column safely
        msr_col = f"MSR: {self._MSR_name_to_ID(MSR_name)} demand [kW]"
        cols_to_plot.append(msr_col)

        #cols_to_plot.append(f"MSR: {self._MSR_name_to_ID(MSR_name)} demand [kW]")

        # adjuster for amount of CPs in neaightbourhood
        #df_slice["Oplaad punten [kW]"] = df_slice["Oplaad punten [kW]"]*((year-2025)/25)*EV_factor
        #df_slice["MSR totaal [kW]"] = df_slice["Zonnepanelen [kW]"] + df_slice["Oplaad punten [kW]"] + df_slice["Woningen totaal [kW]"] + df_slice["Utiliteit totaal [kW]"]
        
        # --- store into session_state
        st.session_state["df_plot_data"] = df_slice.set_index("DATUM_TIJDSTIP_2024")[cols_to_plot]

        #return plot
    def _MSR_name_to_ID(self, MSR_name):
        if MSR_name == "Sporenburg":
            MSR_ID_short = 9020467
            MSR_ID_long = 1099527115509
        if MSR_name == "Roelantstraat":
            MSR_ID_short = 3002917
            MSR_ID_long = 1099524246697
        if MSR_name == "Vincent van Goghstraat":
            MSR_ID_short = 9015800
            MSR_ID_long = 1099526882871

        return MSR_ID_short #, MSR_ID_long


            # Sporenburg", "Roelantstraat", "Vincent van Goghstraat"
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

        df = self._adjust_EV_profile(df, target_year)
        return df
    
    def adjust_EV_profile(self, df, EV_adoption_rate, EV_factor=5):
        df["Oplaad punten [kW]"] = df["Oplaad punten [kW]"]*((EV_adoption_rate-10)/90)*EV_factor
        df["MSR totaal [kW]"] = df["Zonnepanelen [kW]"] + df["Oplaad punten [kW]"] + df["Woningen totaal [kW]"] + df["Utiliteit totaal [kW]"]

        return df
    
    def update_charge_strat(self, df, charge_strat, df_profiles, df_MSRs, MSR_name):
        charge_profile_name = self.charge_profile_lookup(charge_strat)
        df["Oplaad punten [kW]"] = df_profiles[charge_profile_name].copy()*df_MSRs[MSR_name][self.building_type_to_num("CP", df_MSRs)]*12670*4 
        df["MSR totaal [kW]"] = df["Zonnepanelen [kW]"] + df["Oplaad punten [kW]"] + df["Woningen totaal [kW]"] + df["Utiliteit totaal [kW]"]

        return df
    
    def charge_profile_lookup(self, charge_strat):
        
        if charge_strat == "Regular on-demand charging":
            prof_name = "Charge point energy_normalised [kWh/kWh]"
        
        if charge_strat == "Grid-aware smart charging":
            prof_name = "Elaad_net_bewust_norm. [kWh/kWh]"

        if charge_strat == "Capacity pooling":
            prof_name = "Elaad_cap_pooling_norm. [kWh/kWh]"

        if charge_strat == "V2G":
            prof_name = "Elaad_V2G_norm. [kWh/kWh]"

        return prof_name

    def plot_df_with_dashed_lines(
            self, 
            df,
            placeholder,
            dashed_series = [
                "Oplaad punten [kW]",
                "Utiliteit totaal [kW]",
                "Woningen totaal [kW]",
                "Zonnepanelen [kW]"
            ]
        ):
        if df is None or df.empty:
            placeholder.write("No data to plot.")
            return
        
        label_map = {
            "Oplaad punten [kW]" : "Public charging points",
            "Utiliteit totaal [kW]": "Utility buildings",
            "Woningen totaal [kW]": "Accomodation buildings",
            "Zonnepanelen [kW]": "Solar panels"
        }

        dashed_series = [
            "Public charging points",
            "Utility buildings",
            "Accomodation buildings",
            "Solar panels"
        ]

        # Reset index safely
        df_reset = df.reset_index()

        # Identify the index column (the column added by reset_index)
        index_col = df_reset.columns[0]

        # Ensure datetime index is treated correctly
        df_reset[index_col] = pd.to_datetime(df_reset[index_col])

        # Convert to long format
        df_long = df_reset.melt(
            id_vars=index_col,
            var_name="series",
            value_name="value"
        )

        df_long["series"] = df_long["series"].replace(label_map)

        # Build chart
        chart = (
            alt.Chart(df_long)
            .mark_line()
            .encode(
                x=alt.X(index_col + ":T", title="Date"),   # Temporal axis (date/time)
                y=alt.Y("value:Q", title="Power [kW]"),
                color=alt.Color("series:N", title=""),
                strokeDash=alt.condition(
                    alt.FieldOneOfPredicate(field="series", oneOf=dashed_series),
                    alt.value([4, 4]),       # dashed style
                    alt.value([1, 0])        # solid style
                ),
                strokeWidth=alt.condition(
                    alt.FieldOneOfPredicate(field="series", oneOf=dashed_series),
                    alt.value(1),            # thinner dashed lines
                    alt.value(2.5)           # thicker solid lines
                )
            )
            .properties(
                padding={"bottom": 40}         # add 40px bottom margin
            )
        )

        # Render chart
        placeholder.altair_chart(chart, width='stretch')
    
    # --- Image function set up ---
    def image_converter(self, URL, R, G, B, A, width=None):
        response = requests.get(URL)
        image = Image.open(BytesIO(response.content)).convert("RGBA")
        background = Image.new("RGBA", image.size, (R, G, B, A))
        background.paste(image, (0,0), image)
        final_image = background.convert("RGB")

        if width:
            w, h = final_image.size
            ratio = width / w
            new_height = int(h * ratio)
            final_image = final_image.resize((width, new_height), Image.LANCZOS)

        return final_image
    
    def image_loader(self, URL, width=None):
        response = requests.get(URL)
        image = Image.open(BytesIO(response.content)).convert("RGBA")

        if width:
            w, h = image.size
            ratio = width / w
            new_height = int(h * ratio)
            image = image.resize((width, new_height), Image.LANCZOS)
        
        return image
    
    def MSR_image_display(self, MSR_name):
        if MSR_name == "Sporenburg":
            image_URL = "https://i.ibb.co/bjWzTp9K/Sporenburg.png"
        elif MSR_name == "Roelantstraat":
            image_URL = "https://i.ibb.co/v6tmHYWN/Roelantstraat.png"
        elif MSR_name == "Vincent van Goghstraat":
            image_URL = "https://i.ibb.co/zHZsmrsy/Vincent-van-Goghstraat.png"
        else:
            return NameError
        
        loaded_image = self.image_loader(image_URL)

        return loaded_image

if __name__ == "__main__":
    main()