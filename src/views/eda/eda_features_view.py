import streamlit as st
import polars as pl
import pandas as pd
from pathlib import Path
import io
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from utils.features.data_meta_model import NTCTapDataMetaModel, DataMetaModelPolars


def load_dataset_summary(dataset_name, selected_df):
    st.success(f"✅ Dataset loaded: {dataset_name} — Shape: {selected_df.shape}")

    # display KPIs next to each other
    col1, col2= st.columns([1, 3])
    with col1:
        # add KPIs for the dataset
        st.markdown("---")
        st.subheader("📈 Dataset KPIs")
        st.metric("Rows", selected_df.shape[0])
        st.metric("Columns", selected_df.shape[1])
        st.metric("Memory Usage", f"{selected_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        st.metric("Missing Values", selected_df.isnull().sum().sum())
        st.metric("Duplicates", selected_df.duplicated().sum())
        #st.metric("Min Date", f"{selected_df.index.min()}")
        #st.metric("Max Date", f"{selected_df.index.max()}")

        # categorical columns
        categorical_types = ["category", "string", "object"]  # must further check cardinality or actual data
        cat_cols = selected_df.select_dtypes(include=categorical_types).columns.tolist()
        if cat_cols:
            st.metric("Categorical Columns", len(cat_cols))

        # numerical columns
        numeric_types = [
            "int", "int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64",
            "float", "float16", "float32", "float64",
            "Int8", "Int16", "Int32", "Int64",  # pandas nullable integer
            "UInt8", "UInt16", "UInt32", "UInt64"
        ]
        num_cols = selected_df.select_dtypes(include=numeric_types).columns.tolist()
        if num_cols:
            st.metric("Numerical Columns", len(num_cols))
        #st.metric("Numerical Values", selected_df[num_cols].nunique().sum())

        # datetime columns
        date_format_types = ["timedelta64", "timedelta", "datetime64", "datetime"
            #"datetime64[ns]", "datetime64[ms]", "datetime64[s]", "datetime64[us]", "datetime64[μs]",
            #"datetime64[D]", "datetime64[M]", "datetime64[Y]", "datetime64[h]", "datetime64[m]",
            #"datetime64[ns, UTC]", "datetime64[ns, tz]",
            #"timedelta64[ns]", "timedelta64[us]", "timedelta64[ms]", "timedelta64[s]", "timedelta64[m]",
            #"timedelta64[h]", "timedelta64[D]", "timedelta64[W]", "timedelta64[M]", "timedelta64[Y]"
        ]
        dt_cols = selected_df.select_dtypes(include=date_format_types).columns.tolist()
        if dt_cols:
            st.metric("Datetime Columns", len(dt_cols))
        #st.metric("Datetime Values", selected_df[dt_cols].nunique().sum())

        # boolean columns
        boolean_types = ["bool", "boolean"]  # pandas includes nullable "boolean"
        bool_cols = selected_df.select_dtypes(include=boolean_types).columns.tolist()
        if bool_cols:
            st.metric("Boolean Columns", len(bool_cols))
        #st.metric("Boolean Values", selected_df[bool_cols].nunique().sum())

        # other columns
        other_cols = selected_df.select_dtypes(exclude=["object", "complex", "number",]).columns.tolist()
        if other_cols:
            st.metric("Other Columns", len(other_cols))
        #st.metric("Other Values", selected_df[other_cols].nunique().sum())
        # display data types
        #st.metric("Data Types", selected_df.dtypes.to_dict())

    with col2:
        st.markdown("---")
        st.subheader("📊 Data Overview")

        # Dataset Summary
        with st.expander("📄 Dataset Summary Report"):
            st.write("Some basic statistics about the dataset here to copy into report.")

        with st.expander("🗺️ Missing Values Heatmap"):
            st.write("Visualize missing data across the dataset. Use the options below to adjust.")

            # Calculate missing percentages
            # missing_summary = selected_df.isnull().mean() * 100
            # 
            # # Plot as horizontal bar chart
            # fig, ax = plt.subplots(figsize=(5, len(missing_summary) * 0.4))
            # sns.barplot(x=missing_summary.values.flatten(), y=missing_summary.index, palette="viridis", ax=ax)
            # ax.set_xlim(0, 100)  # ensuring clean 0–100% scale
            # ax.set_xlabel("Missing Value Percentage")
            # ax.set_ylabel("Features")
            # ax.set_title("Missing Data per Feature")
            # st.pyplot(fig)

            # Compute missing percentage
            missing_summary = selected_df.isnull().mean() * 100
            missing_df = missing_summary.reset_index()
            missing_df.columns = ["Feature", "Missing %"]
            missing_df.sort_values("Missing %", ascending=True, inplace=True)

            # Normalize color scale
            norm = colors.Normalize(vmin=0, vmax=missing_df["Missing %"].max())
            cmap = plt.get_cmap("viridis")

            bar_colors = [cmap(norm(val)) for val in missing_df["Missing %"]]

            # Plot
            fig, ax = plt.subplots(figsize=(6, len(missing_df) * 0.4))
            ax.barh(missing_df["Feature"], missing_df["Missing %"], color=bar_colors)

            ax.set_xlim(0, 100)
            ax.set_xlabel("Missing Value Percentage")
            ax.set_title("Missing Data per Feature")

            st.pyplot(fig)

        st.markdown("---")

        # Feature Summary
        meta_model = DataMetaModelPolars(pl.from_pandas(selected_df))

        st.subheader("🧬 Feature Summary")
        selected_features = meta_model.df_features


        for feature in selected_features:
            with st.expander(f"🔎 {feature}"):
                stats = meta_model.summarize(feature)  # on-demand summarization
                if stats:
                    st.json(stats)
                else:
                    st.info("No summary available.")

                    