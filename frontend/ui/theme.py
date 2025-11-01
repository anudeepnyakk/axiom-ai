import streamlit as st

BLUE = "#1A73E8"

def apply_theme():
    st.markdown(f"""
    <style>
    body, .stApp {{
        background-color: #F8FAFD;
        font-family: 'Inter', sans-serif;
    }}
    .header {{
        width: 100%;
        padding: 14px 28px;
        background: #FFFFFF;
        border-bottom: 1px solid #E3E8EF;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .logo {{
        font-size: 30px;
        font-weight: 700;
        color: {BLUE};
    }}
    .tagline {{
        font-size: 14px;
        color: #475569;
        margin-left: 8px;
    }}
    .health-dot {{
        width: 10px; height:10px;
        background:#16A34A;
        border-radius:50%;
        display:inline-block;
        margin-right:6px;
    }}
    .health-dot-error {{
        width: 10px; height:10px;
        background:#DC2626;
        border-radius:50%;
        display:inline-block;
        margin-right:6px;
    }}
    .health-dot-warning {{
        width: 10px; height:10px;
        background:#F59E0B;
        border-radius:50%;
        display:inline-block;
        margin-right:6px;
    }}
    .health-text {{
        font-size: 13px;
        color:#111827;
    }}

    /* Chat */
    .chat-bubble-user {{
        background: {BLUE};
        color:white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 6px 0 6px auto;
        max-width: 78%;
    }}
    .chat-bubble-bot {{
        background: #FFFFFF;
        border: 1px solid #E3E8EF;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 6px auto 6px 0;
        max-width: 78%;
        color: #111827;
    }}

    /* Drawer */
    .axiom-drawer {{
        position: fixed;
        top: 75px;
        right: 0;
        width: 460px;
        height: calc(100% - 80px);
        background: white;
        border-left: 1px solid #E3E8EF;
        box-shadow: -6px 0 14px rgba(0,0,0,0.08);
        transform: translateX(480px);
        transition: transform .25s ease-out;
        padding: 20px;
        z-index: 1000;
    }}
    .axiom-drawer.open {{
        transform: translateX(0);
    }}
    .drawer-title {{
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)
