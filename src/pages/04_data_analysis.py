# pages/03_Data_Analysis.py
import streamlit as st
from home import render_sidebar

st.set_page_config(page_title="Data Analysis", layout="wide")
render_sidebar()
st.header("📊 Data Analysis")
st.write("Here you can build your EDA and time‑series plots…")
