import streamlit as st
import os
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

# --- News App Header with Ticker ---
st.markdown(
    """
    <style>
    .news-header {{
        background: linear-gradient(90deg, #0f2027, #2c5364);
        color: white;
        padding: 30px 0 10px 0;
        text-align: center;
        border-radius: 0 0 20px 20px;
        margin-bottom: 0px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .news-ticker {{
        background: #ffcc00;
        color: #222;
        font-weight: bold;
        padding: 8px 0;
        border-radius: 0 0 20px 20px;
        margin-bottom: 20px;
        font-size: 18px;
        animation: ticker 20s linear infinite;
    }}
    @keyframes ticker {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    .news-card {{
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 24px;
        padding: 24px;
        transition: box-shadow 0.2s;
        border-left: 6px solid #2c5364;
        color: #111 !important;
    }}
    .news-card h3, .news-card .news-summary, .news-card .news-meta {{
        color: #111 !important;
    }}
    .news-card:hover {{
        box-shadow: 0 6px 24px rgba(44,83,100,0.15);
        border-left: 6px solid #ffcc00;
    }}
    .news-meta {{
        color: #444 !important;
        font-size: 14px;
        margin-bottom: 8px;
    }}
    .news-summary {{
        font-size: 17px;
        margin-bottom: 10px;
        color: #111 !important;
    }}
    .sidebar-section {{
        background: #f7f7f7;
        border-radius: 10px;
        padding: 18px 12px;
        margin-bottom: 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        color: #111 !important;
    }}
    .sidebar-section h3 {{
        color: #111 !important;
    }}
    .alert-panel {{
        background: #fffbe6;
        border-left: 5px solid #ffcc00;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        color: #111 !important;
    }}
    .notification-panel {{
        background: #e6f7ff;
        border-left: 5px solid #1890ff;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        color: #111 !important;
    }}
    .footer {{
        color: #888;
        font-size: 15px;
        margin-top: 40px;
        text-align: center;
    }}
    </style>
    <div class='news-header'>
        <h1 style='margin-bottom: 0;'>📰 News Summarizer & TTS</h1>
        <div style='font-size: 20px; margin-top: 6px;'>Get the latest news, analysis, and listen to summaries in multiple languages</div>
    </div>
    <div class='news-ticker'>
        Breaking: {breaking}  
    </div>
    """.format(breaking=(st.session_state.alerts[0] if st.session_state.alerts else "No breaking alerts right now.")),
    unsafe_allow_html=True
)

# --- Sidebar Redesign ---
st.sidebar.markdown("""
<div class='sidebar-section'>
    <h3>🗣️ Audio Language</h3>
</div>
""", unsafe_allow_html=True)
st.sidebar.selectbox("Choose TTS Language", list(language_options.keys()), key="sidebar_lang")
st.sidebar.markdown("""
<div class='sidebar-section'>
    <h3>🌓 Theme</h3>
</div>
""", unsafe_allow_html=True)
st.sidebar.radio("Theme", ["Light", "Dark"], key="sidebar_theme")

# --- News Category Selector ---
news_categories = [
    "All",
    "Business",
    "Technology",
    "Sports",
    "Entertainment",
    "Health",
    "Science",
    "World",
    "Politics",
    "Finance",
    "Travel",
    "Lifestyle"
]
st.sidebar.markdown("""
<div class='sidebar-section'>
    <h3>📰 News Category</h3>
</div>
""", unsafe_allow_html=True)
selected_category = st.sidebar.selectbox("Choose News Category", news_categories, key="news_category")

# --- Input Section ---
with st.container():
    st.markdown("### 🔍 Enter Company or Keyword")
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input("Company or Keyword", placeholder="e.g., Tesla, Olympics, COVID", key="company_input")
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
    if not company_name.strip() and selected_category == "All":
        st.error("⚠️ Please enter a company/keyword or select a category.")
    else:
        with st.spinner(f"Fetching news for '{company_name or selected_category}'..."):
            # Only pass company_name to scrape_news
            articles = scrape_news(company_name or selected_category)

        if not articles:
            st.warning("❌ No articles found.")
        else:
            st.session_state.articles = articles

