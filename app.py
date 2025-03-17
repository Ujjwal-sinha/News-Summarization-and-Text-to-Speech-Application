import streamlit as st
from utils import scrape_news, analyze_sentiment, text_to_speech, comparative_analysis, generate_final_output
import os

st.set_page_config(page_title="News Summarization App", page_icon="📰")

st.title("News Summarization and Text-to-Speech Application")

company_name = st.text_input("Enter Company Name", placeholder="e.g., Google")

if st.button("Fetch News"):
    if not company_name:
        st.error("Please enter a company name.")
    else:
        with st.spinner("Fetching news articles..."):
            articles = scrape_news(company_name)
        
        if not articles:
            st.warning(f"No articles found for '{company_name}'.")
        else:
            comparative_analysis_result = comparative_analysis(articles)
            final_output = generate_final_output(company_name, articles, comparative_analysis_result)
            
            st.subheader("Analysis Results")
            st.json(final_output)
            
            st.subheader("Audio Summary (in Hindi)")
            summary_text = " ".join([article['summary'] for article in articles])
            try:
                audio_file = text_to_speech(summary_text)
                if os.path.exists(audio_file):
                    st.audio(audio_file, format="audio/mp3")
                    st.button("Clear Audio", on_click=lambda: os.remove(audio_file) if os.path.exists(audio_file) else None)
                else:
                    st.error("Failed to generate audio file.")
            except Exception as e:
                st.error(f"Error generating audio: {e}")

st.markdown("---")
st.write("Built with ❤️ by UJJWAL SINHA")