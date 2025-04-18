# views/wrangler_view.py

import streamlit as st
import pandas as pd
from augmento_datawrangler import AugmentoDataWrangler

def load_wrangler_view():

    st.sidebar.header("Data Wrangler Controls")

    st.header("🧩 Augmento Data Wrangler")
    st.caption("Load and merge multiple datasets interactively.")

    # Load or initialize wrangler in session
    if "wrangler" not in st.session_state:
        st.session_state.wrangler = AugmentoDataWrangler()

    wrangler = st.session_state.wrangler

    # Load saved session datasets (only once)
    if "saved_datasets" in st.session_state and not getattr(wrangler, "_session_loaded", False):
        wrangler.import_from_session(st.session_state["saved_datasets"])
        wrangler._session_loaded = True
        st.info(f"📂 Loaded {len(st.session_state['saved_datasets'])} saved datasets from session.")

    # === Upload ===
    uploaded_files = st.file_uploader(
        "📤 Upload CSV or Parquet Files", type=["csv", "parquet"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            name = uploaded_file.name
            tmp_path = f"temp_{name}"
            with open(tmp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                wrangler.load_dataset(tmp_path, name=name)
                st.success(f"✅ Loaded `{name}` successfully.")
            except Exception as e:
                st.error(f"❌ Failed to load `{name}`: {e}")

    # === Display Loaded Datasets ===
    if wrangler.datasets:
        st.subheader("📂 Loaded Datasets")
        for name, meta in wrangler.get_metadata().items():
            with st.expander(f"📄 {name}"):
                st.write(f"**Rows**: {meta['rows']}")
                st.write(f"**Columns**: {len(meta['columns'])}")
                st.code(", ".join(meta["columns"]))

        # === Join Logic ===
        if len(wrangler.datasets) >= 2:
            st.subheader("🔗 Join Configuration")

            common_keys = list(set.intersection(*[set(df.columns) for df in wrangler.datasets.values()]))
            join_keys = st.multiselect("🧩 Join on", options=common_keys, default=["datetime"])
            join_type = st.selectbox("🔀 Join type", ["inner", "outer", "left", "right"])

            if st.button("🔄 Join Datasets"):
                try:
                    joined = wrangler.join_datasets(keys=join_keys, how=join_type)
                    st.success(f"✅ Joined DataFrame with shape {joined.shape}")
                    st.session_state["joined_df"] = joined
                    st.session_state["joined_df_name"] = f"joined_{'_'.join(join_keys)}_{join_type}"
                except Exception as e:
                    st.error(f"❌ Join failed: {e}")

    else:
        st.info("📤 Upload at least two datasets to enable joining.")

    # === Show Persisted Joined Dataset (even after rerun) ===
    if "joined_df" in st.session_state:
        st.subheader("🧬 Persisted Joined Dataset")
        joined_df = st.session_state["joined_df"]
        st.write(f"**Shape**: {joined_df.shape}")
        st.dataframe(joined_df.head(300), use_container_width=True)

        # Download
        st.download_button(
            label="💾 Download Joined Dataset as CSV",
            data=joined_df.to_csv(index=False),
            file_name=f"{st.session_state.get('joined_df_name', 'joined_dataset')}.csv",
            mime="text/csv"
        )

        # Remove
        if st.button("❌ Remove Joined Dataset"):
            del st.session_state["joined_df"]
            if "joined_df_name" in st.session_state:
                del st.session_state["joined_df_name"]
            st.success("🗑️ Joined dataset removed from session.")
            st.rerun()

    # === Reset Button for Entire Wrangler ===
    if st.button("🧹 Reset Wrangler"):
        st.session_state.pop("wrangler", None)
        st.session_state.pop("joined_df", None)
        st.session_state.pop("joined_df_name", None)
        st.rerun()
