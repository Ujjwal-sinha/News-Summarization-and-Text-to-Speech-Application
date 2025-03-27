import streamlit as st
import os
os.system("apt-get update && apt-get install -y ffmpeg")
import pandas as pd
import plotly.express as px
import requests
import json
from utils import (
    scrape_news,
    text_to_speech,
    comparative_analysis,
    generate_news_reel
)
from collections import Counter
import shutil

# Page config
st.set_page_config(page_title="News Summarizer & TTS", page_icon="📰", layout="wide")

# Define directories and files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
ALERTS_FILE = os.path.join(BASE_DIR, "alerts.json")
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "notifications.json")

# Ensure audio directory exists
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'show_alerts' not in st.session_state:
    st.session_state.show_alerts = False

# Helper function to load JSON files
def load_json(file_path, default=[]):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return default
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return default

# Load initial data
st.session_state.alerts = load_json(ALERTS_FILE)
st.session_state.notifications = load_json(NOTIFICATIONS_FILE)

# --- Sidebar Language Selector ---
language_options = {
    "Hindi 🇮🇳": "hi",
    "English 🇬🇧": "en",
    "Bengali 🇧🇩": "bn",
    "Spanish 🇪🇸": "es",
    "Tamil 🇮🇳": "ta"
}
st.sidebar.markdown("## 🗣️ Audio Language")
selected_lang_label = st.sidebar.selectbox("Choose TTS Language", list(language_options.keys()))
lang_code = language_options[selected_lang_label]

# --- Light/Dark Mode Toggle ---
mode = st.sidebar.radio("🌓 Theme", ["Light", "Dark"])
if mode == "Dark":
    st.markdown(
        "<style>body { background-color: #111; color: #fff; } .stApp { background-color: #1e1e1e; }</style>",
        unsafe_allow_html=True
    )

