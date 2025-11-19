import streamlit as st
import pandas as pd


def render_documents(processed_files: dict | None = None):
    """
    Render the documents table in the SystemOps tab.

    Args:
        processed_files (dict | None): Mapping of filename -> metadata.
    """
    st.subheader("📄 Document Index")

    files = processed_files or {}

    if files:
        data = []
        for filename, info in files.items():
            data.append(
                {
                    "Document": filename,
                    "Chunks": info.get("chunk_count", 0),
                    "Status": "✅ Indexed",
                    "Type": "PDF" if filename.lower().endswith(".pdf") else "Text",
                }
            )

        df = pd.DataFrame(data)
        st.dataframe(
            df,
            column_config={
                "Status": st.column_config.TextColumn("Status"),
                "Chunks": st.column_config.NumberColumn("Chunks", format="%d"),
            },
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Total documents: {len(files)}")
    else:
        st.info("No documents found. Upload files using the sidebar to get started.")
