# pages/01_Data_Loader.py

# pages/01_Data_Loader.py
import streamlit as st
from utils.ui.layout_utils import render_logo
from views.data_load.augmento_api_view import load_api_view
from views.data_load.bitmex_api_view import load_bitmex_view
from views.data_load.add_dataset_view import load_add_dataset_view

#st.set_page_config(page_title="Data Loader", layout="wide")
st.set_page_config(page_title="Home — NTC TAP", layout="wide")

render_logo(title="📦 Data Loader")


# === RESTORE CURRENT DATASET ON LOAD ===
st.session_state.saved_datasets = st.session_state.get("saved_datasets", [])
saved = st.session_state.saved_datasets
# If there's at least one saved and no current dataset selected, pick the last
if saved and "current_dataset_name" not in st.session_state:
    last = saved[-1]
    st.session_state.current_dataset_name = last["name"]
    df = last.get("df")
    client = last.get("client")
    auditor = last.get("auditor")
    if last["name"].startswith("bitmex_"):
        st.session_state.bitmex_df      = df
        st.session_state.bitmex_client  = client
        st.session_state.bitmex_auditor = auditor
    elif last["name"].startswith("augmento_"):
        st.session_state.df_augmento      = df
        st.session_state.client_augmento  = client
        st.session_state.auditor_augmento = auditor
    elif last["name"].startswith("preloaded_"):
        st.session_state.df_preloaded      = df
        st.session_state.client_preloaded  = client
        st.session_state.auditor_preloaded = auditor
    else:
        st.info("No dataset loaded. Please select a dataset to analyze and click 'Load Selected File'.")

tabs = st.tabs(["⚗️ Augmento API", "📈 BitMEX API", "📥 Add Dataset"] )

# === LOAD VIEWS ===
api_tab, bitmex_tab, add_tab = tabs

with api_tab:
    load_api_view()

with bitmex_tab:
    load_bitmex_view()

with add_tab:
    load_add_dataset_view()

# === SESSION MANAGER ===
st.sidebar.header("📊 Session Manager")
# Initialize saved_datasets
if "saved_datasets" not in st.session_state:
    st.session_state.saved_datasets = []
saved = st.session_state.saved_datasets
if saved:
    for i, ds in enumerate(saved):
        name_col, disp_col, rem_col = st.sidebar.columns([3,1,1])
        name_col.markdown(f"**{ds['name']}**")
        # Display button
        if disp_col.button("▶️", key=f"display_{i}"):
            st.session_state.current_dataset_name = ds['name']
            df = ds.get('df')
            client = ds.get('client')
            auditor = ds.get('auditor')
            #if ds['name'].startswith('bitmex_'):
            #    st.session_state.bitmex_df      = df
            #    st.session_state.bitmex_client  = client
            #    st.session_state.bitmex_auditor = auditor
            #else:
            #    st.session_state.df_augmento      = df
            #    st.session_state.client_augmento  = client
            #    st.session_state.auditor_augmento = auditor

            if ds["name"].startswith("bitmex_"):
                st.session_state.bitmex_df      = df
                st.session_state.bitmex_client  = client
                st.session_state.bitmex_auditor = auditor
            elif ds["name"].startswith("augmento_"):
                st.session_state.df_augmento      = df
                st.session_state.client_augmento  = client
                st.session_state.auditor_augmento = auditor
            elif ds["name"].startswith("preloaded_"):
                st.session_state.df_preloaded      = df
                st.session_state.client_preloaded  = client
                st.session_state.auditor_preloaded = auditor
            else:
                st.info("No dataset loaded. Please select a dataset to analyze and click 'Load Selected File'.")

            st.rerun()
        # Remove button
        if rem_col.button("🗑️", key=f"remove_global_{i}"):
            removed_name = ds['name']
            # Update the saved list
            updated = saved.copy()
            updated.pop(i)
            st.session_state.saved_datasets = updated
            # Clear store-in-session flags
            for cb in ['augmento_store_checkbox_1','augmento_store_checkbox_2',
                       'bitmex_store_checkbox_1','bitmex_store_checkbox_2']:
                st.session_state.pop(cb, None)
            # If removed was current, revert to last or clear
            if st.session_state.get('current_dataset_name') == removed_name:
                if updated:
                    last = updated[-1]
                    st.session_state.current_dataset_name = last['name']
                    df = last.get('df')
                    client = last.get('client')
                    auditor = last.get('auditor')
                    #if last['name'].startswith('bitmex_'):
                    #    st.session_state.bitmex_df      = df
                    #    st.session_state.bitmex_client  = client
                    #    st.session_state.bitmex_auditor = auditor
                    #else:
                    #    st.session_state.df_augmento      = df
                    #    st.session_state.client_augmento  = client
                    #    st.session_state.auditor_augmento = auditor

                    if last["name"].startswith("bitmex_"):
                        st.session_state.bitmex_df      = df
                        st.session_state.bitmex_client  = client
                        st.session_state.bitmex_auditor = auditor
                    elif last["name"].startswith("augmento_"):
                        st.session_state.df_augmento      = df
                        st.session_state.client_augmento  = client
                        st.session_state.auditor_augmento = auditor
                    elif last["name"].startswith("preloaded_"):
                        st.session_state.df_preloaded      = df
                        st.session_state.client_preloaded  = client
                        st.session_state.auditor_preloaded = auditor
                    else:
                        st.info("No dataset loaded. Please select a dataset to analyze and click 'Load Selected File'.")                

                else:
                    # No datasets left
                    for key in ['current_dataset_name', 'bitmex_df', 'bitmex_client', 'bitmex_auditor',
                                'df_augmento', 'client_augmento', 'auditor_augmento']:
                        st.session_state.pop(key, None)
            st.rerun()
else:
    st.warning('No dataset loaded. Please select a dataset to analyze and click "Load Selected File".')
    st.sidebar.info("No datasets in session.")
