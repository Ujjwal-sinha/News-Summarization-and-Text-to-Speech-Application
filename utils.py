from bs4 import BeautifulSoup
from transformers import pipeline
from gtts import gTTS
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import streamlit as st


def scrape_news(company_name):
    """Scrape news articles from Google News for the given company."""
    driver = None
    try:
        # Configure Chrome options for Streamlit Cloud
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
        
        # Use ChromeDriverManager to download and get the driver path
        driver_path = ChromeDriverManager().install()
        driver_dir = os.path.dirname(driver_path)
        
        # Debug: List directory contents
        st.write(f"DEBUG: Driver directory: {driver_dir}")
        st.write(f"DEBUG: Directory contents: {os.listdir(driver_dir)}")
        
        # Look for the chromedriver executable
        executable_path = os.path.join(driver_dir, "chromedriver")
        
        if not os.path.isfile(executable_path):
            raise FileNotFoundError(f"chromedriver not found in {driver_dir}. Available files: {os.listdir(driver_dir)}")
        
        # Ensure it’s executable
        if not os.access(executable_path, os.X_OK):
            st.write(f"DEBUG: Setting executable permissions for {executable_path}")
            os.chmod(executable_path, 0o755)  # Make it executable (rwxr-xr-x)
        
        # Verify permissions after setting
        if not os.access(executable_path, os.X_OK):
            raise PermissionError(f"Could not make {executable_path} executable. Check system permissions.")
        
        st.write(f"DEBUG: Using ChromeDriver at {executable_path}")
        service = Service(executable_path=executable_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = f"https://news.google.com/search?q={company_name}"
        st.write(f"DEBUG: Fetching URL: {url}")
        driver.get(url)

        # Wait for articles to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        time.sleep(5)  # Buffer for dynamic content
        
        # Parse page source with BeautifulSoup
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
                
                # Topic detection using both title and summary
                text_to_analyze = (title + " " + summary).lower()
                topics = [topic for topic, keywords in topic_keywords.items() if any(kw in text_to_analyze for kw in keywords)] or ["General"]
                
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

        return articles

    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()

# Rest of the functions remain unchanged
def analyze_sentiment(text):
    """Analyze sentiment of the given text using a pre-trained model."""
    global sentiment_pipeline
    if 'sentiment_pipeline' not in globals():
        sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    result = sentiment_pipeline(text)[0]
    return "Positive" if result['label'] == "POSITIVE" else "Negative"

def text_to_speech(text, language='hi'):
    """Convert text to speech in the specified language (default: Hindi)."""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_file = "output.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        st.error(f"TTS failed: {str(e)}")
        return None

def comparative_analysis(articles):
    """Perform comparative analysis on the list of articles."""
    sentiment_distribution = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for article in articles:
        sentiment = article['sentiment']
        if sentiment == 'Positive':
            sentiment_distribution['Positive'] += 1
        elif sentiment == 'Negative':
            sentiment_distribution['Negative'] += 1
        else:
            sentiment_distribution['Neutral'] += 1
   
    all_topics = [topic for article in articles for topic in article['topics']]
    common_topics = list(set.intersection(*[set(article['topics']) for article in articles])) if articles else ["Technology"]
    topic_overlap = {
        "Common Topics": common_topics,
        "Unique Topics in Article 1": list(set(articles[0]['topics']) - set(common_topics)) if articles else ["AI", "Mobile"],
        "Unique Topics in Article 2": list(set(articles[1]['topics']) - set(common_topics)) if len(articles) > 1 else ["Partnerships", "Hardware"]
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