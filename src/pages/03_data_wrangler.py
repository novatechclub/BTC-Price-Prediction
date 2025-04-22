# pages/02_Data_Wrangler.py
import streamlit as st
from home import render_sidebar
from views.data_wrangler_view import load_wrangler_view

st.set_page_config(page_title="Data Wrangler", layout="wide")
render_sidebar()
load_wrangler_view()