# --- Display Articles as Cards (Filtered by Category) ---
if st.session_state.articles:
    filtered_articles = st.session_state.articles
    if selected_category != "All":
        filtered_articles = [a for a in st.session_state.articles if selected_category.lower() in [t.lower() for t in a.get('topics', [])]]
    st.markdown(f"<h2 style='margin-top: 0;'>🗞️ {selected_category} News Articles</h2>", unsafe_allow_html=True)
    if not filtered_articles:
        st.info(f"No articles found for category '{selected_category}'. Showing all articles.")
        filtered_articles = st.session_state.articles
    for article in filtered_articles:
        st.markdown(f"""
        <div class='news-card'>
            <div class='news-meta'>
                <b>Topics:</b> {', '.join(article['topics'])} &nbsp;|&nbsp; <b>Sentiment:</b> {article['sentiment']}
            </div>
            <a href='{article['link']}' target='_blank' style='text-decoration: none; color: #2c5364;'><h3 style='margin-bottom: 8px;'>{article['title']}</h3></a>
            <div class='news-summary'>{article['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Sentiment Analysis ---
    result = comparative_analysis(st.session_state.articles)
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
    all_topics = [t for article in st.session_state.articles for t in article.get("topics", [])]
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
    summary_text = " ".join([article['summary'] for article in st.session_state.articles if article.get('summary')])
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
    <button class='alert-button' onclick="window.location.reload()">🔔 Manage Alerts</button>
    """,
    unsafe_allow_html=True
)

if st.button("🔔 Manage Alerts", key="alert_button", help="Click to manage your news alerts"):
    st.session_state.show_alerts = not st.session_state.get('show_alerts', False)
    st.experimental_rerun()

if st.session_state.get('show_alerts', False):
    with st.expander("🔔 Alert System", expanded=True):
        st.markdown("<div class='alert-panel'><b>Set New Alert</b></div>", unsafe_allow_html=True)
        # Set New Alert
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
        if st.session_state.notifications:
            st.markdown("<div class='notification-panel'><b>Notifications</b></div>", unsafe_allow_html=True)
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

# --- News Reels Feature (Instagram-like Reels) ---
st.markdown("""
<style>
.reel-header {
    background: linear-gradient(90deg, #232526, #414345);
    color: white;
    padding: 30px 0 10px 0;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin-bottom: 0px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.reel-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 24px;
    padding: 24px;
    color: #111;
    display: flex;
    flex-direction: column;
    align-items: center;
}
</style>
<div class='reel-header'>
    <h2 style='margin-bottom: 0;'>🎬 News Reels</h2>
    <div style='font-size: 18px; margin-top: 6px;'>Swipe through unlimited latest news reels</div>
</div>
""", unsafe_allow_html=True)

with st.expander("🎬 News Reels (Beta)", expanded=False):
    reels_categories = [
        "All", "Business", "Technology", "Sports", "Entertainment", "Health", "Science", "World", "Politics", "Finance", "Travel", "Lifestyle"
    ]
    reels_category = st.selectbox("Choose News Category for Reels", reels_categories, key="reels_category_app")
    if 'reels_articles' not in st.session_state or st.button("🔄 Refresh News Reels", key="refresh_reels_app"):
        with st.spinner("Fetching latest news for reels..."):
            reels_articles = scrape_news(reels_category if reels_category != "All" else "")
        if not reels_articles:
            st.session_state.reels_articles = []
            st.warning("No news found for this category.")
        else:
            st.session_state.reels_articles = reels_articles
            st.session_state.reel_index = 0
    if 'reel_index' not in st.session_state:
        st.session_state.reel_index = 0
    articles = st.session_state.get('reels_articles', [])
    reel_index = st.session_state.get('reel_index', 0)
    if articles:
        article = articles[reel_index % len(articles)]
        st.markdown(f"""
        <div class='reel-card'>
            <a href='{article['link']}' target='_blank' style='text-decoration: none; color: #232526;'><h2 style='margin-bottom: 8px;'>{article['title']}</h2></a>
            <div style='font-size: 18px; margin-bottom: 8px;'>{article['summary']}</div>
            <div style='color: #888; font-size: 15px;'>Topics: {', '.join(article['topics'])} | Sentiment: {article['sentiment']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎬 Play Reel Video for this News", key=f"play_reel_{reel_index}_app"):
            with st.spinner("Generating video reel for this news..."):
                video_path = generate_news_reel(
                    text=article['summary'],
                    language="en",
                    output_file=f"news_reel_{reel_index}_app.mp4"
                )
            if os.path.exists(video_path):
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("⬇️ Download This Reel", f, f"news_reel_{reel_index}_app.mp4", mime="video/mp4")
            else:
                st.error("❌ Failed to generate news reel.")
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            if st.button("⬅️ Previous", key="prev_reel_app"):
                st.session_state.reel_index = (reel_index - 1) % len(articles)
                st.experimental_rerun()
        with col3:
            if st.button("Next ➡️", key="next_reel_app"):
                st.session_state.reel_index = (reel_index + 1) % len(articles)
                st.experimental_rerun()
        st.markdown(f"<div style='text-align:center; color:#888;'>Reel {reel_index+1} of {len(articles)}</div>", unsafe_allow_html=True)
    else:
        st.info("No news reels available. Try refreshing or changing the category.")

# --- Footer Styling ---
st.markdown(
    """
    <div class='footer'>
        Built with ❤️ by <b>Ujjwal Sinha</b> • <a href='https://github.com/Ujjwal-sinha' target='_blank'>GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)