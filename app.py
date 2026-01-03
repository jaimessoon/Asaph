import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

# --- 1. SETTINGS & AUTH ---
st.set_page_config(page_title="JARVIS | Songbook", layout="wide", page_icon="🎵")

# Check for Google Login
if not st.experimental_user.is_logged_in:
    st.title("🛡️ JARVIS | Asaph Songbook")
    st.info("Authentication required. Please log in with your Google account.")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

# --- 2. DATABASE CONNECTION (Using your Secret) ---
# We pull the URL you just saved in Streamlit Secrets
SHEET_URL = st.secrets["GOOGLE_SHEET_URL"]
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. SCRAPER ENGINE ---
def search_ug(query):
    search_url = f"https://www.ultimate-guitar.com/search.php?title={query.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        data_div = soup.find('div', class_='js-store')
        data_content = json.loads(data_div['data-config'])
        results = data_content['store']['page']['data']['results']
        
        search_options = {}
        for item in results:
            if 'tab_url' in item and 'song_name' in item:
                label = f"{item['song_name']} - {item['artist_name']} ({item.get('type', 'Tab')})"
                search_options[label] = item['tab_url']
        return search_options
    except Exception:
        return {}

def scrape_ug_details(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.content, 'html.parser')
    data_div = soup.find('div', class_='js-store')
    data_content = json.loads(data_div['data-config'])
    raw_content = data_content['store']['page']['data']['tab_view']['wiki_tab']['content']
    # Clean up formatting
    clean_content = raw_content.replace('[ch]', '[').replace('[/ch]', ']')
    clean_content = re.sub(r'\[/?tab\]', '', clean_content)
    return clean_content

# --- 4. SIDEBAR: USER & SOURCES ---
with st.sidebar:
    st.title(f"👤 {st.experimental_user.name}")
    st.caption(st.experimental_user.email)
    
    st.divider()
    
    # Load sources from Sheet
    try:
        sources_df = conn.read(spreadsheet=SHEET_URL, worksheet="Sources", ttl=3600)
    except:
        sources_df = pd.DataFrame(columns=["User_Email", "Site_Name", "Base_URL"])

    user_sources = sources_df[sources_df['User_Email'] == st.experimental_user.email]
    
    # Selection of Primary Source
    available_sites = user_sources['Site_Name'].tolist() if not user_sources.empty else ["Ultimate-Guitar"]
    primary_source = st.selectbox("Current Search Source", available_sites)
    
    with st.expander("➕ Add Custom Source"):
        new_site = st.text_input("Site Name")
        new_base = st.text_input("Base URL")
        if st.button("Register Source"):
            new_s_row = pd.DataFrame([{"User_Email": st.experimental_user.email, "Site_Name": new_site, "Base_URL": new_base}])
            updated_sources = pd.concat([sources_df, new_s_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Sources", data=updated_sources)
            st.success("New source registered!")
            st.rerun()

    if st.button("Logout"):
        st.logout()

# --- 5. MAIN TABS ---
tab1, tab2 = st.tabs(["🔍 Find & Gather", "📚 My Songbook"])

with tab1:
    st.header("Gather New Music")
    query = st.text_input("Search for song title or artist", key="main_search")
    
    if query:
        results = search_ug(query)
        if results:
            selected_label = st.selectbox("Select a version:", list(results.keys()))
            if st.button("Save to Library"):
                with st.spinner("Processing..."):
                    target_url = results[selected_label]
                    chordpro_data = scrape_ug_details(target_url)
                    
                    # Save to Library tab
                    try:
                        library_df = conn.read(spreadsheet=SHEET_URL, worksheet="Library", ttl=0)
                    except:
                        library_df = pd.DataFrame(columns=["User_Email", "Song_Title", "Artist", "ChordPro_Body", "Source_URL"])
                    
                    new_song = pd.DataFrame([{
                        "User_Email": st.experimental_user.email,
                        "Song_Title": selected_label.split(" - ")[0],
                        "Artist": selected_label.split(" - ")[1] if "-" in selected_label else "Unknown",
                        "ChordPro_Body": chordpro_data,
                        "Source_URL": target_url
                    }])
                    
                    updated_lib = pd.concat([library_df, new_song], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="Library", data=updated_lib)
                    st.success(f"Added {selected_label} to your collection!")
        else:
            st.warning("No matches found on Ultimate-Guitar.")

with tab2:
    st.header("My Collection")
    try:
        lib_df = conn.read(spreadsheet=SHEET_URL, worksheet="Library", ttl=0)
        my_songs = lib_df[lib_df['User_Email'] == st.experimental_user.email]
        
        if not my_songs.empty:
            song_list = my_songs['Song_Title'].tolist()
            view_choice = st.selectbox("Open Song", song_list)
            
            song_data = my_songs[my_songs['Song_Title'] == view_choice].iloc[0]
            st.divider()
            st.subheader(f"{song_data['Song_Title']} - {song_data['Artist']}")
            
            # Display chordpro text in a readable way
            st.text_area("Chord Sheet", value=song_data['ChordPro_Body'], height=500)
        else:
            st.info("Your library is currently empty.")
    except Exception as e:
        st.error("Could not load library. Ensure your 'Library' tab exists in Google Sheets.")
