# streamlit_app.py

import streamlit as st
import polars as pl
import pandas as pd
from utils.visualization.visual_utils import plot_btc_candlestick
from utils.ui.layout_utils import render_logo




st.set_page_config(page_title="Home — NTC TAP", layout="wide")



render_logo()




#st.header("👋 Welcome to NTC Tabular Analytics Platform (NTC-TAP)")

df_start = pl.read_parquet(
    "app_assets/_hidden_asset/bitmex_XBTUSD_1d_2020-01-01_until_2025-01-01.parquet").to_pandas()

df_start['timestamp'] = pd.to_datetime(df_start['timestamp']).dt.tz_localize(None)

# Sidebar or main panel for selecting date range
min_date = df_start['timestamp'].min().date()
max_date = df_start['timestamp'].max().date()

start_default = pd.to_datetime("2023-01-01").date()
end_default = max_date

start_date, end_date = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(start_default, end_default),
    format="YYYY-MM-DD"
)

fig = plot_btc_candlestick(df_start,
    date_column="timestamp",
    start_date=start_date,
    end_date=end_date
)

#st.subheader("📈 BTC Candlestick Chart")

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
Use the menu on the left to navigate between:
- Data Loader  (DONE)
- Session Manager (WIP)
- Data Wrangler (WIP)
- Data Analysis (WIP) 
- Time Series Analysis (WIP)
- Model Demo  (OPEN)
""")

# st.set_page_config(layout="wide")
# 
# st.markdown("""
#     <style>
#         .block-container {
#             padding-top: 1rem !important;
#             padding-bottom: 1rem !important;
#         }
#     </style>
# """, unsafe_allow_html=True)
# 
# 
# # Navigation
# st.markdown(
#     """
#     <style>
#         [data-testid=stSidebar] [data-testid=stImage]{
#             text-align: center;
#             display: block;
#             margin-left: auto;
#             margin-right: auto;
#             width: 100%;
#         }
#     </style>
#     """, unsafe_allow_html=True
# )
# with st.sidebar:
#     st.sidebar.image("../Assets/NTC_Icon.png", width=100, clamp=True)
#     st.sidebar.title("NTC Augmento App")
# 
#     view = st.sidebar.radio("Select View below", ["⚗️ Augmento API", "📈 BitMEX API", "🧩 Data Wrangler"])
# 
# if view == "⚗️ Augmento API":
#     st.sidebar.markdown("---")
#     load_api_view()
# elif view == "📈 BitMEX API":
#     st.sidebar.markdown("---")
#     load_bitmex_view()
#     #st.sidebar.markdown("---")
# elif view == "🧩 Data Wrangler":
#     st.sidebar.markdown("---")
#     load_wrangler_view()
# 