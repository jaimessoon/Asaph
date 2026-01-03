import streamlit as st

st.title("JARVIS Debug Mode")

# Check 1: Secrets
if "GOOGLE_SHEET_URL" in st.secrets:
    st.success("✅ Secret 'GOOGLE_SHEET_URL' found.")
else:
    st.error("❌ Secret 'GOOGLE_SHEET_URL' is missing!")

# Check 2: Auth Configuration
if "auth" in st.secrets:
    st.success("✅ Auth section found in secrets.")
else:
    st.warning("⚠️ Auth section missing. Login will not work.")

# Check 3: Simple Login Button
try:
    if not st.experimental_user.is_logged_in:
        st.write("Please log in:")
        st.button("Log in with Google", on_click=st.login)
    else:
        st.write(f"Hello, {st.experimental_user.name}!")
except Exception as e:
    st.error(f"Auth Error: {e}")
