# views/bitmex_api_view.py
import streamlit as st
from utils.bitmex_client import BitmexClient
from utils.augmento_audit import AugmentoClientAudit
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
        return sorted(folder.glob("*.parquet"))

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

    def store_session_data_bitmex(df, client, auditor):
        st.session_state.bitmex_df      = df
        st.session_state.bitmex_client  = client
        st.session_state.bitmex_auditor = auditor

    # === CONTROLS IN MAIN CONTENT ===
    with st.expander("⚙️ Controls", expanded=True):
        load_mode = st.radio(
            "Choose Load Mode",
            ["📦 Preloaded Dataset", "🌐 Load from API"],
            key="bitmex_load_mode"
        )

        if load_mode == "📦 Preloaded Dataset":
            preloaded_files = get_preloaded_datasets()
            selected_file = st.selectbox(
                "Select Preloaded Dataset",
                [f.name for f in preloaded_files],
                key="bitmex_selected_file"
            )
            store_in_session = st.checkbox("✅ Add to Wrangler Session", key="bitmex_store_1")
            load_pre = st.button("📥 Load Selected File", key="bitmex_file_load")
        else:
            store_in_session = st.checkbox("✅ Add to Wrangler Session", key="bitmex_store_2")
            start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"), key="bitmex_start_date")
            end_date   = st.date_input("End Date", value=pd.to_datetime("2025-01-01"), key="bitmex_end_date")
            symbol     = st.text_input("Symbol", value="XBTUSD", key="bitmex_symbol")
            bin_size   = st.selectbox("Bin Size", ["1m","5m","1h","1d"], index=2, key="bitmex_bin_size")
            load_api   = st.button("📥 Load & Inspect Dataset", key="bitmex_load_btn")

    # === DATA LOADING LOGIC ===
    if load_mode == "📦 Preloaded Dataset" and load_pre:
        if st.session_state.get("last_loaded_file_bitmex") != selected_file:
            df = pd.read_parquet(f"./preloaded_datasets_bitmex/{selected_file}")
            #parts = selected_file.replace(".parquet","").split("_")
            client = BitmexClient()
            client.source     = df["exchange"].iloc[0]
            client.coin       = df["symbol"].iloc[0]
            client.bin_size   = df["bin_size"].iloc[0]
            client.start_date = df["datetime"].min().strftime("%Y-%m-%d")
            client.end_date   = df["datetime"].max().strftime("%Y-%m-%d")
            client.last_df    = df
            auditor = AugmentoClientAudit.from_client(df, _client=client, source="bitmex", verbose=False)
            store_session_data_bitmex(df, client, auditor)
            st.session_state.last_loaded_file_bitmex = selected_file
            st.sidebar.success("✅ Dataset loaded!")

    elif load_mode == "🌐 Load from API" and load_api:
        df, client = load_data(
            start_date=str(start_date),
            end_date=str(end_date),
            symbol=symbol,
            bin_size=bin_size
        )
        client.source     = "bitmex"
        client.coin       = symbol
        client.bin_size   = bin_size
        client.start_date = str(start_date)
        client.end_date   = str(end_date)
        client.last_df    = df
        auditor = AugmentoClientAudit.from_client(df, _client=client, source="bitmex", verbose=False)
        store_session_data_bitmex(df, client, auditor)
        st.sidebar.success("✅ Dataset loaded!")

    # === AFTER DATA IS LOADED: ONLY BITMEX KEYS ===
    if "bitmex_df" in st.session_state and "bitmex_auditor" in st.session_state:
        df      = st.session_state.bitmex_df
        client  = st.session_state.bitmex_client
        auditor = st.session_state.bitmex_auditor

        st.sidebar.success(f"Loaded shape: {df.shape}")

        if store_in_session:
            if "saved_datasets" not in st.session_state:
                st.session_state.saved_datasets = []
            dataset_name = f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_{client.end_date}"
            if not any(d["name"] == dataset_name for d in st.session_state.saved_datasets):
                st.session_state.saved_datasets.append({
                    "name":     dataset_name,
                    "df":       df,
                    "client":   client,
                    "auditor":  auditor
                })

        # === KPIs ===
        n_rows, n_cols = df.shape
        n_missing = df.isnull().sum().sum()
        n_duplicates = df.duplicated(subset=["datetime"]).sum()
        score = max(0, round(100 - ((n_missing/(n_rows*n_cols))*50 + (n_duplicates/n_rows)*50),4))

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("🧮 Rows", f"{n_rows:,}")
        k2.metric("🧱 Columns", f"{n_cols:,}")
        k3.metric("❌ Missing", f"{n_missing:,}")
        k4.metric("🔁 Duplicates", f"{n_duplicates:,}")
        k5.metric("💯 Quality Score", f"{score}/100")

        # Export & Preview
        df_disp, fmt_col, dl_col = st.columns(3)
        with df_disp:
            full_prev = st.checkbox("Show full preview", key="bitmex_full_preview")
        with fmt_col:
            fmt = st.radio("", ["CSV","Parquet"], horizontal=True, label_visibility="collapsed", key="bitmex_export_format")
        with dl_col:
            prefix = f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_until_{client.end_date}"
            if fmt=="CSV":
                st.download_button("💾 Save as CSV", df.to_csv(index=False), f"{prefix}.csv", mime="text/csv")
            else:
                buf = io.BytesIO(); df.to_parquet(buf, index=False)
                st.download_button("💾 Save as Parquet", buf.getvalue(), f"{prefix}.parquet")

        st.dataframe(df if full_prev else df.head(500), use_container_width=True)

        # Missing + Visuals
        missing = df.isnull().sum()
        st.subheader("🔍 Missing Values per Column")
        if (m2 := missing[missing>0]).empty:
            st.success("✅ No columns with missing values")
        else:
            st.bar_chart(m2.sort_values(ascending=False), color="#FF4500")

        st.subheader("📊 Visual Summary")
        st.plotly_chart(plot_missing_heatmap(df, bin_size=client.bin_size), use_container_width=True)

        # top distributions fallback
        preferred = [c for c in ["open","high","low","close","trades"] if c in df.columns]
        cols = preferred if preferred else df.select_dtypes("number").columns.tolist() or df.columns.tolist()
        st.plotly_chart(plot_top_distributions(df[cols], top_n=5), use_container_width=True)

        st.plotly_chart(plot_total_trading_activity(df), use_container_width=True)

        if st.toggle("📋 Show Metadata", value=False, key="bitmex_show_metadata"):
            st.json({
                "source": client.source,
                "coin": client.coin,
                "bin_size": client.bin_size,
                "start_date": client.start_date,
                "end_date": client.end_date,
                "missing_intervals":    len(auditor.audit_report["missing_time_points"]),
                "duplicates":           len(auditor.audit_report["duplicate_timestamps"]),
                "flagged_columns":      auditor.audit_report.get("flagged_columns", []),
            })
