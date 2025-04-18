# streamlit_app.py

import streamlit as st
from views.augmento_api_view import load_api_view
from views.data_wrangler_view import load_wrangler_view  # Optional


st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)


# Navigation
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)
with st.sidebar:
    st.sidebar.image("../Assets/NTC_Icon.png", width=100, clamp=True)
    st.sidebar.title("NTC Augmento App")

    view = st.sidebar.radio("Select View below", ["📥 Load & Audit Dataset", "🧩 Data Wrangler"])

if view == "📥 Load & Audit Dataset":
    load_api_view()
elif view == "🧩 Data Wrangler":
    load_wrangler_view()
