# custom_css.py
import streamlit as st

def apply_custom_css():
    custom_css = """
    <style>
    [data-testid="stSidebar"] > div:first-child {
        background-color: #e9e9e9; /* Cập nhật màu nền ở đây */
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
