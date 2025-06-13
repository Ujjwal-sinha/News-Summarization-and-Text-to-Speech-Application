import streamlit as st
import os
from utils import scrape_news, generate_news_reel

# Page config
st.set_page_config(page_title="News Reels", page_icon="🎬", layout="wide")

# --- Styles ---
st.markdown("""
<style>
.reel-header {
    background: linear-gradient(90deg, #232526, #414345);
    color: white;
    padding: 2rem 0;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.reel-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.reel-content {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #2c5364;
}
.reel-content h2, .reel-content p, .reel-content div {
    color: #000 !important;
}
[data-theme="dark"] .reel-content {
    background: #161B22 !important;
}
[data-theme="dark"] .reel-content h2,
[data-theme="dark"] .reel-content p,
[data-theme="dark"] .reel-content div {
    color: #fff !important;
}
[data-theme="dark"] .reel-container {
    background: #0D1117;
}
.reel-nav {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 1.5rem 0;
}
.reel-counter {
    text-align: center;
    color: #666;
    margin: 1rem 0;
}
.image-upload {
    background: #f8f9fa;
    border: 2px dashed #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
}
[data-theme="dark"] .image-upload {
    background: #1a2029;
    border-color: #2d333b;
}
.reel-counter {
    text-align: center;
    color: #666;
    margin: 1rem 0;
}
[data-theme="dark"] .reel-counter {
    color: #8b949e;
}
.translated-text {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    color: #000 !important;
}
[data-theme="dark"] .translated-text {
    background-color: #1a2029;
    color: #fff !important;
}
</style>

<div class='reel-header'>
    <h1>🎬 News Reels</h1>
    <p style='font-size: 1.2em; margin-top: 1rem;'>
        Experience news in an engaging, Instagram-style format
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'reels_articles' not in st.session_state:
    st.session_state.reels_articles = []
if 'reel_index' not in st.session_state:
    st.session_state.reel_index = 0

# Main container
st.markdown("<div class='reel-container'>", unsafe_allow_html=True)

# Category selection and refresh
col1, col2 = st.columns([3, 1])
with col1:
    category = st.selectbox(
        "Choose News Category",
        ["All", "Business", "Technology", "Sports", "Entertainment", 
         "Health", "Science", "World", "Politics"]
    )
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        with st.spinner("Fetching latest news..."):
            articles = scrape_news(category if category != "All" else "")
            if articles:
                st.session_state.reels_articles = articles
                st.session_state.reel_index = 0
                st.success(f"Found {len(articles)} news stories!")
            else:
                st.error("No news found. Try a different category.")

# Display current reel
if st.session_state.reels_articles:
    articles = st.session_state.reels_articles
    current_idx = st.session_state.reel_index
    article = articles[current_idx % len(articles)]
    
    # Reel content
    st.markdown(f"""
    <div class='reel-content'>
        <h2>{article['title']}</h2>
        <p style='font-size: 1.1em; margin: 1rem 0;'>{article['summary']}</p>
        <div style='color: #666;'>
            Topics: {', '.join(article['topics'])} | Sentiment: {article['sentiment']}
        </div>
        <a href='{article['link']}' target='_blank' style='display: inline-block; margin-top: 1rem;'>
            🔗 Read full article
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.reel_index = (current_idx - 1) % len(articles)
            st.rerun()
    with col2:
        st.markdown(f"<div class='reel-counter'>Reel {current_idx + 1} of {len(articles)}</div>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡️", use_container_width=True):
            st.session_state.reel_index = (current_idx + 1) % len(articles)
            st.rerun()
    
    # Video generation
    st.markdown("### 🎥 Create Video Reel")
    st.markdown("<div class='image-upload'>", unsafe_allow_html=True)
    image_file = st.file_uploader("Upload Background Image (Optional)", type=["jpg", "jpeg", "png"])
    if st.button("🎬 Generate Video Reel", use_container_width=True):
        with st.spinner("Creating your video reel..."):
            image_path = None
            if image_file:
                image_path = f"temp_bg_{current_idx}.jpg"
                with open(image_path, "wb") as f:
                    f.write(image_file.getvalue())
            
            video_path = generate_news_reel(
                text=article['summary'],
                language="en",
                output_file=f"news_reel_{current_idx}.mp4",
                image_path=image_path
            )
            
            if os.path.exists(video_path):
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Reel",
                        f,
                        f"news_reel_{current_idx}.mp4",
                        mime="video/mp4"
                    )
                # Display translated text if available
                if article.get('translated_text'):
                    st.markdown("#### 📝 Translated Text")
                    st.markdown(f"<div class='translated-text'>{article['translated_text']}</div>", unsafe_allow_html=True)
            else:
                st.error("Failed to generate video reel. Please try again.")
            
            # Cleanup
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("👆 Choose a category and click 'Refresh' to start viewing news reels")

st.markdown("</div>", unsafe_allow_html=True)  # Close main container