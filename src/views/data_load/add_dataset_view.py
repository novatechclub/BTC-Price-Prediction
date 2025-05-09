import streamlit as st
import polars as pl
import pandas as pd
from pathlib import Path
import streamlit as st
import polars as pl
import pandas as pd
from pathlib import Path

DATA_DIR = Path("app_assets/preloaded_assets/time_series_preloaded")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def store_uploaded_dataset(df, name: str):
    if isinstance(df, pl.DataFrame):
        df = df.to_pandas()
    
    st.session_state.df_uploaded = df
    st.session_state.last_uploaded_name = name

    if "saved_datasets" not in st.session_state:
        st.session_state.saved_datasets = []

    if not any(d["name"] == name for d in st.session_state.saved_datasets):
        st.session_state.saved_datasets.append({
            "name": name,
            "df": df,
        })


def load_add_dataset_view():
    st.subheader("📤 Upload & Add Custom Dataset")
    
    st.markdown(
        "Upload a `.csv` or `.parquet` file. It will be **converted and stored as a `.parquet` file** "
        f"in `{DATA_DIR}`."
    )

    uploaded_file = st.file_uploader("Upload CSV or Parquet file", type=["csv", "parquet"])

    if uploaded_file:
        file_name = st.text_input("📝 Enter a name for your dataset (no extension)", value=uploaded_file.name.split(".")[0])

        if file_name:
            if st.button("📥 Save Dataset"):
                try:
                    # Load into Polars
                    if uploaded_file.name.endswith(".csv"):
                        df = pl.read_csv(uploaded_file)
                        df = df.to_pandas()  # Convert to Pandas DataFrame
                    else:
                        df = pl.read_parquet(uploaded_file)
                        df = df.to_pandas()

                    # Save to disk as Parquet
                    file_path = DATA_DIR / f"{file_name}.parquet"
                    df.to_parquet(str(file_path))

                    # Store in session
                    store_uploaded_dataset(df, file_name)

                    st.success(f"✅ Dataset saved as {file_path.name}")
                    st.markdown("### 🔍 Preview")
                    st.dataframe(df.head(100), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to upload dataset: {e}")

