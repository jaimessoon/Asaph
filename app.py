import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

# --- 1. SETTINGS & AUTH ---
st.set_page_config(page_title="JARVIS | Songbook", layout="wide")

# Check if user is logged in (Streamlit 1.42+ native)
if not st.experimental_user.is_logged_in:
    st.title("🛡️ JARVIS Access")
    st.write("Please log in with your Google account to access your personal songbook.")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

# --- 2. DATABASE CONNECTION ---
# Using your provided Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1e7hBwOYzO2VX9N1XUy2LgTP4gJWC05D5Fty6Gl79kT8/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. SCRAPER ENGINE ---
def search_ug(query):
    """Searches Ultimate Guitar and returns a dict of labels and URLs."""
    search_url = f"https://www.ultimate-guitar.com/search.php?title={query.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        data_div = soup.find('div', class_='js-store')
        data_content = json.loads(data_div['data-config'])
        results = data_content['store']['page']['data']['results']
        
        search_options = {}
        for item in results:
            if 'tab_url' in item and 'song_name' in item:
                # Filter for Chords/Tabs
                label = f"{item['song_name']} - {item['artist_name']} ({item.get('type', 'Tab')})"
                search_options[label] = item['tab_url']
        return search_options
    except:
        return {}

def scrape_ug_details(url):
    """Fetches the actual ChordPro content from a specific UG page."""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data_div = soup.find('div', class_='js-store')
    data_content = json.loads(data_div['data-config'])
    raw_content = data_content['store']['page']['data']['tab_view']['wiki_tab']['content']
    # Convert [ch]G[/ch] to [G]
    clean_content = raw_content.replace('[ch]', '[').replace('[/ch]', ']')
    clean_content = re.sub(r'\[/?tab\]', '', clean_content)
    return clean_content

# --- 4. SIDEBAR: SOURCE MANAGER ---
with st.sidebar:
    st.title(f"👤 {st.experimental_user.name}")
    st.write(st.experimental_user.email)
    
    st.divider()
    st.subheader("Source Manager")
    
    # Load sources from Sheet
    try:
        sources_df = conn.read(spreadsheet=SHEET_URL, worksheet="Sources")
    except:
        sources_df = pd.DataFrame(columns=["User_Email", "Site_Name", "Base_URL"])

    user_sources = sources_df[sources_df['User_Email'] == st.experimental_user.email]
    
    # Selection of Primary Source
    source_list = user_sources['Site_Name'].tolist() if not user_sources.empty else ["Ultimate-Guitar"]
    primary_source = st.selectbox("Primary Source", source_list)
    
    # Add new source
    with st.expander("➕ Add New Website"):
        new_site = st.text_input("Site Name (e.g. WorshipTogether)")
        new_base = st.text_input("Base URL")
        if st.button("Save Source"):
            new_s_row = pd.DataFrame([{"User_Email": st.experimental_user.email, "Site_Name": new_site, "Base_URL": new_base}])
            updated_sources = pd.concat([sources_df, new_s_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Sources", data=updated_sources)
            st.success("Source saved!")
            st.rerun()

    if st.button("Log out"):
        st.logout()

# --- 5. MAIN UI: GATHER & VIEW ---
tab1, tab2 = st.tabs(["🔍 Gather Song", "📚 My Songbook"])

with tab1:
    st.header("Search & Gather")
    query = st.text_input("Enter Song Title or Artist")
    
    if query:
        results = search_ug(query)
        if results:
            selected_label = st.selectbox("Select the correct version:", list(results.keys()))
            if st.button("Download & Save to JARVIS"):
                with st.spinner("Scraping..."):
                    target_url = results[selected_label]
                    chordpro_data = scrape_ug_details(target_url)
                    
                    # Save to Library
                    library_df = conn.read(spreadsheet=SHEET_URL, worksheet="Library")
                    new_song = pd.DataFrame([{
                        "User_Email": st.experimental_user.email,
                        "Song_Title": selected_label.split(" - ")[0],
                        "Artist": selected_label.split(" - ")[1] if "-" in selected_label else "Unknown",
                        "ChordPro_Body": chordpro_data,
                        "Source_URL": target_url,
                        "Key": "Original"
                    }])
                    updated_lib = pd.concat([library_df, new_song], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="Library", data=updated_lib)
                    st.success(f"Saved '{selected_label}' to your library!")
        else:
            st.warning("No results found. Try a broader search.")

with tab2:
    st.header("Your Collection")
    lib_df = conn.read(spreadsheet=SHEET_URL, worksheet="Library")
    my_songs = lib_df[lib_df['User_Email'] == st.experimental_user.email]
    
    if not my_songs.empty:
        song_to_view = st.selectbox("Select a song to play", my_songs['Song_Title'].tolist())
        current_song = my_songs[my_songs['Song_Title'] == song_to_view].iloc[0]
        
        st.divider()
        st.subheader(f"{current_song['Song_Title']} - {current_song['Artist']}")
        # Render the ChordPro (simple text for now)
        st.code(current_song['ChordPro_Body'], language="chordpro")
    else:
        st.write("Your songbook is empty. Use the 'Gather' tab to add songs!")
