# pages/03_Data_Analysis.py
import streamlit as st
from utils.ui.layout_utils import render_logo
import streamlit as st
import pandas as pd
from pathlib import Path
import polars as pl
from views.eda.eda_features_view import load_dataset_summary


st.set_page_config(page_title="Data Analysis", layout="wide")
render_logo(title="📊 Data Analysis")

PRELOADED_FILES = Path("app_assets/preloaded_assets/time_series_preloaded")

def load_preloaded_datasets():
    folder = PRELOADED_FILES
    return sorted(folder.glob("*.parquet"))

#st.subheader("📊 Basic EDA")

# Load Mode
source_mode = st.radio("Select Data Source", ["📦 Preloaded", "📁 Session"], key="eda_source_mode")

selected_df = None
dataset_name = None

if source_mode == "📦 Preloaded":
    preloaded_files = load_preloaded_datasets()
    if not preloaded_files:
        st.warning("No preloaded datasets found.")
    else:
        selected_file = st.selectbox("Select Dataset File", [f.name for f in preloaded_files])
        if st.button("📥 Load Dataset"):
            selected_df = pl.read_parquet(f"{str(PRELOADED_FILES)}/{selected_file}")
            selected_df = selected_df.to_pandas()
            dataset_name = selected_file
elif source_mode == "📁 Session":
    if "saved_datasets" not in st.session_state or not st.session_state.saved_datasets:
        st.warning("No datasets stored in session.")
    else:
        names = [d["name"] for d in st.session_state.saved_datasets]
        selected_name = st.selectbox("Select Session Dataset", names)
        if st.button("📥 Load Dataset"):
            selected_df = next(d["df"] for d in st.session_state.saved_datasets if d["name"] == selected_name)
            dataset_name = selected_name

# Create Dataset Summary
if selected_df is not None:
    tab1, tab2 = st.tabs(["📊 Feature Summary", "📈 Data Visualizations"])
    with tab1:

        st.subheader("📊 Feature Summary")
        load_dataset_summary(dataset_name=dataset_name, selected_df=selected_df)
    with tab2:
        st.subheader("📈 Data Visualizations")
        # Add your data visualizations here
        st.write("Visualizations will be added here.")
        # Example: st.line_chart(selected_df)
        # Example: st.bar_chart(selected_df)
        # Example: st.map(selected_df)
else:
    st.warning("No dataset loaded. Please select a dataset to analyze.")


