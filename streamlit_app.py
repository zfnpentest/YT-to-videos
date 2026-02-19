import streamlit as st
import yt_dlp
import os
import subprocess
import sys

# 1. Access Control (Simple Password)
PASSWORD = "your_secret_password_here" # Change this!

st.set_page_config(page_title="Ultra Downloader", page_icon="🛡️")

def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if not st.session_state.auth:
        pwd = st.text_input("Enter Access Key:", type="password")
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("🛡️ Ultra Downloader (Max 403 Bypass)")

    # UI for standard inputs
    url = st.text_input("Video Link:", placeholder="https://...")
    
    col1, col2 = st.columns(2)
    with col1:
        format_choice = st.selectbox("Format:", ["MP4 (Video)", "MP3 (Audio)"])
    with col2:
        res = st.selectbox("Resolution:", ["1080", "720", "480", "Best"])

    # --- ADVANCED BYPASS SECTION ---
    with st.expander("🛠️ 403 Bypass Tools (Use if Download Fails)"):
        st.info("YouTube 2026 blocks server IPs. Fill these to look like a human.")
        po_token = st.text_input("PO Token:", placeholder="Paste your po_token here...")
        visitor_data = st.text_input("Visitor Data:", placeholder="Paste visitorData here...")
        cookie_data = st.text_area("Cookies (Netscape Format):", height=100)

    # Manual Update Button
    if st.sidebar.button("Update yt-dlp Engine"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
        st.sidebar.success("Updated!")

    if st.button("Download & Process", use_container_width=True):
        if not url:
            st.error("Missing URL!")
        else:
            with st.spinner("Bypassing filters..."):
                # Save cookies if provided
                if cookie_data:
                    with open("cookies.txt", "w") as f:
                        f.write(cookie_data)

                # MAX DEFENSE OPTIONS
                ydl_opts = {
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'quiet': True,
                    # Rotation of clients to confuse the bot-detector
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web', 'mweb', 'tv'],
                            'po_token': [f'web+{po_token}'] if po_token else None,
                        }
                    }
                }
                
                if cookie_data: ydl_opts['cookiefile'] = "cookies.txt"
                
                # Format logic
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
                            st.download_button("💾 Save File", f, file_name=os.path.basename(file_path), use_container_width=True)
                    st.success("Download Successful!")
                except Exception as e:
                    st.error(f"403 Error or Blocked: {str(e)}")
                    st.warning("Hint: Update your PO Token and Cookies!")
