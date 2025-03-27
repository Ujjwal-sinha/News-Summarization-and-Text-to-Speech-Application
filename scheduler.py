from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import shutil
from utils import scrape_news, text_to_speech
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define directories and files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
ALERTS_FILE = os.path.join(BASE_DIR, "alerts.json")
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "notifications.json")
CHECK_INTERVAL = 3600  # Check every hour (in seconds)
MAX_NOTIFICATIONS = 50  # Maximum number of notifications to keep

# Ensure audio directory exists
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def load_json(file_path, default=[]):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return default
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return default

def save_notifications(notifications):
    try:
        # Keep only the most recent notifications
        if len(notifications) > MAX_NOTIFICATIONS:
            notifications = notifications[-MAX_NOTIFICATIONS:]
        with open(NOTIFICATIONS_FILE, "w") as f:
            json.dump(notifications, f)
    except Exception as e:
        logging.error(f"Failed to save notifications: {e}")

def check_news():
    alerts = load_json(ALERTS_FILE)
    if not alerts:
        logging.info("No alerts to check.")
        return

    notifications = load_json(NOTIFICATIONS_FILE)
    current_time = datetime.now().isoformat()

    for term in alerts:
        logging.info(f"Checking news for alert: {term}")
        articles = scrape_news(term)
        if articles:
            existing_titles = {n['message'].split(': ')[-1] for n in notifications if n['term'] == term}
            new_articles = [a for a in articles if a['title'] not in existing_titles]
            
            if new_articles:
                summary_text = " ".join([a['summary'] for a in new_articles[:1]])
                temp_audio, translated_text = text_to_speech(summary_text, language='en')
                if temp_audio:
                    # Move audio to a persistent location
                    audio_file = os.path.join(AUDIO_DIR, f"alert_{term}_{current_time.replace(':', '-')}.mp3")
                    shutil.move(temp_audio, audio_file)
                    
                    notification = {
                        "term": term,
                        "message": f"New news for '{term}': {new_articles[0]['title']}",
                        "audio_file": audio_file,
                        "timestamp": current_time,
                        "articles": new_articles,  # Store all new articles
                        "read": False  # Mark as unread
                    }
                    notifications.append(notification)
                    logging.info(f"New notification added for {term}")

    save_notifications(notifications)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_news, 'interval', seconds=CHECK_INTERVAL)
    scheduler.start()
    logging.info(f"Scheduler started, checking every {CHECK_INTERVAL} seconds. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()