# pages/02_Session_Manager.py

import streamlit as st
from utils.filter_dataframe import filter_dataframe
from utils.column_summary import display_column_summary
import pandas as pd
import io


st.set_page_config(page_title="Session Manager", layout="wide")
st.title("🧹 Session Manager")

# --- 1) load persisted datasets ---
saved = st.session_state.get("saved_datasets", [])
if not saved:
    st.info("No datasets in session to manage.")
    st.stop()

# --- 2) choose one ---
names = [d["name"] for d in saved]
sel = st.selectbox("Select dataset to manage", names, key="session_manager_select")
entry = next(d for d in saved if d["name"] == sel)
df = entry["df"]

# --- 3) column‐selection tabs ---
st.markdown("---")
st.subheader("🔧 Select Columns for Filtering")

all_cols = df.columns.tolist()

tabs = st.tabs(["Multiselect", "Text Input"])
with tabs[0]:
    multi_keep = st.multiselect(
        "Pick columns to keep",
        all_cols,
        default=st.session_state.get("col_multi_keep", all_cols),
        key="col_multi_keep"
    )

with tabs[1]:
    text_input = st.text_input(
        "Enter column names (comma‑separated)",
        value=st.session_state.get("col_text_input", ""),
        key="col_text_input"
    ).strip()
    # parse and validate
    parsed = [c.strip() for c in text_input.split(",") if c.strip()]
    invalid = [c for c in parsed if c not in all_cols]
    if invalid:
        st.warning(f"Ignoring unknown columns: {', '.join(invalid)}")
    text_keep = [c for c in parsed if c in all_cols]

# decide which to use: text input (if non‑empty) overrides multiselect
if text_input:
    keep = text_keep
else:
    keep = multi_keep

if not keep:
    st.error("⚠️ No columns selected. Please pick at least one column.")
    st.stop()

# subset the DataFrame to only those columns
df_sub = df[keep].copy()

# --- 4) auto‑generate filters on the subset ---
st.markdown("---")
st.subheader("⚙️ Filter & Clean Data")
filtered = filter_dataframe(df_sub, key=sel)

# --- 5) preview & apply ---
st.markdown("### Preview Filtered Data")
# --- 3) KPIs for the selected dataset ---
st.subheader("📊 Dataset KPIs")
n_rows, n_cols = df.shape
n_missing = df.isnull().sum().sum()
# count duplicates in 'datetime' if it exists, else zero
n_duplicates = df.duplicated(subset=["datetime"]).sum() if "datetime" in df.columns else 0
total_cells = n_rows * n_cols
score = max(
    0,
    round(100 - ((n_missing / total_cells) * 50 + (n_duplicates / n_rows) * 50), 4)
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🧮 Rows", f"{n_rows:,}")
k2.metric("🧱 Columns", f"{n_cols:,}")
k3.metric("❌ Missing", f"{n_missing:,}")
k4.metric("🔁 Duplicates", f"{n_duplicates:,}")
k5.metric("💯 Quality Score", f"{score}/100")
st.dataframe(filtered.head(100), use_container_width=True)

# 8) after Apply button, or wherever makes sense:
display_column_summary(
    df=filtered,
    expander_label="📊 Column Summary"
)

# Export & Preview
df_display, fmt_toggle, dl_btn = st.columns(3)
with df_display:
    full_prev = st.checkbox("Show full preview", key="augmento_full_preview")
with fmt_toggle:
    fmt = st.radio("", ["CSV","Parquet"], horizontal=True, label_visibility= "collapsed", key="augmento_export_format")
with dl_btn:
    prefix = f"filtred_dataset"
    if fmt=="CSV":
        st.download_button("💾 Save as CSV", df.to_csv(index=False), f"{prefix}.csv", mime="text/csv")
    else:
        buf = io.BytesIO(); df.to_parquet(buf, index=False)
        st.download_button("💾 Save as Parquet", buf.getvalue(), f"{prefix}.parquet")

if st.button("🧽 Apply Filters to Session", key="apply_filters"):
    entry["df"] = filtered
    st.success(f"✅ Filters applied to '{sel}'")
