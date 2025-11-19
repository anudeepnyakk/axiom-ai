import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');
    
    /* Global Streamlit styling */
    body, .stApp {
        background-color: #ffffff;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Centered page layout - EXACTLY like Streamlit assistant */
    .main-block {
        max-width: 800px;
        margin: auto;
        padding: 2rem 2rem;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ddd;
        font-size: 1.05rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff4b4b;
        box-shadow: 0 0 0 1px #ff4b4b;
    }
    
    /* Send button */
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        padding: 10px 20px;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background-color: #e04444;
    }
    
    /* Chat messages - EXACT styling from Streamlit assistant */
    .user-msg {
        background: #f2f2f2;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        width: auto;
        max-width: 80%;
        margin-left: auto;
        font-size: 15px;
        line-height: 1.6;
        color: #262730;
    }
    
    .bot-msg {
        background: transparent;
        padding: 12px 0;
        margin-bottom: 10px;
        width: auto;
        font-size: 15px;
        line-height: 1.7;
        color: #262730;
    }
    
    /* Chat container */
    .chat-container {
        padding-top: 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Custom header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .logo {
        font-size: 24px;
        font-weight: 700;
        color: #262730;
    }
    
    .tagline {
        font-size: 14px;
        color: #808495;
    }
    
    .health-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00C853;
        display: inline-block;
        margin-right: 6px;
    }
    
    .health-dot-error {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ff4b4b;
        display: inline-block;
        margin-right: 6px;
    }
    
    .health-text {
        font-size: 13px;
        color: #808495;
    }

    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-green { background-color: #10b981; }
    .status-red { background-color: #ef4444; }
    .status-gray { background-color: #9ca3af; }
    
    /* Hide spinner text */
    .stSpinner > div {
        display: none !important;
    }
    
    .stSpinner {
        text-align: center;
        padding: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
