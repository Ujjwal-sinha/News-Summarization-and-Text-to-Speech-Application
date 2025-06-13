import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from transformers import pipeline
from googletrans import Translator
import tempfile
import os
import logging
import ffmpeg
import textwrap
import platform

# Setup logging
logging.basicConfig(level=logging.INFO)

# Setup sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

def scrape_news(company_name):
    try:
        logging.info(f"🔍 Fetching news for: {company_name}")
        query = company_name.replace(" ", "+")
        url = f"https://www.bing.com/news/search?q={query}&FORM=HDRSC6"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        news_cards = soup.find_all("div", class_="news-card") or soup.select("div.t_s")
        logging.info(f"📰 Found {len(news_cards)} news elements")

        for card in news_cards:
            title_tag = card.select_one("a.title") or card.select_one("h2 > a") or card.find("a")
            if not title_tag or not title_tag.text.strip():
                logging.warning("⚠️ Skipping card with no title")
                continue

            title = title_tag.text.strip()
            link = title_tag.get("href", "#")
            summary_tag = card.find("div", class_="snippet") or card.find("div", class_="news-card-snippet") or card.find("p")
            summary = summary_tag.text.strip() if summary_tag and summary_tag.text else "No summary available"
            logging.info(f"✅ Article found: {title}")

            sentiment = analyze_sentiment(summary)
            topics = detect_topics(summary)
            articles.append({"title": title, "summary": summary, "link": link, "topics": topics, "sentiment": sentiment})
            if len(articles) == 10:
                break

        if not articles:
            logging.warning(f"❌ No valid news articles found for '{company_name}'")
        return articles

    except Exception as e:
        logging.error(f"❌ Scraping failed: {e}")
        return []

def detect_topics(summary):
    summary_lower = summary.lower()
    topic_keywords = {
        "AI": ["ai", "artificial intelligence", "machine learning", "gemini"],
        "Mobile": ["mobile", "android", "phone", "app"],
        "Partnerships": ["partner", "collaboration", "tie-up", "spacex", "mediatek"],
        "Technology": ["tech", "innovation", "software", "hardware"],
        "Security": ["security", "privacy", "delete", "dangerous"]
    }
    topics = [topic for topic, keywords in topic_keywords.items() if any(keyword in summary_lower for keyword in keywords)]
    return topics or ["General"]

def analyze_sentiment(text):
    try:
        result = sentiment_pipeline(text)[0]
        return result['label']
    except Exception as e:
        logging.error(f"❌ Sentiment analysis failed: {e}")
        return "N/A"

def text_to_speech(text, language='hi'):
    try:
        translator = Translator()
        translated = translator.translate(text, dest=language).text if language != 'en' else text
        audio_path = tempfile.mktemp(suffix=".mp3")
        gTTS(text=translated, lang=language).save(audio_path)
        return audio_path, translated
    except Exception as e:
        logging.error(f"❌ TTS failed: {e}")
        return "", ""

def escape_ffmpeg_text(text):
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if not text:
        return ""
    escape_chars = {
        '\\': '\\\\', ':': '\\:', "'": "\\'", ',': '\\,', '%': '\\%', '\n': ' ',
        '"': '\\"', '=': '\\=', '[': '\\[', ']': '\\]', '{': '\\{', '}': '\\}',
        '$': '\\$', '#': '\\#', '@': '\\@', '&': '\\&'
    }
    result = text
    for char, escaped in escape_chars.items():
        result = result.replace(char, escaped)
    if len(result) > 200:
        result = result[:200].rsplit(' ', 1)[0] + '...'
    return result.strip()

def get_default_font_path():
    system = platform.system()
    if system == "Darwin":
        return "/System/Library/Fonts/Supplemental/Arial.ttf"
    elif system == "Windows":
        return "C:/Windows/Fonts/arial.ttf"
    else:
        return "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

