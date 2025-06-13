import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter
import requests
from utils import scrape_news, text_to_speech, comparative_analysis

# Page config
st.set_page_config(page_title="News Search & Analysis", page_icon="📰", layout="wide")

# --- Page Header ---
st.markdown("""
<style>
.search-header {
    background: linear-gradient(90deg, #2c5364, #203a43);
    color: white;
    padding: 2rem 0;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.search-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
}
.result-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 4px solid #2c5364;
}
.result-card {
    background: white;
}
.result-card * {
    color: #000 !important;
}
.result-card h3 {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
}
.result-card p {
    font-size: 1.1rem;
    line-height: 1.6;
}
[data-theme="dark"] .result-card {
    background: #161B22;
}
[data-theme="dark"] .result-card * {
    color: #fff !important;
}
.result-card .news-meta {
    font-size: 0.9rem;
    color: #000 !important;
    margin-top: 0.75rem;
}
[data-theme="dark"] .result-card {
    background: #161B22;
}
[data-theme="dark"] .result-card *,
[data-theme="dark"] .result-card h3,
[data-theme="dark"] .result-card p,
[data-theme="dark"] .result-card .news-meta {
    color: #fff !important;
}
.result-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    border-left: 4px solid #ffcc00;
}
.sentiment-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-right: 0.5rem;
}
.sentiment-positive { 
    background: #d4edda; 
    color: #155724 !important; 
}
.sentiment-negative { 
    background: #f8d7da; 
    color: #721c24 !important; 
}
.sentiment-neutral { 
    background: #e2e3e5; 
    color: #383d41 !important; 
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

<div class='search-header'>
    <h1>📰 News Search & Analysis</h1>
    <p style='font-size: 1.2em; margin-top: 1rem;'>
        Search, analyze, and listen to news about any company or topic
    </p>
</div>
""", unsafe_allow_html=True)

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

# Main search interface
st.markdown("<div class='search-container'>", unsafe_allow_html=True)

# Search input with category selection
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("🔍 Search for company or topic", placeholder="e.g., Tesla, AI, Climate Change")
with col2:
    category = st.selectbox("Category", [
        "All", "Business", "Technology", "Sports", 
        "Entertainment", "Health", "Science",
        "World", "Politics"
    ])

