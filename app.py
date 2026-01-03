import streamlit as st

# Set Page Config (This changes the tab name in your browser)
st.set_page_config(page_title="Asaph | Digital Songbook", page_icon="🎵")

# Custom CSS to make it look less like a "data app" and more like a "music app"
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stHeader {
        font-family: 'serif';
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# The Branding
st.title("ASAPH")
st.caption("Gathered. Organized. Played. — *The Digital Songbook for the Modern Levite*")
st.divider()