# --- Title ---
st.markdown("<h1 style='text-align: center;'>📰 News Summarizer & TTS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Get the latest news, analysis, and listen to summaries in multiple languages</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Input Section ---
with st.container():
    st.markdown("### 🔍 Enter Company Name")
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input("Company", placeholder="e.g., Tesla", key="company_input")
    with col2:
        if company_name:
            domain = company_name.lower().replace(" ", "") + ".com"
            logo_url = f"https://logo.clearbit.com/{domain}"
            try:
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    st.image(logo_url, width=64, caption="Company Logo")
            except requests.RequestException:
                st.write("Logo not available")

# --- Fetch News ---
if st.button("🚀 Fetch News"):
    if not company_name.strip():
        st.error("⚠️ Please enter a valid company name.")
    else:
        with st.spinner(f"Fetching news for '{company_name}'..."):
            articles = scrape_news(company_name)

        if not articles:
            st.warning("❌ No articles found.")
        else:
            st.session_state.articles = articles

            # --- Display Articles ---
            st.markdown("### 🗞️ News Articles")
            for article in articles:
                st.markdown(f"**🔹 [{article['title']}]({article['link']})**")
                st.write(article["summary"])
                st.markdown(f"`Topics:` {', '.join(article['topics'])} | `Sentiment:` {article['sentiment']}")
                st.markdown("---")

            # --- Sentiment Analysis ---
            result = comparative_analysis(articles)
            sentiment_data = result.get("Sentiment Distribution", {})
            if sentiment_data:
                st.markdown("### 📊 Sentiment Distribution")
                df = pd.DataFrame(list(sentiment_data.items()), columns=["Sentiment", "Count"])
                col1, col2 = st.columns(2)
                with col1:
                    pie = px.pie(df, names="Sentiment", values="Count", title="Pie Chart")
                    st.plotly_chart(pie, use_container_width=True)
                with col2:
                    bar = px.bar(df, x="Sentiment", y="Count", title="Bar Chart", color="Sentiment")
                    st.plotly_chart(bar, use_container_width=True)
            else:
                st.info("⚠️ No sentiment data available to visualize.")

            # --- Topic-wise Breakdown ---
            all_topics = [t for article in articles for t in article.get("topics", [])]
            topic_counts = Counter(all_topics)
            if topic_counts:
                st.markdown("### 🧠 Topic-wise Breakdown")
                df_topics = pd.DataFrame(topic_counts.items(), columns=["Topic", "Count"])
                topic_bar = px.bar(
                    df_topics.sort_values("Count", ascending=False),
                    x="Topic",
                    y="Count",
                    title="Frequency of Topics Across News Articles",
                    color="Topic",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                st.plotly_chart(topic_bar, use_container_width=True)
            else:
                st.info("⚠️ No topics available to visualize.")

            # --- Audio Summary + Translation ---
            summary_text = " ".join([article['summary'] for article in articles if article.get('summary')])
            if summary_text.strip():
                audio_file, translated_text = text_to_speech(summary_text, language=lang_code)
                st.session_state.translated_text = translated_text

                if os.path.exists(audio_file):
                    st.markdown(f"### 🎧 Audio Summary in {selected_lang_label}")
                    st.audio(audio_file, format="audio/mp3")
                    with open(audio_file, "rb") as f:
                        st.download_button("⬇️ Download Audio", f, "summary.mp3", "audio/mp3")
                    if st.button("🗑️ Clear Audio"):
                        try:
                            os.remove(audio_file)
                            st.success("Audio file cleared successfully.")
                        except OSError as e:
                            st.error(f"Failed to remove audio file: {e}")

                    # Show Translated Summary
                    st.markdown("#### 📝 Translated Summary Text")
                    st.markdown(
                        f"<div style='background-color: black; padding: 15px; border-radius: 10px;'>{translated_text}</div>",
                        unsafe_allow_html=True
                    )

# --- Special Alert System Button ---
st.markdown(
    """
    <style>
    .alert-button {
        background-color: #ffcc00;
        color: black;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    .alert-button:hover {
        background-color: #e6b800;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("🔔 Manage Alerts", key="alert_button", help="Click to manage your news alerts"):
    st.session_state.show_alerts = not st.session_state.show_alerts  # Toggle visibility

if st.session_state.show_alerts:
    with st.expander("🔔 Alert System", expanded=True):
        # Set New Alert
        st.markdown("#### Set New Alert")
        alert_term = st.text_input("Enter company or keyword", placeholder="e.g., Tesla, AI", key="alert_input")
        if st.button("Add Alert"):
            if alert_term.strip():
                if alert_term not in st.session_state.alerts:
                    st.session_state.alerts.append(alert_term)
                    try:
                        with open(ALERTS_FILE, "w") as f:
                            json.dump(st.session_state.alerts, f)
                        st.success(f"Alert set for '{alert_term}'!")
                    except Exception as e:
                        st.error(f"Failed to save alert: {e}")
                else:
                    st.warning("Alert already exists.")
            else:
                st.error("⚠️ Please enter a valid term.")

        # Display Current Alerts
        if st.session_state.alerts:
            st.markdown("#### Current Alerts")
            for term in st.session_state.alerts:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"- {term}")
                with col2:
                    if st.button("🗑️", key=f"delete_{term}"):
                        st.session_state.alerts.remove(term)
                        try:
                            with open(ALERTS_FILE, "w") as f:
                                json.dump(st.session_state.alerts, f)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to remove alert: {e}")

        # Check Notifications
        st.markdown("#### Notifications")
        if st.button("🔄 Refresh Notifications"):
            st.session_state.notifications = load_json(NOTIFICATIONS_FILE)
            if not st.session_state.notifications:
                st.info("No new notifications found.")
            else:
                unread_count = sum(1 for n in st.session_state.notifications if not n.get('read'))
                st.success(f"Loaded {len(st.session_state.notifications)} notifications ({unread_count} unread).")

        if st.session_state.notifications:
            # Add mark all as read button
            if st.button("📭 Mark All as Read"):
                for notif in st.session_state.notifications:
                    notif['read'] = True
                try:
                    with open(NOTIFICATIONS_FILE, "w") as f:
                        json.dump(st.session_state.notifications, f)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update notifications: {e}")

            # Display notifications in reverse order (newest first)
            for notif in reversed(st.session_state.notifications):
                # Style differently based on read status
                if notif.get('read'):
                    notification_style = "padding: 10px; border-radius: 5px; background-color: #f0f0f0;"
                else:
                    notification_style = "padding: 10px; border-radius: 5px; background-color: #e6f7ff; border-left: 4px solid #1890ff;"
                
                with st.container():
                    st.markdown(
                        f"<div style='{notification_style}'>"
                        f"<b>{notif['term'].title()}</b> - {notif['timestamp'].split('T')[0]}<br>"
                        f"{notif['message']}"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                    
                    # Mark as read button
                    if not notif.get('read'):
                        if st.button("✓ Mark as Read", key=f"read_{notif['timestamp']}"):
                            notif['read'] = True
                            try:
                                with open(NOTIFICATIONS_FILE, "w") as f:
                                    json.dump(st.session_state.notifications, f)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to update notification: {e}")
                    
                    # Display articles if available
                    if 'articles' in notif and notif['articles']:
                        with st.expander("📰 View Articles", expanded=False):
                            for article in notif['articles']:
                                st.markdown(f"**🔹 [{article['title']}]({article['link']})**")
                                st.write(article["summary"])
                                st.markdown(f"`Topics:` {', '.join(article['topics'])} | `Sentiment:` {article['sentiment']}")
                                st.markdown("---")
                    
                    # Audio player
                    audio_file = notif.get('audio_file')
                    if audio_file and os.path.exists(audio_file):
                        st.audio(audio_file, format="audio/mp3")
                        with open(audio_file, "rb") as f:
                            st.download_button(
                                "⬇️ Download Alert Audio", 
                                f, 
                                f"alert_{notif['term']}.mp3", 
                                "audio/mp3",
                                key=f"audio_{notif['timestamp']}"
                            )
                    else:
                        st.warning(f"Audio file for '{notif['term']}' not found.")
                
                st.markdown("---")  # Separator between notifications

# --- News Reel Button Section ---
if st.session_state.translated_text:
    st.markdown("### 🎥 Generate Video Summary Reel")
    if st.button("🎬 Create News Reel"):
        with st.spinner("Generating video reel..."):
            summary_text = " ".join([article['summary'] for article in st.session_state.articles if article.get('summary')])
            video_path = generate_news_reel(
                text=summary_text,
                language=lang_code,
                output_file="news_reel.mp4"
            )

        if os.path.exists(video_path):
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("⬇️ Download News Reel", f, "news_reel.mp4", mime="video/mp4")
        else:
            st.error("❌ Failed to generate news reel.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>Built with ❤️ by <b>Ujjwal Sinha</b> • "
    "<a href='https://github.com/Ujjwal-sinha' target='_blank'>GitHub</a></p>",
    unsafe_allow_html=True
)