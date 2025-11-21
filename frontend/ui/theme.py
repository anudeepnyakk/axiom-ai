"""
Theme - Dark, Wide Layout for Split-Pane RAG Interface

Production-grade styling matching industry-standard RAG tools.
"""

import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Streamlit styling - Dark theme */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Remove massive white header space */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #f1f5f9;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: #f1f5f9;
        font-size: 1.8rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.8rem;
    }
    
    [data-testid="stMetricDelta"] {
        color: #10b981;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #1e293b;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        padding: 1rem;
    }
    
    /* Status indicators */
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
    
    /* Headers */
    h1, h2, h3 {
        color: #f1f5f9;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
    }
    
    /* Expanders */
    [data-testid="stExpander"] {
        background-color: #1e293b;
        border: 1px solid #334155;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1e293b;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        background-color: #1e293b;
        color: #f1f5f9;
    }
    
    /* Toggle */
    [data-baseweb="switch"] {
        background-color: #334155;
    }
    
    /* Slider */
    [data-baseweb="slider"] {
        color: #3b82f6;
    }
    
    /* Divider */
    hr {
        border-color: #334155;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)
