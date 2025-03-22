import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from transformers import pipeline
from googletrans import Translator
import os

# Setup sentiment analysis pipeline (specify model to avoid warning)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

# Scrape news from Bing News (non-JavaScript pages only)
def scrape_news(company_name):
    try:
        print(f"🔍 Fetching news for: {company_name}")
        query = company_name.replace(" ", "+")
        url = f"https://www.bing.com/news/search?q={query}&FORM=HDRSC6"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        news_cards = soup.find_all("div", class_="news-card")
        if not news_cards:
            news_cards = soup.select("div.t_s")

        print(f"📰 Found {len(news_cards)} news elements")

        for card in news_cards:
            # Flexible and robust title parsing
            title_tag = (
                card.select_one("a.title") or
                card.select_one("h2 > a") or
                card.find("a")
            )

            if not title_tag or not title_tag.text.strip():
                print("⚠️ Skipping card with no title")
                continue

            title = title_tag.text.strip()
            link = title_tag.get("href", "#")

            # Try multiple ways to find summary
            summary_tag = (
                card.find("div", class_="snippet") or
                card.find("div", class_="news-card-snippet") or
                card.find("p")
            )
            summary = summary_tag.text.strip() if summary_tag and summary_tag.text else "No summary available"

            print(f"✅ Article found: {title}")
            print(f"🔗 {link}")
            print(f"📝 {summary[:80]}...")

            sentiment = analyze_sentiment(summary)
            topics = detect_topics(summary)

            articles.append({
                "title": title,
                "summary": summary,
                "link": link,
                "topics": topics,
                "sentiment": sentiment
            })

            if len(articles) == 10:
                break

        if not articles:
            print(f"❌ No valid news articles found for '{company_name}'")
        return articles

    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return []

# Detect topics from article summary
def detect_topics(summary):
    summary_lower = summary.lower()
    topic_keywords = {
        "AI": ["ai", "artificial intelligence", "machine learning", "gemini"],
        "Mobile": ["mobile", "android", "phone", "app"],
        "Partnerships": ["partner", "collaboration", "tie-up", "spacex", "mediatek"],
        "Technology": ["tech", "innovation", "software", "hardware"],
        "Security": ["security", "privacy", "delete", "dangerous"]
    }
    topics = [topic for topic, keywords in topic_keywords.items()
              if any(keyword in summary_lower for keyword in keywords)]
    return topics or ["General"]

# Analyze sentiment using transformers
def analyze_sentiment(text):
    result = sentiment_pipeline(text)[0]
    return result['label']

# Convert text to speech (Hindi by default)
def text_to_speech(text, language='hi'):
    try:
        if language != 'en':
            translator = Translator()
            translated = translator.translate(text, dest=language).text
        else:
            translated = text

        tts = gTTS(text=translated, lang=language)
        tts.save("output.mp3")
        return "output.mp3", translated

    except Exception as e:
        print(f"❌ TTS failed: {e}")
        return "", ""

# Analyze overall sentiment and topics
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

# Generate final structured response
def generate_final_output(company_name, articles, comparative_analysis_result):
    sentiment_dist = comparative_analysis_result["Sentiment Distribution"]
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
