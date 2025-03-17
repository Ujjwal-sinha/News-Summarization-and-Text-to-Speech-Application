from bs4 import BeautifulSoup
from transformers import pipeline
from gtts import gTTS
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import streamlit as st

def scrape_news(company_name):
    """Scrape news articles from Google News for the given company."""
    try:
        # Configure Chrome options for Streamlit Cloud
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://news.google.com/search?q={company_name}"
        st.write(f"DEBUG: Fetching URL: {url}")
        driver.get(url)

        # Wait for articles to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        time.sleep(3)  # Buffer for dynamic content
        
        # Parse page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = []
        article_tags = soup.find_all('article')
        st.write(f"DEBUG: Found {len(article_tags)} article tags")

        # Topic keywords for dynamic assignment
        topic_keywords = {
            "AI": ["ai", "artificial intelligence", "machine learning", "gemini"],
            "Mobile": ["mobile", "android", "phone", "app"],
            "Partnerships": ["partner", "collaboration", "tie-up", "spacex", "mediatek"],
            "Technology": ["tech", "innovation", "software", "hardware"],
            "Security": ["security", "privacy", "delete", "dangerous"]
        }

        for item in article_tags[:10]:
            title_element = item.find('a', class_='JtKRv')
            summary_element = item.find(['div', 'span'])  # Broad search for summary
            
            if title_element:
                title = title_element.get_text(strip=True)
                link = "https://news.google.com" + title_element['href'].lstrip('.')
                summary = summary_element.get_text(strip=True) if summary_element and summary_element.get_text(strip=True) else "No summary available"
                
                # Topic detection
                summary_lower = summary.lower()
                topics = [topic for topic, keywords in topic_keywords.items() if any(kw in summary_lower for kw in keywords)] or ["General"]
                
                sentiment = analyze_sentiment(summary)
                articles.append({
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'topics': topics,
                    'sentiment': sentiment
                })
            else:
                st.write("DEBUG: Skipping article - no title found")

        if not articles:
            st.write(f"DEBUG: No articles processed for '{company_name}'")

        driver.quit()
        return articles

    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def analyze_sentiment(text):
    """Analyze sentiment of the given text using a pre-trained model."""
    global sentiment_pipeline
    if 'sentiment_pipeline' not in globals():
        # Lazy load to avoid PyTorch/Streamlit conflict
        sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    result = sentiment_pipeline(text)[0]
    return result['label']

def text_to_speech(text, language='hi'):
    """Convert text to speech in the specified language (default: Hindi)."""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_file = "output.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        raise Exception(f"TTS failed: {str(e)}")

def comparative_analysis(articles):
    """Perform comparative analysis on the list of articles."""
    sentiment_distribution = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for article in articles:
        sentiment = article['sentiment']
        if sentiment == 'POSITIVE':
            sentiment_distribution['Positive'] += 1
        elif sentiment == 'NEGATIVE':
            sentiment_distribution['Negative'] += 1
        else:
            sentiment_distribution['Neutral'] += 1
   
    topic_overlap = {
        "Common Topics": ["Technology"],
        "Unique Topics in Article 1": ["AI", "Mobile"],
        "Unique Topics in Article 2": ["Partnerships", "Hardware"]
    }
    return {
        "Sentiment Distribution": sentiment_distribution,
       
        "Topic Overlap": topic_overlap
    }

def generate_final_output(company_name, articles, comparative_analysis_result):
    """Generate the final structured output for display."""
    sentiment_dist = comparative_analysis_result["Sentiment Distribution"]
    dominant_sentiment = max(sentiment_dist, key=sentiment_dist.get)
    sentiment_summary = f"{company_name}'s latest news coverage is mostly {dominant_sentiment.lower()}."
    if dominant_sentiment == "Positive":
        sentiment_summary += " Potential stock growth expected."
    elif dominant_sentiment == "Negative":
        sentiment_summary += " Potential challenges ahead."
    else:
        sentiment_summary += " Market outlook remains neutral."
    return {
        "Company": company_name,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_analysis_result,
        "Final Sentiment Analysis": sentiment_summary,
        "Audio": "[Play Hindi Speech]"
    }