def generate_news_reel(text, language="hi", output_file="news_reel.mp4", font_size=30, bg_color="black", image_path=None):
    audio_path = None
    video_no_audio_path = None
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")

        translator = Translator()
        translated_text = translator.translate(text, dest=language).text if language != "en" else text

        # Generate audio
        audio_path = tempfile.mktemp(suffix=".mp3")
        gTTS(text=translated_text, lang=language).save(audio_path)

        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe['format']['duration'])
        if audio_duration < 2:
            audio_duration = 5.0

        # Wrap subtitle text
        wrapped_lines = textwrap.wrap(translated_text, width=40)
        duration_per_line = audio_duration / max(len(wrapped_lines), 1)

        # Use multilingual font
        font_path = get_default_font_path()
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font not found: {font_path}")

        drawtext_filters = []
        for idx, line in enumerate(wrapped_lines):
            safe_line = escape_ffmpeg_text(line)
            if not safe_line:
                continue
            start = idx * duration_per_line
            end = start + duration_per_line
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}':text='{safe_line}':fontcolor=white:fontsize={font_size}:x=(w-text_w)/2:y=h-100:enable='between(t,{start:.2f},{end:.2f})'"
            )
        full_filter = ",".join(drawtext_filters)
        video_no_audio_path = tempfile.mktemp(suffix=".mp4")

        # --- Add background image or animation if provided ---
        if image_path and os.path.exists(image_path):
            # Use the image as a background, loop it for the duration
            (
                ffmpeg
                .input(image_path, loop=1, t=audio_duration)
                .output(video_no_audio_path, vf=full_filter, vcodec="libx264", pix_fmt="yuv420p", r=30)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        else:
            # Use a color background with a simple fade animation
            (
                ffmpeg
                .input(f"color={bg_color}:s=720x1280:r=30", f="lavfi", t=audio_duration)
                .output(video_no_audio_path, vf=f"fade=in:0:30,{full_filter}", vcodec="libx264", pix_fmt="yuv420p")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

        # Combine with audio
        (
            ffmpeg
            .output(ffmpeg.input(video_no_audio_path), ffmpeg.input(audio_path), output_file,
                    vcodec='copy', acodec='aac', shortest=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Cleanup
        for f in [audio_path, video_no_audio_path]:
            if f and os.path.exists(f):
                os.remove(f)

        logging.info(f"✅ News reel created: {output_file}")
        return output_file

    except Exception as e:
        logging.error("❌ FFmpeg error while generating video:")
        logging.error(f"STDOUT:\n{e.stdout.decode(errors='ignore') if hasattr(e, 'stdout') and e.stdout else '(no stdout)'}")
        logging.error(f"STDERR:\n{e.stderr.decode(errors='ignore') if hasattr(e, 'stderr') and e.stderr else '(no stderr)'}")
        return ""
    except Exception as e:
        logging.error(f"❌ News reel generation failed: {str(e)}")
        return ""


def comparative_analysis(articles):
    sentiment_distribution = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for article in articles:
        sentiment = article['sentiment']
        sentiment_distribution['Positive' if sentiment == 'POSITIVE' else 'Negative' if sentiment == 'NEGATIVE' else 'Neutral'] += 1

    coverage_differences = [
        {"Comparison": f"{articles[i]['title']} vs {articles[i+1]['title']}", "Impact": "Varies by content"}
        for i in range(min(len(articles)-1, 1))
    ] if len(articles) > 1 else []

    topic_overlap = {
        "Common Topics": ["Technology"],
        "Unique Topics": list(set([t for a in articles for t in a['topics']]))
    }

    return {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": topic_overlap
    }

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

    return {
        "Company": company_name,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_analysis_result,
        "Final Sentiment Analysis": sentiment_summary,
        "Audio": "[Play Hindi Speech]"
    }

def generate_article_summary(articles):
    """Generate a concise summary of multiple articles."""
    # Fallback to basic summary only, no Groq LLM
    return " ".join([a['summary'] for a in articles[:3]])

if __name__ == "__main__":
    company = "Google"
    articles = scrape_news(company)
    if articles:
        reel_file = generate_news_reel(articles[0]["summary"])
        logging.info(f"🎥 Reel generated: {reel_file}")
        analysis = comparative_analysis(articles)
        output = generate_final_output(company, articles, analysis)
        print(output)