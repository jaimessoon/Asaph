import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIG ---
st.set_page_config(page_title="JARVIS", layout="centered")

if not st.user.is_logged_in:
    st.title("🛡️ JARVIS | Login")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

# --- 2. DATABASE (READ ONLY) ---
# Reading a public sheet is still allowed!
SHEET_URL = st.secrets["GOOGLE_SHEET_URL"]
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. UI TABS ---
tab1, tab2 = st.tabs(["📝 Add New Song", "📚 View Library"])

with tab1:
    st.subheader("Add Song to JARVIS")
    st.info("Use the form below to add songs. It syncs automatically with your library.")
    
    # REPLACE THE URL BELOW with your Google Form "Send" Link
    # Note: Use the 'Embed' link from Google Forms (starts with <iframe...) 
    # but just grab the URL part.
    google_form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform?embedded=true"
    
    st.components.v1.iframe(google_form_url, height=800, scrolling=True)

with tab2:
    st.subheader("Your Collection")
    try:
        # We read from the Sheet that the Form is connected to
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        # Filter by your logged-in email
        my_songs = df[df['User_Email'] == st.user.email]
        
        if not my_songs.empty:
            song_choice = st.selectbox("Select Song", my_songs['Song_Title'].unique())
            content = my_songs[my_songs['Song_Title'] == song_choice].iloc[-1] # Get latest version
            
            st.divider()
            st.write(f"### {content['Song_Title']} - {content['Artist']}")
            st.code(content['ChordPro_Body'], language="markdown")
            
            if st.button("Refresh Library"):
                st.rerun()
        else:
            st.warning("No songs found for your email. Try adding one in the first tab!")
            
    except Exception as e:
        st.error("Connect your Google Sheet URL in Secrets to view the library.")
