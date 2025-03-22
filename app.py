import streamlit as st
import os
import pandas as pd
import plotly.express as px
import requests

from utils import (
    scrape_news,
    text_to_speech,
    comparative_analysis
)

# Page config
st.set_page_config(page_title="News Summarizer & TTS", page_icon="📰", layout="wide")

# Sidebar language selector
st.sidebar.markdown("## 🗣️ Audio Language")
selected_lang = st.sidebar.selectbox("Choose TTS Language", ["Hindi", "English"])
lang_code = "hi" if selected_lang == "Hindi" else "en"

# Light/Dark mode toggle
mode = st.sidebar.radio("🌓 Theme", ["Light", "Dark"])
if mode == "Dark":
    st.markdown(
        "<style>body { background-color: #111; color: #fff; } .stApp { background-color: #1e1e1e; }</style>",
        unsafe_allow_html=True
    )

# Title
st.markdown("<h1 style='text-align: center;'>📰 News Summarizer & Hindi TTS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Get the latest news, analysis, and listen to summaries</p>", unsafe_allow_html=True)
st.markdown("---")

# Input section
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
                if requests.get(logo_url).status_code == 200:
                    st.image(logo_url, width=64, caption="Company Logo")
            except:
                pass

# Fetch News Button
if st.button("🚀 Fetch News"):
    if not company_name.strip():
        st.error("⚠️ Please enter a valid company name.")
    else:
        with st.spinner(f"Fetching news for '{company_name}'..."):
            articles = scrape_news(company_name)

        if not articles:
            st.warning("❌ No articles found.")
        else:
            # Display article cards
            st.markdown("### 🗞️ News Articles")
            for article in articles:
                st.markdown(f"**🔹 [{article['title']}]({article['link']})**")
                st.write(article["summary"])
                st.markdown(f"`Topics:` {', '.join(article['topics'])} | `Sentiment:` {article['sentiment']}")
                st.markdown("---")

            # Comparative sentiment analysis
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

            # Audio Summary
            st.markdown(f"### 🎧 Audio Summary in {selected_lang}")
            summary_text = " ".join([article['summary'] for article in articles if article.get('summary')])

            if summary_text.strip():
                try:
                    audio_file = text_to_speech(summary_text, language=lang_code)
                    if os.path.exists(audio_file):
                        st.audio(audio_file, format="audio/mp3")
                        with open(audio_file, "rb") as f:
                            st.download_button("⬇️ Download Audio", f, "summary.mp3", "audio/mp3")
                        if st.button("🗑️ Clear Audio"):
                            os.remove(audio_file)
                            st.success("Audio file cleared successfully.")
                except Exception as e:
                    st.error(f"Error generating audio: {str(e)}")
            else:
                st.warning("⚠️ No valid summaries found for TTS.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>Built with ❤️ by <b>Ujjwal Sinha</b> • "
    "<a href='https://github.com/Ujjwal-sinha' target='_blank'>GitHub</a></p>",
    unsafe_allow_html=True
)
