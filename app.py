import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# --- CONFIG ---
SHEET_URL = "PASTE_YOUR_FULL_GOOGLE_SHEET_URL_HERE"

st.title("ASAPH | Song Gatherer")

# --- 1. THE SCRAPER ---
def scrape_ug(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    data_div = soup.find('div', class_='js-store')
    data_content = json.loads(data_div['data-config'])
    raw_content = data_content['store']['page']['data']['tab_view']['wiki_tab']['content']
    # Convert [ch] to ChordPro [G]
    return raw_content.replace('[ch]', '[').replace('[/ch]', ']')

# --- 2. THE UI ---
conn = st.connection("gsheets", type=GSheetsConnection)

with st.expander("Add New Song"):
    new_title = st.text_input("Song Title")
    ug_url = st.text_input("Ultimate Guitar URL")
    
    if st.button("Gather & Save"):
        song_body = scrape_ug(ug_url)
        
        # Load existing data
        existing_data = conn.read(spreadsheet=SHEET_URL)
        
        # Create new row
        new_row = pd.DataFrame([{
            "Song_Title": new_title,
            "ChordPro_Body": song_body,
            "Source_URL": ug_url
        }])
        
        # Append and Update
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.success(f"Added {new_title} to Asaph!")

# --- 3. THE LIBRARY ---
st.divider()
df = conn.read(spreadsheet=SHEET_URL)
if not df.empty:
    st.dataframe(df[['Song_Title', 'Source_URL']])
