import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
from bs4 import BeautifulSoup
import json

# --- 1. LOGIN CHECK ---
if not st.user.is_logged_in:
    st.title("Welcome to JARVIS")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

st.title(f"JARVIS | {st.user.name}'s Songbook")
if st.button("Logout"): st.logout()

# --- 2. SOURCE MANAGER ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Default Source
primary_source = "ultimate-guitar.com" 

with st.sidebar:
    st.subheader("Source Settings")
    new_source = st.text_input("Add New Source (URL)")
    if st.button("Add Source"):
        # Logic to save new_source to your Google Sheet 'Sources' tab
        st.success("Source Added!")

# --- 3. SEARCH & SELECT ---
st.subheader("Gather New Song")
search_query = st.text_input("Search Song or Artist", placeholder="e.g. Hotel California")

if search_query:
    st.info(f"Searching {primary_source}...")
    
    # 3a. Search Logic (Simplified Example)
    # JARVIS goes to UG search results and finds top 5 links
    search_url = f"https://www.ultimate-guitar.com/search.php?title={search_query.replace(' ', '%20')}"
    
    # In a real scraper, we extract titles and links here
    # For now, let's simulate the results:
    results = {
        "Hotel California (Chords)": "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-chords-463",
        "Hotel California (Official)": "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-official-1912533"
    }
    
    selected_name = st.selectbox("Select the correct version:", list(results.keys()))
    
    if st.button("Confirm & Gather"):
        target_url = results[selected_name]
        # Run the scraper logic we built earlier
        # save_to_sheet(target_url)
        st.success(f"Saved {selected_name} to your library!")
