# JARVIS | Asaph Songbook 🎵

**JARVIS** (Jaimes' Automated Retrieval & Visual Integration System) is a personal digital songbook and music gatherer. It allows users to search for songs, scrape ChordPro-style lyrics/chords from primary sources like Ultimate-Guitar, and save them to a private Google Sheets database.

## 🚀 Features
- **Google OAuth Integration:** Secure personal login for private library access.
- **Automated Gathering:** Search and scrape songs directly into your database.
- **Custom Sources:** Add and manage your own primary music source websites.
- **Dynamic Library:** Real-time sync with Google Sheets for easy editing and viewing.

---

## 🔒 Privacy Policy

**Last Updated: January 4, 2026**

This Privacy Policy explains how JARVIS ("the App") handles your data. Because this is a personal, open-source project, transparency is our priority.

### 1. Data Collection
- **User Identity:** The App uses Google OAuth to identify you. We collect your **Email Address** and **Name** purely to distinguish your personal song library from other users within the same database.
- **Song Data:** Any songs you search for and "Save" are stored in a Google Sheet associated with the App.

### 2. Data Usage
- Your email is used as a "Unique Key" in the database so that only *your* songs are displayed when *you* log in.
- We do not sell, trade, or share your email or library data with third parties.

### 3. Data Storage
- All data is stored in a **Google Sheet**. As the user, you have full control over this data.
- OAuth tokens are managed by Streamlit's secure authentication hosting and are not stored permanently by the App code.

### 4. Third-Party Services
- **Google Sheets API:** Used to store and retrieve your song library.
- **Ultimate-Guitar / External Sites:** The App fetches public data from these sites at your request. We do not send your personal data to these external sites.

### 5. Contact
For any questions regarding your data or to request data deletion, please contact the repository owner via GitHub.

---

## 🛠️ Setup & Installation
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up your `.streamlit/secrets.toml` with your `GOOGLE_SHEET_URL` and `[auth]` credentials.
4. Run the app: `streamlit run app.py`.

## 📜 License
This project is for personal and educational use. Please respect the Copyright and Terms of Service of any music websites you scrape data from.
