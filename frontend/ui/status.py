import streamlit as st

def render_status():
    st.subheader("🧾 Logs")
    st.code("INFO processed report.pdf\nERROR failed lab.txt", language="text")
