import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
from fpdf import FPDF

# --- 1. SETTINGS ---
st.set_page_config(page_title="JARVIS", layout="centered", page_icon="🎵") # 'centered' is better for mobile

# Custom CSS for bigger mobile buttons
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em; width: 100%; font-size: 18px; border-radius: 10px; }
    .stCode { font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

if not st.user.is_logged_in:
    st.title("🛡️ JARVIS")
    st.button("Mobile Login", on_click=st.login)
    st.stop()

# --- 2. MUSIC ENGINE ---
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def transpose_chord(chord, steps):
    def replace(match):
        root, suffix = match.group(1), match.group(2)
        if root in NOTES:
            return NOTES[(NOTES.index(root) + steps) % 12] + suffix
        return match.group(0)
    return re.sub(r'([A-G]#?|Bb|Eb|Ab|Db|Gb)(.*)', replace, chord)

def process_song(text, steps):
    return re.sub(r'\[(.*?)\]', lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)

def detect_key(text):
    match = re.search(r'\[([A-G]#?|Bb|Eb|Ab|Db|Gb).*?\]', text)
    return match.group(1) if match else "C"

# --- 3. DATABASE ---
SHEET_URL = st.secrets["GOOGLE_SHEET_URL"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet):
    try: return conn.read(spreadsheet=SHEET_URL, worksheet=worksheet, ttl=0)
    except: return pd.DataFrame()

# --- 4. MAIN UI ---
tab1, tab2, tab3 = st.tabs(["🔍 Gather", "📋 Setlists", "🚀 Live Mode"])

# --- TAB 1: GATHER (Mobile Form) ---
with tab1:
    st.subheader("Add Song")
    with st.form("mobile_gather"):
        title = st.text_input("Title")
        artist = st.text_input("Artist")
        body = st.text_area("Chords [G] & Lyrics", height=200)
        if st.form_submit_button("🚀 SAVE TO JARVIS"):
            df = get_data("Library")
            new_row = pd.DataFrame([{"User_Email": st.user.email, "Song_Title": title, "Artist": artist, "ChordPro_Body": body}])
            conn.update(spreadsheet=SHEET_URL, worksheet="Library", data=pd.concat([df, new_row], ignore_index=True))
            st.success("Saved!")

# --- TAB 2: SETLISTS ---
with tab2:
    st.subheader("Setlist Builder")
    lib = get_data("Library")
    if not lib.empty:
        user_songs = lib[lib['User_Email'] == st.user.email]['Song_Title'].tolist()
        with st.form("setlist_form"):
            s_name = st.text_input("Setlist Name")
            s_list = st.multiselect("Pick Songs", user_songs)
            if st.form_submit_button("Create Setlist"):
                st.session_state[f"set_{s_name}"] = s_list
                st.success(f"Setlist '{s_name}' ready!")

# --- TAB 3: LIVE MODE (Mobile Optimized) ---
with tab3:
    lib = get_data("Library")
    my_songs = lib[lib['User_Email'] == st.user.email]
    
    if not my_songs.empty:
        # Simple navigation
        song_list = my_songs['Song_Title'].tolist()
        
        # PERSISTENT INDEX FOR MOBILE GIGS
        if 'song_idx' not in st.session_state: st.session_state.song_idx = 0
        
        # Mobile Buttons for Nav
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: 
            if st.button("⬅️"): st.session_state.song_idx = max(0, st.session_state.song_idx - 1)
        with c2:
            st.write(f"**{st.session_state.song_idx + 1} of {len(song_list)}**")
        with c3:
            if st.button("➡️"): st.session_state.song_idx = min(len(song_list)-1, st.session_state.song_idx + 1)
            
        current_song_title = song_list[st.session_state.song_idx]
        song_data = my_songs[my_songs['Song_Title'] == current_song_title].iloc[0]
        
        st.divider()
        st.subheader(song_data['Song_Title'])
        
        # Transpose Slider (Large for thumbs)
        shift = st.select_slider("Transpose", options=range(-6, 7), value=0)
        
        display_body = process_song(song_data['ChordPro_Body'], shift)
        st.code(display_body, language="markdown")
    else:
        st.info("No songs found.")
