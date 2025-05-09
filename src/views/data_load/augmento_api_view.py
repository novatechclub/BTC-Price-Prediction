# views/augmento_api_view.py
import streamlit as st
from utils.clients.augmento_client import NTCTasAugmentoClient
from utils.clients.augmento_audit import NTCTapClientAudit
import pandas as pd
from pathlib import Path
import io

from utils.visualization.visual_utils import (
    plot_missing_heatmap,
    plot_top_distributions,
    plot_total_activity,
)

PRELOADED_FILES = Path("app_assets/preloaded_assets/augmento_preloaded_datasets")


def load_api_view():
    st.subheader("📥 Load & Inspect Dataset (Augmento)")

    @st.cache_data(show_spinner="Fetching API Summary")
    def get_api_summary():
        return NTCTasAugmentoClient().get_summary()

    @st.cache_data(show_spinner="Scanning Preloaded Files")
    def get_preloaded_datasets():
        folder = PRELOADED_FILES
        return sorted(folder.glob("*.parquet"))

    @st.cache_data(show_spinner="Downloading Data") #, persist="disk"
    def load_data(start_date, end_date, source, coin, bin_size):
        client = NTCTasAugmentoClient()
        df = client.download_full_dataset(
            start_date=start_date,
            end_date=end_date,
            source=source,
            coin=coin,
            bin_size=bin_size
        )
        return df, client

    def store_session_data_augmento(df, client, auditor):
        st.session_state.df_augmento      = df
        st.session_state.client_augmento  = client
        st.session_state.auditor_augmento = auditor

    client_summary = get_api_summary()

    # === CONTROLS IN MAIN CONTENT ===
    with st.expander("⚙️ Controls", expanded=True):
        load_mode = st.radio(
            "Choose Load Mode",
            ["📦 Preloaded Dataset", "🌐 Load from API"],
            key="augmento_load_mode"
        )

        if load_mode == "📦 Preloaded Dataset":
            preloaded_files = get_preloaded_datasets()
            selected_file = st.selectbox(
                "Select Preloaded Dataset",
                [f.name for f in preloaded_files],
                key="augmento_selected_file"
            )
            store_in_session = st.checkbox(
                "✅ Add to current Session",
                key="augmento_store_checkbox_1"
            )
            load_preloaded = st.button(
                "📥 Load Selected File",
                key="augmento_file_load"
            )
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

            store_in_session = st.checkbox(
                "✅ Add to Wrangler Session",
                key="augmento_store_checkbox_2"
            )
            start_date = st.date_input(
                "Start Date",
                value=pd.to_datetime("2024-11-01"),
                key="augmento_start_date"
            )
            end_date   = st.date_input(
                "End Date",
                value=pd.to_datetime("2025-02-01"),
                key="augmento_end_date"
            )
            source = st.selectbox("Platform", sources, key="augmento_source", index=default_source_index)
            coin   = st.selectbox("Coin",    coins,   key="augmento_coin", index=default_coin_index)
            bin_size = st.selectbox("Bin Size", bin_sizes, key="augmento_bin_size", index=default_bin_size_index)
            load_api  = st.button("📥 Load & Inspect Dataset", key="augmento_load_btn")

    # === DATA LOADING LOGIC ===
    if load_mode == "📦 Preloaded Dataset" and load_preloaded:
        if st.session_state.get("last_loaded_file_augmento") != selected_file:
            df = pd.read_parquet(f"{str(PRELOADED_FILES)}/{selected_file}")

            # derive metadata
            df["datetime"] = pd.to_datetime(df["datetime"])
            start = df["datetime"].min().strftime("%Y-%m-%d")
            end   = df["datetime"].max().strftime("%Y-%m-%d")

            client = NTCTasAugmentoClient()
            client.source     = df["source"].iloc[0]
            client.coin       = df["coin_type"].iloc[0]
            client.bin_size   = df["bin_size"].iloc[0].upper()
            client.start_date = start
            client.end_date   = end
            client.last_df    = df

            auditor = NTCTapClientAudit.from_client(
                df, _client=client, source=client.source, verbose=False
            )
            store_session_data_augmento(df, client, auditor)
            st.session_state.last_loaded_file_augmento = selected_file
            st.sidebar.success("✅ Dataset loaded!")

    elif load_mode == "🌐 Load from API" and load_api:
        df, client = load_data(
            start_date=str(start_date),
            end_date=str(end_date),
            source=source,
            coin=coin,
            bin_size=bin_size
        )
        auditor = NTCTapClientAudit.from_client(
            df, _client=client, source=source, verbose=False
        )
        store_session_data_augmento(df, client, auditor)
        st.sidebar.success("✅ Dataset loaded!")

    # === AFTER DATA IS LOADED: ONLY AUGMENTO KEYS ===
    if "df_augmento" in st.session_state and "auditor_augmento" in st.session_state:
        df      = st.session_state.df_augmento
        client  = st.session_state.client_augmento
        auditor = st.session_state.auditor_augmento

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
        df_display, fmt_toggle, dl_btn = st.columns(3)
        with df_display:
            full_prev = st.checkbox("Show full preview", key="augmento_full_preview")
        with fmt_toggle:
            fmt = st.radio("Select File-Format", ["CSV","Parquet"], horizontal=True, label_visibility= "collapsed", key="augmento_export_format")
        with dl_btn:
            if client:
                prefix = f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_until_{client.end_date}"
            else:
                prefix = st.session_state.get("current_dataset_name", "uploaded_dataset")            
            
            if fmt=="CSV":
                st.download_button("💾 Save as CSV", df.to_csv(index=False), f"{prefix}.csv", mime="text/csv")
            else:
                buf = io.BytesIO(); df.to_parquet(buf, index=False)
                st.download_button("💾 Save as Parquet", buf.getvalue(), f"{prefix}.parquet")

        with st.expander("🗒️ Check Table", expanded=False):
            st.dataframe(df if full_prev else df.head(100), use_container_width=True)

        # Missing + Visuals
        missing = df.isnull().sum()
        #st.subheader("🔍 Missing Values per Column")
        with st.expander("🔍 Missing Values per Column", expanded=False):
            if (m2 := missing[missing>0]).empty:
                st.success("✅ No columns with missing values")
            else:
                st.bar_chart(m2.sort_values(ascending=False), color="#FF4500")

        #st.subheader("📊 Visual Summary")
        with st.expander("📊 Visual Summary", expanded=False):
            st.plotly_chart(plot_missing_heatmap(df, bin_size=client.bin_size), use_container_width=True)

            # top distributions fallback
            preferred = [c for c in ["open","high","low","close","trades"] if c in df.columns]
            if preferred:
                cols = preferred
            else:
                nums = df.select_dtypes("number").columns.tolist()
                cols = nums if nums else df.columns.tolist()
            st.plotly_chart(plot_top_distributions(df[cols], top_n=5), use_container_width=True)

            st.plotly_chart(plot_total_activity(df), use_container_width=True)

        if st.toggle("📋 Show Metadata", value=False, key="augmento_meta_toggle"):
            st.json({
                "source": client.source,
                "coin": client.coin,
                "bin_size": client.bin_size,
                "start_date": client.start_date,
                "end_date": client.end_date,
                "missing_intervals": len(auditor.audit_report["missing_time_points"]),
                "duplicates":        len(auditor.audit_report["duplicate_timestamps"]),
                "flagged_columns":   auditor.audit_report.get("flagged_columns", []),
            })
