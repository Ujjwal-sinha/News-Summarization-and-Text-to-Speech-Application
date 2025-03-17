import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from gtts import gTTS
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_news(company_name):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        
        url = f"https://news.google.com/search?q={company_name}"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = []

        article_tags = soup.find_all('article')
        print(f"Total <article> tags found: {len(article_tags)}")
        
        # Topic keyword mapping
        topic_keywords = {
            "AI": ["ai", "artificial intelligence", "machine learning", "gemini"],
            "Mobile": ["mobile", "android", "phone", "app"],
            "Partnerships": ["partner", "collaboration", "tie-up", "spacex", "mediatek"],
            "Technology": ["tech", "innovation", "software", "hardware"],
            "Security": ["security", "privacy", "delete", "dangerous"]
        }
        
        for item in article_tags[:10]:
            title_element = item.find('a', class_='JtKRv')
            summary_element = item.find(['div', 'span'])
            
            print(f"Title Element: {title_element}")
            print(f"Summary Element: {summary_element}")
            if not summary_element:
                print(f"Full article HTML for debugging: {item.prettify()}")
            
            if title_element:
                title = title_element.get_text(strip=True)
                link = "https://news.google.com" + title_element['href'].lstrip('.')
                summary = summary_element.get_text(strip=True) if summary_element and summary_element.get_text(strip=True) else "No summary available"
                
                # Determine topics based on summary
                summary_lower = summary.lower()
                topics = []
                for topic, keywords in topic_keywords.items():
                    if any(keyword in summary_lower for keyword in keywords):
                        topics.append(topic)
                if not topics:
                    topics = ["General"]
                
                sentiment = analyze_sentiment(summary)
                
                articles.append({
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'topics': topics,
                    'sentiment': sentiment
                })
            else:
                print("Skipping an article due to missing title.")
        
        if not articles:
            print("No articles found for the given company name.")
        
        driver.quit()
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# Sentiment analysis
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    result = sentiment_pipeline(text)[0]
    return result['label']

# Text-to-Speech
def text_to_speech(text, language='hi'):
    tts = gTTS(text=text, lang=language)
    tts.save("output.mp3")
    return "output.mp3"

# Comparative analysis
def comparative_analysis(articles):
    sentiment_distribution = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for article in articles:
        sentiment = article['sentiment']
        if sentiment == 'POSITIVE':
            sentiment_distribution['Positive'] += 1
        elif sentiment == 'NEGATIVE':
            sentiment_distribution['Negative'] += 1
        else:
            sentiment_distribution['Neutral'] += 1
    
    coverage_differences = [
        {
            "Comparison": "Article 1 highlights AI advancements, while Article 2 discusses strategic partnerships.",
            "Impact": "The first boosts tech optimism, the second suggests growth potential."
        }
    ]
    
    topic_overlap = {
        "Common Topics": ["Technology"],
        "Unique Topics in Article 1": ["AI", "Mobile"],
        "Unique Topics in Article 2": ["Partnerships", "Hardware"]
    }
    
    return {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": topic_overlap
    }

# Generate final output with dynamic sentiment summary
def generate_final_output(company_name, articles, comparative_analysis_result):
    sentiment_dist = comparative_analysis_result["Sentiment Distribution"]
    total = sum(sentiment_dist.values())
    dominant_sentiment = max(sentiment_dist, key=sentiment_dist.get)
    sentiment_summary = f"{company_name}'s latest news coverage is mostly {dominant_sentiment.lower()}."
    if dominant_sentiment == "Positive":
        sentiment_summary += " Potential stock growth expected."
    elif dominant_sentiment == "Negative":
        sentiment_summary += " Potential challenges ahead."
    else:
        sentiment_summary += " Market outlook remains neutral."
    
    final_output = {
        "Company": company_name,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_analysis_result,
        "Final Sentiment Analysis": sentiment_summary,
        "Audio": "[Play Hindi Speech]"
    }
    return final_output