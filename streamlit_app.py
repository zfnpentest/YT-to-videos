import streamlit as st
import yt_dlp
import os
import subprocess
import sys
import requests
from packaging import version

# --- 1. ACCESS CONTROL (Hides password from GitHub) ---
def check_password():
    if "auth" not in st.session_state: 
        st.session_state.auth = False
    
    if not st.session_state.auth:
        # This pulls the password you set in the Streamlit Dashboard
        try:
            correct_password = st.secrets["ACCESS_PASSWORD"]
        except:
            st.error("🔑 Admin: Set ACCESS_PASSWORD in Streamlit Secrets!")
            return False
            
        pwd = st.text_input("🛡️ Enter Access Key:", type="password")
        if pwd == correct_password:
            st.session_state.auth = True
            st.rerun()
        elif pwd != "":
            st.error("❌ Incorrect Password")
        return False
    return True

# --- 2. VERSION GUARD LOGIC ---
def get_versions():
    current_ver = yt_dlp.version.__version__
    try:
        response = requests.get("https://pypi.org/pypi/yt-dlp/json", timeout=5)
        latest_ver = response.json()["info"]["version"]
    except:
        latest_ver = current_ver
    return current_ver, latest_ver

# Run the app if authenticated
if check_password():
    # SIDEBAR: Status & Updates
    st.sidebar.title("🛠️ System Control")
    current, latest = get_versions()
    
    if version.parse(current) < version.parse(latest):
        st.sidebar.error(f"⚠️ UPDATE NEEDED\nRunning: {current}\nLatest: {latest}")
        if st.sidebar.button("🚀 Upgrade yt-dlp Now"):
            with st.sidebar.status("Updating engine..."):
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            st.sidebar.success("Engine Updated! Refreshing...")
            st.rerun()
    else:
        st.sidebar.success(f"✅ ENGINE READY\nVersion: {current}")

    # MAIN UI
    st.title("📥 Ultra Downloader v2026")
    url = st.text_input("Paste Link:", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2 = st.columns(2)
    with col1:
        format_choice = st.selectbox("Type:", ["MP4 (Video)", "MP3 (Audio)"])
    with col2:
        res = st.selectbox("Max Resolution:", ["1080", "720", "480", "Best"])

    # ADVANCED BYPASS TOOLS
    with st.expander("🛡️ Advanced Bypass (Use for 403 Errors)"):
        st.write("Get these from your browser's F12 Network tab (v1/player)")
        po_token = st.text_input("PO Token")
        visitor_data = st.text_input("Visitor Data")
        cookie_data = st.text_area("Cookies (Netscape Format)")

    if st.button("Prepare Download", use_container_width=True):
        if not url:
            st.error("Please enter a link!")
        else:
            with st.spinner("Bypassing filters..."):
                # Setup Cookies
                if cookie_data:
                    with open("cookies.txt", "w") as f: f.write(cookie_data)

                # MAX DEFENSE OPTS
                ydl_opts = {
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            # Rotates clients to dodge bot detection
                            'player_client': ['web', 'mweb', 'tv'],
                            'po_token': [f'web+{po_token}'] if po_token else None,
                            'visitor_data': [visitor_data] if visitor_data else None
                        }
                    }
                }
                
                if cookie_data: ydl_opts['cookiefile'] = "cookies.txt"

                # Format selection
                if format_choice == "MP3 (Audio)":
                    ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
                else:
                    ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if res != "Best" else 'bestvideo+bestaudio/best'

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        file_path = ydl.prepare_filename(info)
                        if format_choice == "MP3 (Audio)":
                            file_path = file_path.rsplit('.', 1)[0] + '.mp3'

                        with open(file_path, "rb") as f:
                            st.download_button("💾 Save to Device", f, file_name=os.path.basename(file_path), use_container_width=True)
                    st.success("Success!")
                except Exception as e:
                    st.error(f"403 Blocked: {str(e)}")
                    st.info("Try updating your PO Token and Cookies above.")
