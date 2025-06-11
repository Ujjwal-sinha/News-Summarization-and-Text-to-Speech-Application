import streamlit as st
import os
from utils import scrape_news, generate_news_reel

st.set_page_config(page_title="News Reels", page_icon="🎬", layout="wide")

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
.reel-controls {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 20px 0;
}
</style>
<div class='reel-header'>
    <h1 style='margin-bottom: 0;'>🎬 News Reels</h1>
    <div style='font-size: 20px; margin-top: 6px;'>Swipe through unlimited latest news reels</div>
</div>
""", unsafe_allow_html=True)

# --- News Category Selector ---
categories = [
    "All", "Business", "Technology", "Sports", "Entertainment", "Health", "Science", "World", "Politics", "Finance", "Travel", "Lifestyle"
]
category = st.selectbox("Choose News Category", categories, key="reels_category")

# --- Fetch News for Reels ---
if 'reels_articles' not in st.session_state or st.button("🔄 Refresh News Reels"):
    with st.spinner("Fetching latest news for reels..."):
        articles = scrape_news(category if category != "All" else "")
    if not articles:
        st.session_state.reels_articles = []
        st.warning("No news found for this category.")
    else:
        st.session_state.reels_articles = articles
        st.session_state.reel_index = 0

# --- Reel Navigation State ---
if 'reel_index' not in st.session_state:
    st.session_state.reel_index = 0

articles = st.session_state.get('reels_articles', [])
reel_index = st.session_state.get('reel_index', 0)

# --- Show Reel (One at a Time, Like Instagram Reels) ---
if articles:
    article = articles[reel_index % len(articles)]
    st.markdown(f"""
    <div class='reel-card'>
        <a href='{article['link']}' target='_blank' style='text-decoration: none; color: #232526;'><h2 style='margin-bottom: 8px;'>{article['title']}</h2></a>
        <div style='font-size: 18px; margin-bottom: 8px;'>{article['summary']}</div>
        <div style='color: #888; font-size: 15px;'>Topics: {', '.join(article['topics'])} | Sentiment: {article['sentiment']}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- Generate and Show Reel Video for This Article ---
    if st.button("🎬 Play Reel Video for this News", key=f"play_reel_{reel_index}"):
        with st.spinner("Generating video reel for this news..."):
            video_path = generate_news_reel(
                text=article['summary'],
                language="en",
                output_file=f"news_reel_{reel_index}.mp4"
            )
        if os.path.exists(video_path):
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("⬇️ Download This Reel", f, f"news_reel_{reel_index}.mp4", mime="video/mp4")
        else:
            st.error("❌ Failed to generate news reel.")

    # --- Reel Controls (Next/Previous) ---
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("⬅️ Previous", key="prev_reel"):
            st.session_state.reel_index = (reel_index - 1) % len(articles)
            st.experimental_rerun()
    with col3:
        if st.button("Next ➡️", key="next_reel"):
            st.session_state.reel_index = (reel_index + 1) % len(articles)
            st.experimental_rerun()
    st.markdown(f"<div style='text-align:center; color:#888;'>Reel {reel_index+1} of {len(articles)}</div>", unsafe_allow_html=True)
else:
    st.info("No news reels available. Try refreshing or changing the category.")
