import streamlit as st
import yt_dlp
import os
import subprocess
import sys
import requests
from packaging import version

# 1. Access Control
PASSWORD = "your_secret_password_here"

st.set_page_config(page_title="Ultra DL + Version Guard", page_icon="🛡️")

# --- VERSION CHECKER LOGIC ---
def get_versions():
    # Local version
    current_ver = yt_dlp.version.__version__
    # Remote version from PyPI
    try:
        response = requests.get("https://pypi.org/pypi/yt-dlp/json", timeout=5)
        latest_ver = response.json()["info"]["version"]
    except:
        latest_ver = current_ver # Fallback if offline
    return current_ver, latest_ver

def check_password():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pwd = st.text_input("Enter Access Key:", type="password")
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        return False
    return True

if check_password():
    # --- SIDEBAR: The Version Guard ---
    st.sidebar.title("🛠️ System Status")
    current, latest = get_versions()
    
    if version.parse(current) < version.parse(latest):
        st.sidebar.error(f"⚠️ OUTDATED\nInstalled: {current}\nLatest: {latest}")
        if st.sidebar.button("🚀 Update Engine Now"):
            with st.sidebar.status("Updating..."):
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            st.sidebar.success("Updated! Refreshing...")
            st.rerun()
    else:
        st.sidebar.success(f"✅ UP TO DATE\nVersion: {current}")

    # --- MAIN UI ---
    st.title("🛡️ Ultra Downloader")
    url = st.text_input("Video Link:", placeholder="https://...")
    
    with st.expander("🛠️ Advanced 403 Bypass"):
        st.info("YouTube 2026: Use these if 'Standard' fails.")
        po_token = st.text_input("PO Token:")
        v_data = st.text_input("Visitor Data:")
        cookie_data = st.text_area("Cookies (Netscape):")

    if st.button("Download", use_container_width=True):
        if url:
            with st.spinner("Extracting..."):
                if cookie_data:
                    with open("cookies.txt", "w") as f: f.write(cookie_data)
                
                opts = {
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'extractor_args': {'youtube': {
                        'player_client': ['web', 'mweb'],
                        'po_token': [f'web+{po_token}'] if po_token else None,
                        'visitor_data': [v_data] if v_data else None
                    }}
                }
                if cookie_data: opts['cookiefile'] = "cookies.txt"

                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        path = ydl.prepare_filename(info)
                        with open(path, "rb") as f:
                            st.download_button("💾 Save to Device", f, file_name=os.path.basename(path))
                    st.success("Finished!")
                except Exception as e:
                    st.error(f"Download Blocked: {str(e)}")
