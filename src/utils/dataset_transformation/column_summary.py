# utils/column_summary.py

import pandas as pd
import streamlit as st

def display_column_summary(
    df: pd.DataFrame,
    expander_label: str = "🔎 Column Summary"
):
    """
    Wraps your numeric / categorical column summary (with inline charts) in an expander.
    """
    with st.expander(expander_label, expanded=False):
        if df.empty:
            st.info("No data to summarize.")
            return

        # split columns
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c].dtype)]
        cat_cols = [c for c in df.columns if c not in num_cols]

        tabs = st.tabs(["Numeric Columns", "Categorical Columns"])

        # Numeric tab
        with tabs[0]:
            if not num_cols:
                st.info("No numeric columns to summarize.")
            else:
                rows = []
                for c in num_cols:
                    mn = df[c].min()
                    mx = df[c].max()
                    rows.append({
                        "column": c,
                        "dtype": str(df[c].dtype),
                        "min_max": f"{mn} – {mx}",
                        "values": df[c].tolist(),
                    })
                summary_df = pd.DataFrame(rows)

                st.dataframe(
                    summary_df,
                    hide_index=True,
                    column_config={
                        "column": "Column",
                        "dtype": "Data Type",
                        "min_max": "Min – Max",
                        "values": st.column_config.LineChartColumn(
                            "Values over Rows"
                        ),
                    },
                    use_container_width=True
                )

        # Categorical tab
        with tabs[1]:
            if not cat_cols:
                st.info("No categorical columns to summarize.")
            else:
                rows = []
                for c in cat_cols:
                    vc = df[c].value_counts()
                    top10 = vc.head(10)
                    rows.append({
                        "column": c,
                        "dtype": str(df[c].dtype),
                        "min_max": "",
                        "counts": top10.tolist(),
                    })
                summary_df = pd.DataFrame(rows)

                st.dataframe(
                    summary_df,
                    hide_index=True,
                    column_config={
                        "column": "Column",
                        "dtype": "Data Type",
                        "min_max": "Min – Max",
                        "counts": st.column_config.BarChartColumn(
                            "Top‑10 Value Counts"
                        ),
                    },
                    use_container_width=True
                )
