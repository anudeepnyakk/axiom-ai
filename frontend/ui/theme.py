import streamlit as st

BLUE = "#1A73E8"

def apply_theme():
    st.markdown(f"""
    <style>
    /* Global ChatGPT-like styling */
    body, .stApp {{
        background-color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Header */
    .header {{
        width: 100%;
        padding: 12px 24px;
        background: #FFFFFF;
        border-bottom: 1px solid #E5E5E5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0;
    }}
    .logo {{
        font-size: 20px;
        font-weight: 600;
        color: #0D0D0D;
        letter-spacing: -0.5px;
    }}
    .tagline {{
        font-size: 13px;
        color: #6E6E80;
        margin-left: 10px;
        font-weight: 400;
    }}
    .health-dot {{
        width: 8px; 
        height: 8px;
        background: #10A37F;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }}
    .health-dot-error {{
        width: 8px;
        height: 8px;
        background: #EF4444;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }}
    .health-dot-warning {{
        width: 8px;
        height: 8px;
        background: #F59E0B;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }}
    .health-text {{
        font-size: 12px;
        color: #6E6E80;
        font-weight: 500;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: #F9FAFB;
        border-right: 1px solid #E5E5E5;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: #0D0D0D;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
        background-color: transparent;
        border-bottom: 1px solid #E5E5E5;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 12px 0;
        background-color: transparent;
        border: none;
        color: #6E6E80;
        font-weight: 500;
        font-size: 14px;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: #0D0D0D;
        border-bottom: 2px solid #0D0D0D;
    }}
    
    /* Button styling - ChatGPT like */
    .stButton button {{
        background: #10A37F;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 16px;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s;
    }}
    
    .stButton button:hover {{
        background: #0E8B6F;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.3);
    }}
    
    /* Form submit button */
    .stFormSubmitButton button {{
        background: #10A37F;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 14px;
    }}
    
    .stFormSubmitButton button:hover {{
        background: #0E8B6F;
    }}
    
    /* Hide spinner text */
    .stSpinner > div {{
        display: none !important;
    }}
    
    /* Keep only the spinner icon */
    .stSpinner {{
        text-align: center;
        padding: 20px 0;
    }}

    /* Drawer */
    .axiom-drawer {{
        position: fixed;
        top: 65px;
        right: 0;
        width: 460px;
        height: calc(100% - 65px);
        background: white;
        border-left: 1px solid #E5E5E5;
        box-shadow: -4px 0 12px rgba(0,0,0,0.08);
        transform: translateX(480px);
        transition: transform 0.25s ease-out;
        padding: 24px;
        z-index: 1000;
        overflow-y: auto;
    }}
    .axiom-drawer.open {{
        transform: translateX(0);
    }}
    .drawer-title {{
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #0D0D0D;
    }}
    
    /* Input fields */
    .stTextInput input {{
        border-radius: 8px !important;
        border: 1px solid #D1D5DB !important;
        font-size: 14px !important;
    }}
    
    .stTextInput input:focus {{
        border-color: #10A37F !important;
        box-shadow: 0 0 0 1px #10A37F !important;
    }}
    </style>
    """, unsafe_allow_html=True)
