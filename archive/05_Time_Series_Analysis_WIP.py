# pages/1_Time_Series_Analysis.py
# 
# import streamlit as st
# import pandas as pd
# from pathlib import Path
# 
# 
# from utils.time_series import (
#     data_wrangling as dw,
#     feature_engineering as fe,
#     label_processing as lp,
#     anomaly_detection as ad,
#     visualization as vis
# )
# 
# import featuretools as ft
# 
# st.set_page_config(layout="wide")
# st.title("📈🧠 Time Series Analysis (work in progress)")
# 
# # Step 1: File selection or upload
# st.header("1. Upload or Select Data")
# 
# data_option = st.radio("Choose data source:", ("Upload file", "Use existing dataset"))
# if data_option == "Upload file":
#     uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
# else:
#     # Collect preloaded dataset paths
#     pre_paths = sorted(Path("app_assets/augmento_preloaded_datasets").glob("*.*"))
#     bitmex_paths = sorted(Path("app_assets/bitmex_preloaded_datasets").glob("*.*"))
#     all_pre = pre_paths + bitmex_paths
# 
#     # Create display names for the dropdown
#     display_names = [p.name for p in all_pre]
# 
#     # Sidebar selection
#     selected_name = st.sidebar.selectbox("Select preloaded file", options=display_names)
# 
#     # Find the corresponding path
#     selected_path = next(p for p in all_pre if p.name == selected_name)
# 
#     # Load the file
#     df = pd.read_parquet(selected_path)
# 
# if 'df' in locals():
#     st.success("✅ Data loaded!")
#     st.write(df.head())
# 
#     # Step 2: Data Wrangling
#     datetime_col = st.selectbox("Select datetime column:", df.columns, index=0)
#     wrangler = dw.DataWrangling(df, datetime_col)
#     df = wrangler.df
# 
#     tab1, tab2, tab3, tab4, tab5 = st.tabs([
#         "🛠️ Feature Engineering",
#         "🏷️ Label Processing",
#         "🚨 Anomaly Detection",
#         "📊 Visualization",
#         "📄 Final Dataset Preview"
#     ])
# 
#     # =========================
#     with tab1:
#         st.header("🛠️ Feature Engineering")
#         cols_to_engineer = st.multiselect("Select columns for feature engineering", df.columns)
# 
#         if st.button("➕ Add Lag Features") and cols_to_engineer:
#             df = fe.add_lag_features(df, cols_to_engineer)
#             st.success("Lag features added.")
# 
#         if cols_to_engineer:
#             fft_col = st.selectbox("Select column for FFT features", cols_to_engineer)
#             fft_feats = fe.add_fft_features(df, fft_col)
#             st.write("Top FFT features:")
#             st.json(fft_feats.to_dict())
# 
#             slope_col = st.selectbox("Column for Slope", cols_to_engineer)
#             df = fe.add_slope_feature(df, slope_col)
#             st.success("Slope feature added.")
# 
#         st.subheader("⚙️ Automated Feature Engineering (Featuretools)")
#         use_afe = st.checkbox("Run automated feature engineering using Featuretools")
# 
#         all_agg_primitives = sorted(ft.list_primitives().query("type == 'aggregation'")['name'].tolist())
#         all_trans_primitives = sorted(ft.list_primitives().query("type == 'transform'")['name'].tolist())
# 
#         if use_afe:
#             time_col = st.selectbox("Select time index column", df.columns)
#             afe_depth = st.slider("Max Feature Depth", 1, 3, 1)
# 
#             selected_agg = st.multiselect("Aggregation Primitives", all_agg_primitives, default=["mean", "std"])
#             selected_trans = st.multiselect("Transform Primitives", all_trans_primitives, default=["month", "day", "weekday"])
# 
#             if st.button("Run Featuretools"):
#                 st.info("Running automated feature engineering...")
#                 df_afe = fe.auto_feature_engineering(
#                     df.reset_index(), 
#                     time_index=time_col,
#                     max_depth=afe_depth,
#                     agg_primitives=selected_agg,
#                     trans_primitives=selected_trans
#                 )
#                 st.success("Automated feature engineering complete!")
#                 st.write(df_afe.head())
#                 df = df_afe  # Optionally replace df for future steps
# 
#     # =========================
#     with tab2:
#         st.header("🏷️ Label Preprocessing")
#         price_col = st.selectbox("Select price column to generate labels", df.columns)
#         horizon = st.slider("Prediction Horizon (steps ahead)", 1, 10, 3)
#         df = lp.create_binary_return_label(df, price_col, horizon)
#         st.write("Label Distribution:")
#         dist = lp.plot_label_distribution(df)
# 
#     # =========================
#     with tab3:
#         st.header("🚨 Anomaly Detection")
#         anomaly_col = st.selectbox("Select column to detect anomalies", df.columns)
#         method = st.radio("Anomaly Detection Method", ("Z-score", "IQR"))
# 
#         if method == "Z-score":
#             anomalies = ad.detect_anomalies_zscore(df, anomaly_col)
#         else:
#             anomalies = ad.detect_anomalies_iqr(df, anomaly_col)
# 
#         st.write(f"Detected {len(anomalies)} anomalies.")
#         ad.plot_anomalies(df, anomaly_col, anomalies)
# 
#     # =========================
#     with tab4:
#         st.header("📊 Time Series Visualization")
#         vis_col = st.selectbox("Select a column to visualize:", df.columns)
# 
#         # Date range filter
#         st.subheader("🔍 Zoom & Filter")
#         start_date = st.date_input("Start date", value=df.index.min().date())
#         end_date = st.date_input("End date", value=df.index.max().date())
# 
#         if start_date and end_date:
#             df_vis = df.loc[start_date:end_date]
#         else:
#             df_vis = df
# 
#         st.subheader("📈 Line Chart")
#         vis.plot_time_series(df_vis, [vis_col], title=f"{vis_col} over Time")
# 
#         st.subheader("📉 Rolling Mean")
#         roll_window = st.slider("Rolling window size", 2, 100, 24)
#         rolling_series = vis.rolling_stats(df_vis[[vis_col]], window=roll_window)
#         st.line_chart(rolling_series)
# 
#         st.subheader("🔁 Autocorrelation")
#         acf_lags = st.slider("Lags for ACF plot", 10, 100, 40)
#         vis.plot_autocorrelation(df_vis, vis_col, lags=acf_lags)
# 
#         st.subheader("🔁 Partial Autocorrelation")
#         vis.plot_pacf_custom(df_vis, vis_col, lags=acf_lags)
# 
#     # =========================
#     with tab5:
#         st.header("📄 Preview Enhanced Data")
#         st.write(df.tail())
# 
# else:
#     st.info("Please upload or select a dataset to begin.")
# 