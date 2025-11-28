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

st.title("⚡MSR model Amsterdam")
st.write(
    "We hope this is useful for you."
)
MSR_name = st.selectbox(
    "Which MSR would you like to view the model for?",
    ("Sporenburg", "Roelantstraat", "Vincent van Goghstraat"))

#print(option)

#Accom_elect_perc = st.slider("What percentage of accomodation is fully electric?", 0, 100, 25)

year = st.slider("What year would you like to model? - For now only impacts EV adoption", 2025, 2050, 2025)

if st.button("Change date to largest draw through MSR"):
    default_start = df_output[f"DATE_{year}"].min().date()

if st.button("Change date to least (or most negative) draw through MSR"):
    None
#st.write("You are modelling ", MSR_name, " MSR", "with an fully electric home adoption rate of ", Accom_elect_perc, "%, in the year ", year, ".")


# Section to load in all dataframes if they are not in cached storage.
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

df_MSRs = st.session_state.df_MSRs

df_output = bg.profile_creator(df_profiles, df_MSRs, MSR_name)
df_output["DATUM_TIJDSTIP_2024"] = pd.to_datetime(df_output["DATUM_TIJDSTIP_2024"], dayfirst=True)
df_output = bg._map_2024_to_year(df_output, year)
#test = bg.building_type_to_num("Wo", df_MSRs)
#print(test)
# hi


# st.dataframe(df_output)

#st.sidebar.header("Date Filter")



min_date = df_output[f"DATE_{year}"].min().date()
max_date = df_output[f"DATE_{year}"].max().date()

default_start = datetime.now()

start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
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
#st.write(df_output)


# --- TESTING ---
