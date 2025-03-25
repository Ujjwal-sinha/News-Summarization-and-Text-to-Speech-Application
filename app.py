import streamlit as st
import os
import pandas as pd
import plotly.express as px
import requests
from utils import (
    scrape_news,
    text_to_speech,
    comparative_analysis,
    generate_news_reel
)
from collections import Counter

# Page config
st.set_page_config(page_title="News Summarizer & TTS", page_icon="📰", layout="wide")

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""

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
        company_name = st.text_input("Company", placeholder="e.g., Tesla")
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
            st.session_state.articles = articles  # ✅ Store in session

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
            all_topics = []
            for article in st.session_state.articles:
                all_topics.extend(article.get("topics", []))

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
                st.session_state.translated_text = translated_text  # ✅ Store in session

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

# --- 🎬 News Reel Button Section (separate from fetch block) ---
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
