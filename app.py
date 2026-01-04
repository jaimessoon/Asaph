import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIG ---
st.set_page_config(page_title="JARVIS", layout="centered", page_icon="🎵")

if not st.user.is_logged_in:
    st.title("🛡️ JARVIS | Login")
    st.info("Welcome, Jaimes. Please log in to access your songbook.")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

# --- 2. DATABASE (READ ONLY) ---
SHEET_URL = st.secrets["GOOGLE_SHEET_URL"]
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. UI TABS ---
tab1, tab2 = st.tabs(["📝 Add New Song", "📚 My Songbook"])

with tab1:
    st.subheader("Add Song")
    
    # SETUP YOUR PRE-FILLED URL
    # Replace the ID below and the entry ID with your own (See instructions below)
    form_base_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
    email_entry_id = "entry.123456789" # This is the ID for the Email field
    
    # This automatically injects the logged-in user's email into the form
    prefilled_url = f"{form_base_url}?{email_entry_id}={st.user.email}&embedded=true"
    
    st.components.v1.iframe(prefilled_url, height=700, scrolling=True)

with tab2:
    st.subheader(f"{st.user.name}'s Collection")
    try:
        # Load the linked sheet
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        # Clean column names (Google Forms often adds spaces or timestamps)
        df.columns = [c.strip() for c in df.columns]
        
        # Filter for the current user
        # (Ensure your Form has a field called 'User_Email')
        my_songs = df[df['User_Email'] == st.user.email]
        
        if not my_songs.empty:
            # Sort by newest first (Timestamp is usually first column)
            my_songs = my_songs.iloc[::-1] 
            
            song_choice = st.selectbox("Select Song", my_songs['Song_Title'].unique())
            content = my_songs[my_songs['Song_Title'] == song_choice].iloc[0]
            
            st.divider()
            st.markdown(f"### {content['Song_Title']}")
            st.caption(f"Artist: {content['Artist']}")
            
            # Displaying in a code block preserves chord alignment
            st.code(content['ChordPro_Body'], language="markdown")
            
            if st.button("🔄 Refresh Library"):
                st.rerun()
        else:
            st.warning("Your library is empty. Add a song in the first tab!")
            
    except Exception as e:
        st.error("Sheet connection error. Check your GOOGLE_SHEET_URL in Secrets.")
