import streamlit as st
from utils.augmento_client import AugmentoAPIClient
from utils.augmento_audit import AugmentoClientAudit
from datetime import datetime
import pandas as pd

def load_api_view():
    st.header("📥 Load & Inspect Dataset")

    @st.cache_data(show_spinner="Caching data...", persist="disk")
    def load_data(start_date, end_date, source, coin, bin_size):
        client = AugmentoAPIClient()
        df = client.download_full_dataset(
            start_date=start_date,
            end_date=end_date,
            source=source,
            coin=coin,
            bin_size=bin_size
        )
        return df, client

    # --- Sidebar Controls ---
    client_summary = AugmentoAPIClient().get_summary()

    st.sidebar.header("Data Loader Controls")

    default_coin = "bitcoin"
    default_source = "twitter"
    default_bin_size = "1H"
    coins = client_summary["Coins"]
    sources = client_summary["Sources"]
    bin_sizes = list(client_summary["Bin_sizes"].keys())

    default_coin_index = coins.index(default_coin) if default_coin in coins else 0
    default_source_index = sources.index(default_source) if default_source in sources else 0
    default_bin_size_index = list(bin_sizes).index(default_bin_size) if default_bin_size in bin_sizes else 0

    st.sidebar.markdown("Select the parameters to load a new dataset from the API.")
    start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2024-11-01"))
    end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2025-02-01"))
    source = st.sidebar.selectbox("Platform", sources, index=default_source_index)
    coin = st.sidebar.selectbox("Coin", coins, index=default_coin_index)
    bin_size = st.sidebar.selectbox("Bin Size", bin_sizes, index=default_bin_size_index)
    load_button = st.sidebar.button("📥 Load & Audit Dataset")

    if st.sidebar.button("🔄 Reset Dashboard"):
        st.session_state.clear()
        st.rerun()

    # --- Action ---
    # --- Load button or use session state ---
    if load_button:
        with st.spinner("Loading and auditing data..."):
            df, client = load_data(
                start_date=str(start_date),
                end_date=str(end_date),
                source=source,
                coin=coin,
                bin_size=bin_size
            )
            auditor = AugmentoClientAudit.from_client(df, client, source=source, verbose=False)

            # Store in session state
            st.session_state.df = df
            st.session_state.client = client
            st.session_state.auditor = auditor
            st.success("✅ Dataset loaded and audited!")

    # --- Show dashboard if data is available ---
    if "df" in st.session_state and "auditor" in st.session_state:
        df = st.session_state.df
        client = st.session_state.client
        auditor = st.session_state.auditor

        # === Output ===
        st.success(f"Loaded dataset with shape: {df.shape}")

        # User opt-in to persist dataset
        st.subheader("📌 Add to Data Wrangler")
        store_in_session = st.checkbox("✅ Add this dataset to the Wrangler session", key="store_checkbox")

        if store_in_session:
            if "saved_datasets" not in st.session_state:
                st.session_state.saved_datasets = []

            # Unique name to identify the dataset
            dataset_name = f"{client.source}_{client.coin}_{client.bin_size}_{client.start_date}_{client.end_date}"
            if not any(d["name"] == dataset_name for d in st.session_state.saved_datasets):
                st.session_state.saved_datasets.append({
                    "name": dataset_name,
                    "df": df
                })
                st.success(f"📌 Added `{dataset_name}` to session.")
            else:
                st.info(f"📂 Dataset `{dataset_name}` is already stored.")

        # === KPIs ===
        with st.container():
            st.subheader("📌 Dataset Summary KPIs")

            n_rows, n_cols = df.shape
            n_missing = df.isnull().sum().sum()
            n_duplicates = df.duplicated(subset=["datetime"]).sum()

            total_cells = n_rows * n_cols
            missing_penalty = (n_missing / total_cells) * 50
            duplicate_penalty = (n_duplicates / n_rows) * 50
            score = max(0, round(100 - (missing_penalty + duplicate_penalty), 1))

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("🧮 Rows", f"{n_rows:,}")
            k2.metric("🧱 Columns", f"{n_cols:,}")
            k3.metric("❌ Missing Values", f"{n_missing:,}")
            k4.metric("🔁 Duplicates", f"{n_duplicates:,}")
            k5.metric("💯 Quality Score", f"{score}/100")

        # === Data Preview ===
        st.subheader("📋 Raw Data Preview")
        if st.checkbox("Show full dataframe preview"):
            st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df.head(500), use_container_width=True)

        # === Download Button ===
        st.download_button(
            label="💾 Download Dataset as CSV",
            data=df.to_csv(index=False),
            file_name=f"{client.source}_{client.coin}_{client.bin_size}_dataset.csv",
            mime="text/csv"
        )

        # === Missing Value Chart ===
        st.subheader("🔍 Missing Values per Column")
        missing_by_col = df.isnull().sum()
        missing_by_col = missing_by_col[missing_by_col > 0].sort_values(ascending=False)

        if not missing_by_col.empty:
            st.bar_chart(missing_by_col)
        else:
            st.success("✅ No missing values found.")

        st.subheader("📊 Visual Summary")
        figures = auditor.plot_visual_summary(top_n_columns=5)
        for fig in figures:
            st.pyplot(fig)

        st.subheader("🧾 Session Metadata")
        with st.expander("📌 Client Metadata"):
            st.write(f"**Source**: {client.source}")
            st.write(f"**Coin**: {client.coin}")
            st.write(f"**Bin Size**: {client.bin_size}")
            st.write(f"**Start Date**: {client.start_date}")
            st.write(f"**End Date**: {client.end_date}")
            if hasattr(client, "last_df"):
                st.write(f"**Dataset Shape**: {client.last_df.shape}")
            else:
                st.write(f"**Dataset Shape**: {df.shape}")

        st.subheader("✅ Audit Summary")
        st.json({
            "missing_intervals": len(auditor.audit_report["missing_time_points"]),
            "duplicate_timestamps": len(auditor.audit_report["duplicate_timestamps"]),
            "missing_columns": len(auditor.audit_report.get("missing_columns", [])),
            "flagged_columns": auditor.audit_report.get("flagged_columns", [])
        })
        
    else:
        st.info("👈 Use the sidebar to load a dataset.")
