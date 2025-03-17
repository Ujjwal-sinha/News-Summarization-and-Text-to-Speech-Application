import streamlit as st
from utils import scrape_news, analyze_sentiment, text_to_speech, comparative_analysis, generate_final_output
import os

# Set page config for a polished UI
st.set_page_config(page_title="News Summarization App", page_icon="📰", layout="wide")

st.title("News Summarization and Text-to-Speech Application")

# Input with validation
company_name = st.text_input("Enter Company Name", placeholder="e.g., Google", help="Enter a company like Google or Tesla")

if st.button("Fetch News"):
    if not company_name.strip():  # Check for empty or whitespace-only input
        st.error("Please enter a valid company name.")
    else:
        with st.spinner(f"Fetching news articles for '{company_name}'..."):
            articles = scrape_news(company_name)
        
        if not articles:
            st.warning(f"No articles found for '{company_name}'. Check the logs or try another company.")
            st.info("This could be due to scraping restrictions or no recent news.")
        else:
            # Process results
            comparative_analysis_result = comparative_analysis(articles)
            final_output = generate_final_output(company_name, articles, comparative_analysis_result)
            
            # Display results
            st.subheader("Analysis Results")
            st.json(final_output)
            
            # Audio section
            st.subheader("Audio Summary (in Hindi)")
            summary_text = " ".join([article['summary'] for article in articles])
            try:
                audio_file = text_to_speech(summary_text)
                if os.path.exists(audio_file):
                    st.audio(audio_file, format="audio/mp3")
                    # Improved Clear Audio button with feedback
                    if st.button("Clear Audio"):
                        if os.path.exists(audio_file):
                            os.remove(audio_file)
                            st.success("Audio file cleared successfully.")
                        else:
                            st.warning("No audio file to clear.")
                else:
                    st.error("Failed to generate audio file.")
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")

# Footer
st.markdown("---")
st.write("Built with ❤️ by Ujjwal Sinha ")