#augmento_api_view.py

import streamlit as st
from utils.augmento_client import AugmentoAPIClient
from utils.augmento_audit import AugmentoClientAudit
from datetime import datetime
import pandas as pd
from pathlib import Path
import io

from utils.visual_utils import (
    plot_missing_heatmap,
    plot_top_distributions,
    plot_total_activity,
)



def load_api_view():
    st.subheader("📥 Load & Inspect Dataset")

    @st.cache_data(show_spinner="Fetching API Summary")
    def get_api_summary():
        return AugmentoAPIClient().get_summary()

    @st.cache_data(show_spinner="Scanning Preloaded Files")
    def get_preloaded_datasets():
        folder = Path("preloaded_datasets")
        return sorted([f for f in folder.glob("*.parquet")])

    @st.cache_data(show_spinner="Downloading Data", persist="disk")
    def load_data(start_date, end_date, source, coin, bin_size):
        client = AugmentoAPIClient()
        df = client.download_full_dataset(
            start_date=start_date,
            end_date=end_date,
            source=source,
            coin=coin,
            bin_size=bin_size
        )
        print(df["coin_type"].unique())
        print(df["source"].unique())
        print(df["bin_size"].unique())
        return df, client

    def store_session_data(df, client, auditor):
        st.session_state.df = df
        st.session_state.client = client
        st.session_state.auditor = auditor

    # Sidebar Config
    client_summary = get_api_summary()
    st.sidebar.header("Data Loader Controls")

    load_mode = st.sidebar.radio("Choose Load Mode", ["📦 Preloaded Dataset", "🌐 Load from API"], key="augmento_load_mode")

    default_coin = "bitcoin"
    default_source = "twitter"
    default_bin_size = "1H"

    if load_mode == "📦 Preloaded Dataset":
        preloaded_files = get_preloaded_datasets()
        selected_file = st.sidebar.selectbox("Select Preloaded Dataset", [f.name for f in preloaded_files])
        store_in_session = st.sidebar.checkbox("✅ Add to Wrangler Session", key="store_checkbox")

        if st.sidebar.button("📥 Load Selected File", key="augmento_file_load"):
            if st.session_state.get("last_loaded_file") != selected_file:
                # Load DataFrame from Parquet
                df = pd.read_parquet(f"./preloaded_datasets/{selected_file}")

                # Derive metadata from DataFrame instead of filename
                # -- bin_size
                bin_size_values = df["bin_size"].unique()
                if len(bin_size_values) != 1:
                    st.warning("Multiple bin_size values found; using the first one.")
                bin_size = str(bin_size_values[0]).upper()

                # -- coin_type
                coin_values = df["coin_type"].unique()
                if len(coin_values) != 1:
                    st.warning("Multiple coin_type values found; using the first one.")
                coin = coin_values[0]

                # -- source
                source_values = df["source"].unique()
                if len(source_values) != 1:
                    st.warning("Multiple source values found; using the first one.")
                source = source_values[0]

                # -- derive start/end dates from datetime column
                df["datetime"] = pd.to_datetime(df["datetime"])
                start = df["datetime"].min().strftime("%Y-%m-%d")
                end = df["datetime"].max().strftime("%Y-%m-%d")

                # Initialize client & auditor
                client = AugmentoAPIClient()
                client.source = source
                client.coin = coin
                client.bin_size = bin_size
                client.start_date = start
                client.end_date = end
                client.last_df = df

                auditor = AugmentoClientAudit.from_client(
                    df,
                    _client=client,
                    source=source,
                    verbose=False
                )
                store_session_data(df, client, auditor)
                st.session_state.last_loaded_file = selected_file
                st.sidebar.success("✅ Dataset loaded!")

    else:
        default_coin = "bitcoin"
        default_source = "twitter"
        default_bin_size = "1H"
        coins = client_summary["Coins"]
        sources = client_summary["Sources"]
        bin_sizes = list(client_summary["Bin_sizes"].keys())

        default_coin_index = coins.index(default_coin) if default_coin in coins else 0
        default_source_index = sources.index(default_source) if default_source in sources else 0
        default_bin_size_index = list(bin_sizes).index(default_bin_size) if default_bin_size in bin_sizes else 0

        summary = client_summary
        store_in_session = st.sidebar.checkbox("✅ Add to Wrangler Session", key="store_checkbox")
        start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2024-11-01"))
        end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2025-02-01"))
        source = st.sidebar.selectbox("Platform", sources, index=default_source_index)
        coin = st.sidebar.selectbox("Coin", coins, index=default_coin_index)
        bin_size = st.sidebar.selectbox("Bin Size", bin_sizes, index=default_bin_size_index)

        if st.sidebar.button("📥 Load & Inspect Dataset"):
            df, client = load_data(
                start_date=str(start_date),
                end_date=str(end_date),
                source=source,
                coin=coin,
                bin_size=bin_size
            )
            auditor = AugmentoClientAudit.from_client(df, _client=client, source=source, verbose=False)
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
        #st.subheader("📌 Dataset KPIs")
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
            full_dataframe_prev = st.checkbox("Show full preview", key="augmento_full_preview")
        with format_toggle:
            export_format = st.radio("Choose a format", ["CSV", "Parquet"], horizontal=True, label_visibility="collapsed", key="export_format")
        with file_download_button:
            if export_format == "CSV":
                st.download_button("💾 Download as CSV", df.to_csv(index=False), f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_until_{client.end_date}.csv", mime="text/csv")
            else:
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                st.download_button("💾 Download as Parquet", buffer.getvalue(), f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_until_{client.end_date}.parquet")

        st.dataframe(df if full_dataframe_prev else df.head(500), use_container_width=True)

        st.subheader("🔍 Missing Values per Column")
        missing_by_col = df.isnull().sum()
        if (missing := missing_by_col[missing_by_col > 0].sort_values(ascending=False)).empty:
            st.success("✅ No missing values found.")
        else:
            st.bar_chart(missing)

        st.subheader("📊 Visual Summary")
        st.plotly_chart(plot_missing_heatmap(df, bin_size=client.bin_size), use_container_width=True)
        st.plotly_chart(plot_top_distributions(df, top_n=5), use_container_width=True)
        st.plotly_chart(plot_total_activity(df), use_container_width=True)

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
