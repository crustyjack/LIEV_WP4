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
default_end = datetime.now() + timedelta(days=1)

start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
end_date = st.date_input("End date", start_date + timedelta(days=1), min_value=start_date + timedelta(days=1), max_value=max_date)

plot_placeholder = st.empty()   # chart will appear BELOW this

# ---- INIT SESSION STATE ----
if "df_plot_data" not in st.session_state:
    st.session_state["df_plot_data"] = None

# ---- BUTTON (always above the plot) ----
if st.button("Update plot"):
    bg.plot_df(start_date, end_date, df_output, year)

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
# The following works - it jsut has to be run through the function bg.plot_df_with_dashed_lines(df, dashed_series, placeholder)
"""
df = st.session_state["df_plot_data"]

# Reset index safely
df_reset = df.reset_index()

# Identify the index column (the column added by reset_index)
index_col = df_reset.columns[0]   # first column is the former index

df_long = df_reset.melt(
    id_vars=index_col,
    var_name="series",
    value_name="value"
)

# Example dashed lines
dashed_series = ["Oplaad punten [kW]",
                 "Utiliteit totaal [kW]",
                 "Woningen totaal [kW]",
                 "Zonnepanelen [kW]"]

chart = (
    alt.Chart(df_long)
    .mark_line()
    .encode(
        x=index_col + ":T",   # use the detected column
        y="value:Q",
        color="series:N",
        strokeDash=alt.condition(
            alt.FieldOneOfPredicate(field="series", oneOf=dashed_series),
            alt.value([4, 4]),
            alt.value([1, 0])
        ),
        strokeWidth=alt.condition(
            alt.FieldOneOfPredicate(field="series", oneOf=dashed_series),
            alt.value(1),        # thinner dashed line
            alt.value(2.5)       # default thickness for solid lines
        )
    )
)

plot_placeholder.altair_chart(chart, use_container_width=True)
"""