# pages/02_Data_Wrangler.py
import streamlit as st
from utils.ui.layout_utils import render_logo
from views.wrangler.data_wrangler_view import load_wrangler_view

#st.set_page_config(page_title="Data Wrangler", layout="wide")
st.set_page_config(page_title="Home — NTC TAP", layout="wide")
render_logo(title="🧩 Data Wrangler")
load_wrangler_view()
