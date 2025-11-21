import streamlit as st
import background_code

bg = background_code.BackgroundCode()

st.title("⚡MSR model Amsterdam")
st.write(
    "We hope this is useful for you."
)
MSR = st.selectbox(
    "Which MSR would you like to view the model for?",
    ("Sporenburg", "Choice 2", "Choice 3"))

#print(option)

Accom_elect_perc = st.slider("What percentage of accomodation is fully electric?", 0, 100, 25)

year = st.slider("What year would you like to model?", 2025, 2050, 2025)

st.write("You are modelling ", MSR, " MSR", "with an fully electric home adoption rate of ", Accom_elect_perc, "%, in the year ", year, ".")

sheety = bg.load_Gsheets()