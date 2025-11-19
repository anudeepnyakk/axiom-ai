import streamlit as st

# Streamlit default colors
PRIMARY_COLOR = "#FF4B4B"  # Streamlit red
SECONDARY_COLOR = "#FF8700"  # Streamlit orange

def apply_theme():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');
    
    /* Global Streamlit styling */
    body, .stApp {
        background-color: #FAFAFA;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove header padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Main content area */
    .main .block-container {
        max-width: 900px;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* Custom header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #E0E0E0;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .logo {
        font-size: 28px;
        font-weight: 700;
        color: #31333F;
        letter-spacing: -0.5px;
    }
    
    .tagline {
        font-size: 14px;
        color: #808495;
        font-weight: 400;
    }
    
    .header-right {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .health-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00C853;
    }
    
    .health-dot-error {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #FF4B4B;
    }
    
    .health-text {
        font-size: 13px;
        color: #808495;
        font-weight: 500;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #31333F;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #31333F;
        font-weight: 600;
    }
    
    /* Remove sidebar collapse button */
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Button styling - Streamlit red */
    .stButton button {
        background: #FF4B4B;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stButton button:hover {
        background: #E63946;
        box-shadow: 0 2px 8px rgba(255, 75, 75, 0.3);
        transform: translateY(-1px);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Secondary button styling */
    .stButton button[kind="secondary"] {
        background: #F0F2F6;
        color: #31333F;
        border: 1px solid #E0E0E0;
    }
    
    .stButton button[kind="secondary"]:hover {
        background: #E6E9EF;
        border-color: #D0D0D0;
    }
    
    /* Form submit button */
    .stFormSubmitButton button {
        background: #FF4B4B;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stFormSubmitButton button:hover {
        background: #E63946;
        box-shadow: 0 2px 8px rgba(255, 75, 75, 0.3);
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        border-radius: 4px !important;
        border: 1px solid #E0E0E0 !important;
        font-size: 14px !important;
        font-family: 'Source Sans Pro', sans-serif !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FF4B4B !important;
        box-shadow: 0 0 0 1px #FF4B4B !important;
    }
    
    /* File uploader */
    [data-testid="stSidebar"] .stFileUploader {
        border: 2px dashed #E0E0E0;
        border-radius: 4px;
        padding: 1rem;
        background: #FAFAFA;
    }
    
    [data-testid="stSidebar"] .stFileUploader:hover {
        border-color: #FF4B4B;
        background: #FFF5F5;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #31333F;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 13px;
        color: #808495;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-size: 14px;
        font-weight: 600;
        color: #31333F;
        background: #F0F2F6;
        border-radius: 4px;
    }
    
    .streamlit-expanderHeader:hover {
        background: #E6E9EF;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border-radius: 4px;
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Hide spinner text */
    .stSpinner > div {
        display: none !important;
    }
    
    .stSpinner {
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
        border-bottom: 1px solid #E0E0E0;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 0;
        background-color: transparent;
        border: none;
        color: #808495;
        font-weight: 600;
        font-size: 14px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #FF4B4B;
        border-bottom: 2px solid #FF4B4B;
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 4px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F0F2F6;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #C0C0C0;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #A0A0A0;
    }
    </style>
    """, unsafe_allow_html=True)
