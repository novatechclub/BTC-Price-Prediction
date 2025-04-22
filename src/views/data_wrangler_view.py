# data_wrangler_view.py

import streamlit as st
import pandas as pd
from utils.augmento_datawrangler import AugmentoDataWrangler
from pathlib import Path
import io

def load_wrangler_view():
    # Initialize or load wrangler so sidebar actions have access
    if "wrangler" not in st.session_state:
        st.session_state.wrangler = AugmentoDataWrangler()
    wrangler = st.session_state.wrangler

    # --- Sidebar Controls ---
    st.sidebar.header("🧩 Data Wrangler Controls")

    # Browse preloaded datasets
    st.sidebar.subheader("📦 Preloaded Datasets")
    pre_paths = sorted(Path("preloaded_datasets").glob("*.*"))
    bitmex_paths = sorted(Path("preloaded_datasets_bitmex").glob("*.*"))
    all_pre = pre_paths + bitmex_paths
    display_names = [p.name for p in all_pre]
    selected_pre = st.sidebar.multiselect("Select preloaded files", options=display_names)
    if selected_pre and st.sidebar.button("🔄 Load Preloaded Files", key="load_preloaded"):
        for name in selected_pre:
            path = next(p for p in all_pre if p.name == name)
            try:
                df = pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)
                wrangler.load_dataset(str(path), name=name)
                st.sidebar.success(f"✅ Loaded `{name}` successfully.")
                st.session_state.setdefault("saved_datasets", []).append({"name": name, "df": df})
            except Exception as e:
                st.sidebar.error(f"❌ Failed to load `{name}`: {e}")
    st.sidebar.markdown("---")

    # File uploader in sidebar
    uploaded_files = st.sidebar.file_uploader(
        "📤 Upload CSV or Parquet Files", type=["csv", "parquet"],
        accept_multiple_files=True
    )

    # Reset Wrangler button in sidebar
    if st.sidebar.button("🧹 Reset Wrangler", key="reset_sidebar"):
        for key in ["wrangler", "saved_datasets", "joined_df", "joined_df_name"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.sidebar.markdown("---")

    # --- Main Page ---
    st.header("🧩 Augmento Data Wrangler")
    st.caption("Load and merge multiple datasets interactively.")

    # Import session datasets once
    if "saved_datasets" in st.session_state and not getattr(wrangler, "_session_loaded", False):
        wrangler.import_from_session(st.session_state["saved_datasets"])
        wrangler._session_loaded = True
        st.info(f"📂 Loaded {len(st.session_state['saved_datasets'])} session datasets.")

    # Handle uploads
    if uploaded_files:
        for uploaded_file in uploaded_files:
            name = uploaded_file.name
            tmp_path = f"temp_{name}"
            with open(tmp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                wrangler.load_dataset(tmp_path, name=name)
                st.success(f"✅ Loaded `{name}` successfully.")
                st.session_state.setdefault("saved_datasets", []).append({"name": name, "df": wrangler.datasets[name]})
            except Exception as e:
                st.error(f"❌ Failed to load `{name}`: {e}")

    # === Display Loaded Datasets ===
    if wrangler.datasets:
        st.subheader("📂 Loaded Datasets")
        for name, meta in wrangler.get_metadata().items():
            cols = st.columns([8, 1])
            with cols[0]:
                with st.expander(f"📄 {name}"):
                    st.write(f"**Rows**: {meta['rows']}")
                    st.write(f"**Columns**: {len(meta['columns'])}")
                    st.code(", ".join(meta["columns"]))

                    # --- Column-level Operations ---
                    to_drop = st.multiselect(
                        "🗑️ Drop columns", options=meta['columns'], key=f"drop_cols_{name}"
                    )
                    if st.button("Drop", key=f"drop_btn_{name}"):
                        wrangler.drop_columns(name, to_drop)
                        st.rerun()

                    old_col = st.selectbox(
                        "✏️ Rename column (select existing)", options=meta['columns'], key=f"rename_old_{name}"
                    )
                    new_col = st.text_input(
                        "New column name", key=f"rename_new_{name}"
                    )
                    if st.button("Rename", key=f"rename_btn_{name}") and new_col:
                        wrangler.rename_column(name, old_col, new_col)
                        st.rerun()

                    select_cols = st.multiselect(
                        "✔️ Select columns", options=meta['columns'], default=meta['columns'], key=f"select_cols_{name}"
                    )
                    if st.button("Apply", key=f"select_btn_{name}"):
                        wrangler.select_columns(name, select_cols)
                        st.rerun()

            if cols[1].button("❌", key=f"del_loaded_{name}"):
                wrangler.datasets.pop(name, None)
                if "saved_datasets" in st.session_state:
                    st.session_state["saved_datasets"] = [
                        d for d in st.session_state["saved_datasets"] if d["name"] != name
                    ]
                st.rerun()

        # === Join Logic ===
        if len(wrangler.datasets) >= 2:
            st.subheader("🔗 Join Configuration")
            common_keys = list(
                set.intersection(*[set(df.columns) for df in wrangler.datasets.values()])
            )
            # default to all keys to ensure valid default
            join_keys = st.multiselect(
                "🧩 Join on", options=common_keys, default=common_keys
            )
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

    # === Show Persisted Joined Dataset ===
    if "joined_df" in st.session_state:
        st.subheader("🧬 Joined Dataset Preview")
        joined_df = st.session_state["joined_df"]
        st.write(f"**Shape**: {joined_df.shape}")
        df_display, format_toggle, file_download_button = st.columns(3)
        with df_display:
            full_dataframe_prev = st.checkbox("Show full preview")
        with format_toggle:
            export_format = st.radio("Choose a format", ["CSV", "Parquet"], horizontal=True, label_visibility="collapsed")
        with file_download_button:
            if export_format == "CSV":
                st.download_button(
                    label="💾 Download Joined Dataset as CSV",
                    data=joined_df.to_csv(index=False),
                    file_name=f"{st.session_state.get('joined_df_name', 'joined_dataset')}.csv",
                    mime="text/csv"
                )
            else:
                buffer = io.BytesIO()
                joined_df.to_parquet(buffer, index=False)
                st.download_button("💾 Download as Parquet",
                                   buffer.getvalue(),
                                   f"{st.session_state.get('joined_df_name', 'joined_dataset')}.parquet")
        st.dataframe(joined_df if full_dataframe_prev else joined_df.head(500), use_container_width=True)
        if st.button("❌ Remove Joined Dataset"):
            st.session_state.pop("joined_df", None)
            st.session_state.pop("joined_df_name", None)
            st.success("🗑️ Joined dataset removed.")
            st.rerun()
