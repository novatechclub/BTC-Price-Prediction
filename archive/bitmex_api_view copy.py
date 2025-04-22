# bitmex_api_view.py

import streamlit as st
from utils.bitmex_client import BitmexClient
from utils.augmento_audit import AugmentoClientAudit
from datetime import datetime
import pandas as pd
from pathlib import Path
import io

from utils.visual_utils import (
    plot_missing_heatmap,
    plot_top_distributions,
    plot_total_trading_activity,
)

def load_bitmex_view():
    st.subheader("📥 Load & Inspect Dataset (BitMEX)")

    @st.cache_data(show_spinner="Scanning Preloaded Files")
    def get_preloaded_datasets():
        folder = Path("preloaded_datasets_bitmex")
        return sorted([f for f in folder.glob("*.parquet") if f.name.startswith("bitmex")])

    @st.cache_data(show_spinner="Downloading Data", persist="disk")
    def load_data(start_date, end_date, symbol, bin_size):
        client = BitmexClient()
        df = client.fetch_bucketed_data(
            start_date=start_date,
            end_date=end_date,
            symbol=symbol,
            bin_size=bin_size
        )
        return df, client

    def store_session_data(df, client, auditor):
        st.session_state.df = df
        st.session_state.client = client
        st.session_state.auditor = auditor

    # Sidebar Config
    st.sidebar.header("Data Loader Controls")

    load_mode = st.sidebar.radio("Choose Load Mode", ["📦 Preloaded Dataset", "🌐 Load from API"], key="bitmex_load_mode")

    default_symbol = "XBTUSD"
    default_bin_size = "1h"

    if load_mode == "📦 Preloaded Dataset":
        preloaded_files = get_preloaded_datasets()
        selected_file = st.sidebar.selectbox("Select Preloaded Dataset", [f.name for f in preloaded_files])
        store_in_session = st.sidebar.checkbox("✅ Add to Wrangler Session", key="store_checkbox_bitmex_1")

        if st.sidebar.button("📥 Load Selected File", key="bitmex_file_load"):
            if st.session_state.get("last_loaded_file") != selected_file:
                df = pd.read_parquet(f"./preloaded_datasets_bitmex/{selected_file}")
                parts = selected_file.replace(".parquet", "").split("_")
                symbol, bin_size, start, end = parts[1], parts[2], parts[3], parts[4]

                client = BitmexClient()
                client.source = "bitmex"
                client.coin = symbol
                client.bin_size = bin_size
                client.start_date = start
                client.end_date = end
                client.last_df = df

                auditor = AugmentoClientAudit.from_client(df, _client=client, source="bitmex", verbose=False)
                store_session_data(df, client, auditor)
                st.session_state.last_loaded_file = selected_file
                st.sidebar.success("✅ Dataset loaded!")

    else:
        store_in_session = st.sidebar.checkbox("✅ Add to Wrangler Session", key="store_checkbox_bitmex_2")
        start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
        end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2025-01-01"))
        symbol = st.sidebar.text_input("Symbol", value=default_symbol)
        bin_size = st.sidebar.selectbox("Bin Size", ["1m", "5m", "1h", "1d"], index=2)

        if st.sidebar.button("📥 Load & Inspect Dataset", key="load_file_bitmex"):
            df, client = load_data(
                start_date=str(start_date),
                end_date=str(end_date),
                symbol=symbol,
                bin_size=bin_size
            )
            client.source = "bitmex"
            client.coin = symbol
            client.bin_size = bin_size
            client.start_date = str(start_date)
            client.end_date = str(end_date)
            client.last_df = df

            auditor = AugmentoClientAudit.from_client(df, _client=client, source="bitmex", verbose=False)
            store_session_data(df, client, auditor)
            st.sidebar.success("✅ Dataset loaded!")

    if "df" in st.session_state and "auditor" in st.session_state:
        df = st.session_state.df
        client = st.session_state.client
        auditor = st.session_state.auditor

        st.sidebar.success(f"Loaded shape: {df.shape}")

        if store_in_session:
            if "saved_datasets" not in st.session_state:
                st.session_state.saved_datasets = []
            dataset_name = f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_{client.end_date}"
            if not any(d["name"] == dataset_name for d in st.session_state.saved_datasets):
                st.session_state.saved_datasets.append({"name": dataset_name, "df": df})

        # === KPIs ===
        n_rows, n_cols = df.shape
        n_missing = df.isnull().sum().sum()
        n_duplicates = df.duplicated(subset=["datetime"]).sum()
        total_cells = n_rows * n_cols
        score = max(0, round(100 - ((n_missing / total_cells) * 50 + (n_duplicates / n_rows) * 50), 1))

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("🧮 Rows", f"{n_rows:,}")
        k2.metric("🧱 Columns", f"{n_cols:,}")
        k3.metric("❌ Missing", f"{n_missing:,}")
        k4.metric("🔁 Duplicates", f"{n_duplicates:,}")
        k5.metric("💯 Quality Score", f"{score}/100")

        # === Export + Preview ===
        df_display, format_toggle, file_download_button = st.columns(3)
        with df_display:
            full_dataframe_prev = st.checkbox("Show full preview", key="bitmex_full_preview")
        with format_toggle:
            export_format = st.radio("Choose a format", ["CSV", "Parquet"], horizontal=True, label_visibility="collapsed", key="export_format_bitmex")
        with file_download_button:
            file_prefix = f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_until_{client.end_date}"
            if export_format == "CSV":
                st.download_button("💾 Download as CSV", df.to_csv(index=False), f"{file_prefix}.csv", mime="text/csv", key="csv_download_bitmex")
            else:
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                st.download_button("💾 Download as Parquet", buffer.getvalue(), f"{file_prefix}.parquet", key="parquet_download_bitmex")

        st.dataframe(df if full_dataframe_prev else df.head(500), use_container_width=True)

        st.subheader("🔍 Missing Values per Column")
        missing_by_col = df.isnull().sum()
        if (missing := missing_by_col[missing_by_col > 0].sort_values(ascending=False)).empty:
            st.success("✅ No missing values found.")
        else:
            st.bar_chart(missing)

        st.subheader("📊 Visual Summary")
        st.plotly_chart(plot_missing_heatmap(df, bin_size=client.bin_size), use_container_width=True)
        st.plotly_chart(plot_top_distributions(df[["open", "high", "low", "close", "trades"]], top_n=5), use_container_width=True)
        st.plotly_chart(plot_total_trading_activity(df), use_container_width=True)

        if st.toggle("📋 Show Metadata", value=False):
            st.json({
                "source": client.source,
                "coin": client.coin,
                "bin_size": client.bin_size,
                "start_date": client.start_date,
                "end_date": client.end_date,
                "missing_intervals": len(auditor.audit_report["missing_time_points"]),
                "duplicates": len(auditor.audit_report["duplicate_timestamps"]),
                "flagged_columns": auditor.audit_report.get("flagged_columns", [])
            })
