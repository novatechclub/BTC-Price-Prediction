# utils/filter_dataframe.py

import streamlit as st
import pandas as pd

def filter_dataframe(df: pd.DataFrame, key: str = None) -> pd.DataFrame:
    """
    Auto‑generate a filter UI on every column in df, based on its dtype.
    Returns the filtered dataframe.
    """
    df = df.copy()
    modify = st.checkbox("🔍 Show filters", key=f"use_filters_{key}")
    if not modify:
        return df

    for col in df.columns:
        col_type = df[col].dtype

        # --- datetime columns: compare on date only ---
        if pd.api.types.is_datetime64_any_dtype(col_type):
            # strip tz so that .dt.date always works
            series = df[col]
            if series.dt.tz is not None:
                series = series.dt.tz_localize(None)

            # default to full span
            min_date = series.min().date()
            max_date = series.max().date()
            start, end = st.date_input(
                f"{col} date range",
                [min_date, max_date],
                key=f"filter_{key}_{col}"
            )
            # compare pure python dates
            dates = series.dt.date
            mask = (dates >= start) & (dates <= end)
            df = df[mask]

        # --- numeric columns: slider ---
        elif pd.api.types.is_numeric_dtype(col_type):
            min_val, max_val = float(df[col].min()), float(df[col].max())
            lo, hi = st.slider(
                f"{col} range",
                min_val, max_val,
                (min_val, max_val),
                key=f"filter_{key}_{col}"
            )
            df = df[df[col].between(lo, hi)]

        # --- categorical or small‐cardinality: multiselect ---
        elif pd.api.types.is_categorical_dtype(col_type) or df[col].nunique() < 20:
            options = df[col].dropna().unique().tolist()
            sel = st.multiselect(
                f"{col} values",
                options,
                default=options,
                key=f"filter_{key}_{col}"
            )
            df = df[df[col].isin(sel)]

        # --- everything else: substring search ---
        else:
            txt = st.text_input(
                f"Search {col}",
                key=f"filter_{key}_{col}"
            )
            if txt:
                df = df[df[col].astype(str).str.contains(txt, na=False)]

    return df
