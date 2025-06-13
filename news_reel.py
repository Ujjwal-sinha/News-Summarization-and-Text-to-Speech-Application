import streamlit as st
import os
import json
from utils import scrape_news, generate_news_reel

# --- News Reel Page ---
st.set_page_config(page_title="News Reel", page_icon="🎥", layout="wide")

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
}
</style>
<div class='reel-header'>
    <h1 style='margin-bottom: 0;'>🎥 News Reel</h1>
    <div style='font-size: 20px; margin-top: 6px;'>Watch and listen to the latest news highlights</div>
</div>
""", unsafe_allow_html=True)

# --- Fetch Latest News for Reel ---
st.markdown("### 📰 Get Latest News Highlights")
category = st.selectbox("Choose News Category", [
    "All", "Business", "Technology", "Sports", "Entertainment", "Health", "Science", "World", "Politics", "Finance", "Travel", "Lifestyle"
], key="reel_category")

if st.button("🔄 Fetch Latest News for Reel"):
    with st.spinner("Fetching latest news..."):
        # Only pass category as keyword to scrape_news if supported, else use as query
        articles = scrape_news(category if category != "All" else "")
    if not articles:
        st.warning("No news found for this category.")
    else:
        st.session_state.reel_articles = articles
        st.success(f"Fetched {len(articles)} news articles.")

# --- Show News Reel ---
if 'reel_articles' in st.session_state and st.session_state.reel_articles:
    filtered_articles = st.session_state.reel_articles
    if category != "All":
        filtered_articles = [a for a in st.session_state.reel_articles if category.lower() in [t.lower() for t in a.get('topics', [])]]
    st.markdown("### 📰 Latest News Highlights")
    for article in filtered_articles:  # Removed the [:10] limit
        st.markdown(f"""
        <div class='reel-card'>
            <a href='{article['link']}' target='_blank' style='text-decoration: none; color: #232526;'><h3 style='margin-bottom: 8px;'>{article['title']}</h3></a>
            <div style='font-size: 16px; margin-bottom: 8px;'>{article['summary']}</div>
            <div style='color: #888; font-size: 14px;'>Topics: {', '.join(article['topics'])} | Sentiment: {article['sentiment']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center; color:#888;'>Reels 1 to {len(filtered_articles)}</div>", unsafe_allow_html=True)

    # --- Generate and Show News Reel Video ---
    if st.button("🎬 Generate News Reel Video"):
        with st.spinner("Generating video reel from latest news..."):
            summary_text = " ".join([a['summary'] for a in filtered_articles if a.get('summary')])
            # Allow user to upload an image for the reel background
            st.markdown("#### (Optional) Add a background image for the reel")
            image_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="reel_bg_image")
            image_path = None
            if image_file:
                image_path = os.path.join("temp_reel_bg.jpg")
                with open(image_path, "wb") as f:
                    f.write(image_file.read())
            video_path = generate_news_reel(
                text=summary_text,
                language="en",
                output_file="news_reel_latest.mp4",
                image_path=image_path
            )
        if os.path.exists(video_path):
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("⬇️ Download News Reel", f, "news_reel_latest.mp4", mime="video/mp4")
        else:
            st.error("❌ Failed to generate news reel.")
