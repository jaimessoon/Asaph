import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# --- 1. SETUP ---
st.set_page_config(page_title="JARVIS", layout="centered")

# Authenticate
if not st.user.is_logged_in:
    st.title("🛡️ JARVIS | Login")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

# --- 2. SOURCE & DATA ---
SHEET_URL = st.secrets["GOOGLE_SHEET_URL"]
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. THE UI (ALL ON ONE SCREEN) ---

st.title(f"🎵 JARVIS | {st.user.name}")

# --- SECTION A: SOURCE SELECTION ---
st.subheader("1. Pick Your Source")
source = st.radio(
    "Where are we looking?",
    ["WorshipTogether", "Ultimate-Guitar", "Manual Paste"],
    horizontal=True # Better for mobile thumbs
)

st.divider()

# --- SECTION B: INPUT AREA ---
if source == "Manual Paste":
    st.subheader("2. Paste Your Song")
    with st.form("paste_form"):
        p_title = st.text_input("Song Title")
        p_artist = st.text_input("Artist")
        p_body = st.text_area("Paste Chords & Lyrics here...", height=300)
        if st.form_submit_button("✅ Save to Library"):
            # Simple save logic (requires Form bridge or Service Account)
            st.success(f"Saved {p_title}!") 
else:
    st.subheader(f"2. Search {source}")
    search_query = st.text_input("Type song name here...", key="search_bar")
    if st.button("🔍 Run Search"):
        st.write(f"Searching {source} for '{search_query}'...")
        # (Insert search logic here)

st.divider()

# --- SECTION C: YOUR LIBRARY ---
st.subheader("3. Your Songbook")
try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    user_songs = df[df['User_Email'] == st.user.email]
    if not user_songs.empty:
        selected = st.selectbox("Open a song:", user_songs['Song_Title'].tolist())
        # Display song logic...
        st.info(f"Opening {selected}...")
    else:
        st.write("Your library is currently empty.")
except:
    st.error("Could not load library. Check your Google Sheet link.")
