# streamlit run LIEV_WP4_model.py

import background_code
import gspread
import matplotlib

import streamlit as st
import pandas as pd
import altair as alt

from google.oauth2.service_account import Credentials
from datetime import timedelta, datetime

bg = background_code.BackgroundCode()


# --- Load background data ---

# Load sheet only if not already in session_state
if "sheet" not in st.session_state:
    st.session_state.sheet = bg.load_Gsheets()

sheet = st.session_state.sheet

# Load profiles dataframe only if not already in session_state
if "df_profiles" not in st.session_state:
    st.session_state.df_profiles = bg.get_sheet_dataframe("Profiles", sheet)

df_profiles = st.session_state.df_profiles

# Load MSR dataframe only if not already in session_state
if "df_MSRs" not in st.session_state:
    st.session_state.df_MSRs = bg.get_sheet_dataframe("MSR_summary", sheet)

df_MSRs = st.session_state.df_MSRs

# Load MSR measured dataframe only if not already in session_state
if "df_MSRs_measured" not in st.session_state:
    st.session_state.df_MSRs_measured = bg.get_sheet_dataframe("MSR_measured_profiles", sheet)

df_MSRs_measured = st.session_state.df_MSRs_measured

df_merged = df_profiles.merge(df_MSRs_measured, on="DATUM_TIJDSTIP_2024", how="left")

# --- Create page ---
st.title("⚡MSR model Amsterdam")
st.write(
    "We hope this is useful for you."
)
MSR_name = st.selectbox(
    "Which MSR would you like to view the model for?",
    ("Sporenburg", "Roelantstraat", "Vincent van Goghstraat"))

#Accom_elect_perc = st.slider("What percentage of accomodation is fully electric?", 0, 100, 25)

year = st.slider("What year would you like to model? - For now only impacts EV adoption", 2025, 2050, 2025)

df_output = bg.profile_creator(df_profiles, df_MSRs, MSR_name)
df_output = bg._map_2024_to_year(df_output, year)

if "min_max" not in st.session_state:
    st.session_state.min_max = "-"

if st.button("Change date to largest draw through MSR"):
    date_max_power = df_output.loc[df_output["MSR totaal [kW]"].idxmax(), (f"DATE_{year}")]
    st.session_state.date_max_power = date_max_power
    st.session_state.min_max = "max"

if st.button("Change date to least (or most negative) draw through MSR"):
    date_min_power = df_output.loc[df_output["MSR totaal [kW]"].idxmin(), (f"DATE_{year}")]
    st.session_state.date_min_power = date_min_power
    st.session_state.min_max = "min"
#st.write("You are modelling ", MSR_name, " MSR", "with an fully electric home adoption rate of ", Accom_elect_perc, "%, in the year ", year, ".")

min_date = df_output[f"DATE_{year}"].min().date()
max_date = df_output[f"DATE_{year}"].max().date()

default_start = min_date

if "min_max" in st.session_state:
    if st.session_state.min_max == "max" and "date_max_power" in st.session_state:
        default_start = st.session_state.date_max_power
    elif st.session_state.min_max == "min" and "date_min_power" in st.session_state:
        default_start = st.session_state.date_min_power

start_date = st.date_input("Start date", default_start, min_value=min_date, max_value=max_date)
end_date = st.date_input("End date", start_date + timedelta(days=1), min_value=start_date + timedelta(days=1), max_value=max_date)

plot_placeholder = st.empty()   # chart will appear BELOW this

# ---- INIT SESSION STATE ----
if "df_plot_data" not in st.session_state:
    st.session_state["df_plot_data"] = None

# ---- BUTTON (always above the plot) ----
if st.button("Update plot"):
    bg.prepare_plot_df(start_date, end_date, df_output, year) # not sure what this does

# ---- SHOW PLOT (if exists) ----
plot_placeholder = st.empty()   # <--- optional: ensure placeholder exists early

if st.session_state["df_plot_data"] is not None:
    #plot_placeholder.line_chart(st.session_state["df_plot_data"])
    bg.plot_df_with_dashed_lines(st.session_state["df_plot_data"], plot_placeholder)
else:
    st.write("No plot generated yet.")

# ---- DEBUG ----
#st.write(st.session_state["df_plot_data"])
st.write(df_merged)


# --- TESTING ---
