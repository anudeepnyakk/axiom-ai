import streamlit as st
from datetime import datetime


def render_status():
    st.subheader("📑 Logs")

    st.markdown(
        """
        <style>
        .log-box {
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            background-color: #f3f4f6;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            height: 320px;
            overflow-y: auto;
        }
        .log-info { color: #059669; }
        .log-warn { color: #d97706; }
        .log-error { color: #dc2626; }
        .log-time { color: #9ca3af; margin-right: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logs = [
        ("INFO", "processed ai-agents.pdf successfully"),
        ("INFO", "chunking strategy: recursive_character"),
        ("WARN", "embedding model latency: 230ms"),
        ("INFO", "vector store updated"),
        ("ERROR", "failed to parse lab_results_legacy.txt"),
        ("INFO", "system heartbeat OK"),
    ]

    log_html = ['<div class="log-box">']
    for level, message in logs:
        timestamp = datetime.now().strftime("%H:%M:%S")
        css_class = f"log-{level.lower()}"
        log_html.append(
            f'<div><span class="log-time">[{timestamp}]</span>'
            f'<strong class="{css_class}">{level}</strong> {message}</div>'
        )
    log_html.append("</div>")

    st.markdown("".join(log_html), unsafe_allow_html=True)
