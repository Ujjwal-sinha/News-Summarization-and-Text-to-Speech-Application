import streamlit as st
import json
import os
from datetime import datetime
from utils import scrape_news, text_to_speech

# Page config
st.set_page_config(page_title="News Alerts", page_icon="🔔", layout="wide")

# Constants
ALERTS_FILE = "alerts.json"
NOTIFICATIONS_FILE = "notifications.json"

# --- Styles ---
st.markdown("""
<style>
.alert-header {
    background: linear-gradient(90deg, #232526, #414345);
    color: white;
    padding: 2rem 0;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.alert-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}
.alert-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 4px solid #2c5364;
}
.alert-card h3, .alert-card h4, .alert-card p, .alert-card div {
    color: #000 !important;
}
[data-theme="dark"] .alert-card {
    background: #161B22;
}
[data-theme="dark"] .alert-card h3,
[data-theme="dark"] .alert-card h4,
[data-theme="dark"] .alert-card p,
[data-theme="dark"] .alert-card div {
    color: #fff !important;
}
[data-theme="dark"] .notification-card {
    background: #1a2029;
    color: #fff !important;
}
.alert-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    border-left: 4px solid #ffcc00;
}
.notification-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #1890ff;
}
.notification-unread {
    background: #e6f7ff;
    border-left: 4px solid #1890ff;
}
[data-theme="dark"] .notification-unread {
    background: #1a2029;
    border-left: 4px solid #1890ff;
}
</style>

<div class='alert-header'>
    <h1>🔔 News Alerts</h1>
    <p style='font-size: 1.2em; margin-top: 1rem;'>
        Stay updated with personalized news alerts
    </p>
</div>
""", unsafe_allow_html=True)

# Helper functions
def load_json(file_path, default=[]):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return default
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return default

def save_json(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Error saving to {file_path}: {e}")
        return False

# Load data
alerts = load_json(ALERTS_FILE)
notifications = load_json(NOTIFICATIONS_FILE)

# Main container
st.markdown("<div class='alert-container'>", unsafe_allow_html=True)

# Set New Alert
st.markdown("### ➕ Set New Alert")
with st.form("new_alert_form"):
    alert_term = st.text_input("Enter keyword or company name", placeholder="e.g., Tesla, Climate Change, AI")
    col1, col2 = st.columns(2)
    with col1:
        immediate_check = st.checkbox("Check for news immediately")
    with col2:
        notify_email = st.checkbox("Email notifications (Coming soon)")
    
    if st.form_submit_button("Add Alert"):
        if alert_term.strip():
            if alert_term not in alerts:
                alerts.append(alert_term)
                if save_json(ALERTS_FILE, alerts):
                    st.success(f"Alert set for '{alert_term}'!")
                    
                    if immediate_check:
                        with st.spinner(f"Checking news for '{alert_term}'..."):
                            articles = scrape_news(alert_term)
                            if articles:
                                notification = {
                                    "term": alert_term,
                                    "message": f"Found {len(articles)} new articles about '{alert_term}'",
                                    "timestamp": datetime.now().isoformat(),
                                    "articles": articles,
                                    "read": False
                                }
                                notifications.append(notification)
                                save_json(NOTIFICATIONS_FILE, notifications)
                                st.success(f"Found {len(articles)} articles!")
            else:
                st.warning("This alert already exists.")
        else:
            st.error("Please enter a valid term.")

# Manage Existing Alerts
if alerts:
    st.markdown("### 📝 Your Alerts")
    for term in alerts:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class='alert-card'>
                    <h3>{term}</h3>
                    <p>Monitoring for news updates</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️ Remove", key=f"remove_{term}"):
                    alerts.remove(term)
                    if save_json(ALERTS_FILE, alerts):
                        st.success(f"Alert for '{term}' removed.")
                        st.rerun()

# Show Notifications
if notifications:
    st.markdown("### 🔔 Notifications")
    
    # Mark all as read button
    if st.button("📭 Mark All as Read"):
        for notif in notifications:
            notif['read'] = True
        if save_json(NOTIFICATIONS_FILE, notifications):
            st.success("All notifications marked as read.")
            st.rerun()
    
    # Display notifications
    for notif in reversed(notifications):  # Show newest first
        notification_class = "notification-card notification-unread" if not notif.get('read') else "notification-card"
        
        st.markdown(f"""
        <div class='{notification_class}'>
            <h4>{notif['term']}</h4>
            <p>{notif['message']}</p>
            <small>🕒 {notif['timestamp'].split('T')[0]}</small>
        </div>
        """, unsafe_allow_html=True)
        
        if not notif.get('read'):
            if st.button("✓ Mark as Read", key=f"read_{notif['timestamp']}"):
                notif['read'] = True
                save_json(NOTIFICATIONS_FILE, notifications)
                st.rerun()
        
        # Show articles if available
        if 'articles' in notif and notif['articles']:
            with st.expander("📰 View Articles"):
                for article in notif['articles']:
                    st.markdown(f"**{article['title']}**")
                    st.write(article['summary'])
                    st.markdown(f"Sentiment: {article['sentiment']} | [Read More]({article['link']})")
                    st.markdown("---")

else:
    st.info("No notifications yet. Set up alerts to start receiving updates!")

st.markdown("</div>", unsafe_allow_html=True)  # Close main container