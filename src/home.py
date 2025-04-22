# streamlit_app.py

import streamlit as st
from views.augmento_api_view import load_api_view
from views.data_wrangler_view import load_wrangler_view
from views.bitmex_api_view import load_bitmex_view


st.set_page_config(page_title="Home — NTC Augmento", layout="wide")

def render_sidebar():
    st.sidebar.image("../Assets/NTC_Icon.png", width=100, clamp=True)
    st.sidebar.title("NTC Augmento App")
    
render_sidebar()




st.header("👋 Welcome to NTC Augmento App")
st.markdown("""
Use the menu on the left to navigate between:
- Data Loader  
- Session Manager
- Data Wrangler 
- Data Analysis  
- Feature Engineering  
- Modeling  
- Explain  
""")

# st.set_page_config(layout="wide")
# 
# st.markdown("""
#     <style>
#         .block-container {
#             padding-top: 1rem !important;
#             padding-bottom: 1rem !important;
#         }
#     </style>
# """, unsafe_allow_html=True)
# 
# 
# # Navigation
# st.markdown(
#     """
#     <style>
#         [data-testid=stSidebar] [data-testid=stImage]{
#             text-align: center;
#             display: block;
#             margin-left: auto;
#             margin-right: auto;
#             width: 100%;
#         }
#     </style>
#     """, unsafe_allow_html=True
# )
# with st.sidebar:
#     st.sidebar.image("../Assets/NTC_Icon.png", width=100, clamp=True)
#     st.sidebar.title("NTC Augmento App")
# 
#     view = st.sidebar.radio("Select View below", ["⚗️ Augmento API", "📈 BitMEX API", "🧩 Data Wrangler"])
# 
# if view == "⚗️ Augmento API":
#     st.sidebar.markdown("---")
#     load_api_view()
# elif view == "📈 BitMEX API":
#     st.sidebar.markdown("---")
#     load_bitmex_view()
#     #st.sidebar.markdown("---")
# elif view == "🧩 Data Wrangler":
#     st.sidebar.markdown("---")
#     load_wrangler_view()
# 