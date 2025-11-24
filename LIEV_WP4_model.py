# streamlit run LIEV_WP4_model.py

import background_code
import gspread

import streamlit as st

from google.oauth2.service_account import Credentials

bg = background_code.BackgroundCode()

st.title("⚡MSR model Amsterdam")
st.write(
    "We hope this is useful for you."
)
MSR_name = st.selectbox(
    "Which MSR would you like to view the model for?",
    ("Sporenburg", "Choice 2", "Choice 3"))

#print(option)

Accom_elect_perc = st.slider("What percentage of accomodation is fully electric?", 0, 100, 25)

year = st.slider("What year would you like to model?", 2025, 2050, 2025)

st.write("You are modelling ", MSR_name, " MSR", "with an fully electric home adoption rate of ", Accom_elect_perc, "%, in the year ", year, ".")


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

df_output = bg.profile_creator(df_profiles, df_MSRs, MSR_name)

st.dataframe(df_output)