# Search button with loading state
if st.button("🔎 Search News"):
    if not search_query and category == "All":
        st.warning("Please enter a search term or select a category")
    else:
        with st.spinner("Searching for news..."):
            articles = scrape_news(search_query if search_query else category)
            
            if articles:
                # Display results count and search info
                st.success(f"Found {len(articles)} articles about '{search_query or category}'")
                
                # Articles display
                for article in articles:
                    sentiment_class = {
                        "POSITIVE": "sentiment-positive",
                        "NEGATIVE": "sentiment-negative",
                        "NEUTRAL": "sentiment-neutral"
                    }.get(article['sentiment'], "sentiment-neutral")
                    
                    st.markdown(f"""
                    <div class='result-card'>
                        <div>
                            <span class='sentiment-badge {sentiment_class}'>
                                {article['sentiment']}
                            </span>
                            <small>Topics: {', '.join(article['topics'])}</small>
                        </div>
                        <h3><a href="{article['link']}" target="_blank">{article['title']}</a></h3>
                        <p>{article['summary']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Sentiment Analysis
                st.markdown("### 📊 Sentiment Analysis")
                result = comparative_analysis(articles)
                sentiment_data = result.get("Sentiment Distribution", {})
                if sentiment_data:
                    col1, col2 = st.columns(2)
                    with col1:
                        df = pd.DataFrame(list(sentiment_data.items()), columns=["Sentiment", "Count"])
                        fig = px.pie(df, names="Sentiment", values="Count", title="Sentiment Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        fig = px.bar(df, x="Sentiment", y="Count", title="Sentiment Breakdown")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Audio Summary
                st.markdown("### 🎧 Audio Summary")
                summary_text = " ".join([a['summary'] for a in articles[:3]])
                if st.button("🔊 Generate Audio Summary"):
                    with st.spinner(f"Generating {selected_lang_label} audio..."):
                        audio_file, translated_text = text_to_speech(summary_text, language=lang_code)
                        if audio_file:
                            st.audio(audio_file)
                            st.download_button(
                                "⬇️ Download Audio Summary",
                                open(audio_file, "rb"),
                                "news_summary.mp3",
                                "audio/mp3"
                            )
                            st.markdown("#### 📝 Translated Summary")
                            st.markdown(
                                f"<div class='translated-text'>{translated_text}</div>",
                                unsafe_allow_html=True
                            )
            else:
                st.error("No articles found. Try a different search term or category.")

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
st.sidebar.markdown("## 📰 News Category")
selected_category = st.sidebar.selectbox("Choose News Category", news_categories, key="news_category")

# --- Page Header ---
st.markdown("""
<style>
.news-header {
    background: linear-gradient(90deg, #0f2027, #2c5364);
    color: white;
    padding: 30px 0 10px 0;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.news-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 24px;
    padding: 24px;
    transition: box-shadow 0.2s;
    border-left: 6px solid #2c5364;
}
.news-card * {
    color: #000 !important;
}
.news-card h3 {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
    color: #000 !important;
}
.news-card p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #000 !important;
}
.news-card .news-meta {
    font-size: 0.9rem;
    color: #000 !important;
    margin-top: 0.75rem;
}
[data-theme="dark"] .news-card {
    background: #161B22;
}
[data-theme="dark"] .news-card *,
[data-theme="dark"] .news-card h3,
[data-theme="dark"] .news-card p,
[data-theme="dark"] .news-card .news-meta {
    color: #fff !important;
}
.news-card:hover {
    box-shadow: 0 6px 24px rgba(44,83,100,0.15);
    border-left: 6px solid #ffcc00;
}
</style>
<div class='news-header'>
    <h1>📰 News Search & Analysis</h1>
    <p style='font-size: 1.2em; margin-top: 10px;'>Search for news by company or topic, analyze sentiment, and get audio summaries</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for articles
if 'articles' not in st.session_state:
    st.session_state.articles = []

# --- Input Section ---
with st.container():
    st.markdown("### 🔍 Enter Company or Keyword")
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input("Company or Keyword", placeholder="e.g., Tesla, Olympics, COVID")
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
            articles = scrape_news(company_name or selected_category)
            st.session_state.articles = articles
            
        if not articles:
            st.warning("❌ No articles found.")

# --- Display News and Analysis ---
if st.session_state.articles:
    filtered_articles = st.session_state.articles
    if selected_category != "All":
        filtered_articles = [a for a in st.session_state.articles if selected_category.lower() in [t.lower() for t in a.get('topics', [])]]

    # Display Articles
    st.markdown(f"### 📰 {selected_category} News Articles")
    for article in filtered_articles:
        sentiment_class = {
            'POSITIVE': 'sentiment-positive',
            'NEGATIVE': 'sentiment-negative',
            'NEUTRAL': 'sentiment-neutral'
        }.get(article['sentiment'], 'sentiment-neutral')
        
        st.markdown(f"""
        <div class='result-card'>
            <a href='{article['link']}' target='_blank' style='text-decoration: none;'>
                <h3>{article['title']}</h3>
            </a>
            <p>{article['summary']}</p>
            <div class='news-meta'>
                <span class='sentiment-badge {sentiment_class}'>
                    {article['sentiment']}
                </span>
                Topics: {', '.join(article['topics'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sentiment Analysis
    result = comparative_analysis(st.session_state.articles)
    sentiment_data = result.get("Sentiment Distribution", {})
    if sentiment_data:
        st.markdown("### 📊 Sentiment Analysis")
        df = pd.DataFrame(list(sentiment_data.items()), columns=["Sentiment", "Count"])
        col1, col2 = st.columns(2)
        with col1:
            pie = px.pie(df, names="Sentiment", values="Count", title="Sentiment Distribution")
            st.plotly_chart(pie, use_container_width=True)
        with col2:
            bar = px.bar(df, x="Sentiment", y="Count", title="Sentiment Breakdown", color="Sentiment")
            st.plotly_chart(bar, use_container_width=True)

    # Topic Analysis
    all_topics = [t for article in st.session_state.articles for t in article.get("topics", [])]
    topic_counts = Counter(all_topics)
    if topic_counts:
        st.markdown("### 🧠 Topic Analysis")
        df_topics = pd.DataFrame(topic_counts.items(), columns=["Topic", "Count"])
        topic_bar = px.bar(
            df_topics.sort_values("Count", ascending=False),
            x="Topic",
            y="Count",
            title="Topics Frequency",
            color="Topic"
        )
        st.plotly_chart(topic_bar, use_container_width=True)

    # Audio Summary
    st.markdown("### 🎧 Audio Summary")
    summary_text = " ".join([a['summary'] for a in filtered_articles[:3]])
    if summary_text:
        if st.button("🔊 Generate Audio Summary"):
            with st.spinner(f"Generating {selected_lang_label} audio..."):
                audio_file, translated_text = text_to_speech(summary_text, language=lang_code)
                if audio_file:
                    st.audio(audio_file)
                    with open(audio_file, "rb") as f:
                        st.download_button("⬇️ Download Audio", f, "news_summary.mp3", "audio/mp3")
                    st.markdown("#### 📝 Translated Text")
                    st.markdown(
                        f"<div class='translated-text'>{translated_text}</div>",
                        unsafe_allow_html=True
                    )