import streamlit as st
import os
import pandas as pd
import plotly.express as px
import requests
import json
from utils import (
    scrape_news,
    text_to_speech,
    comparative_analysis,
    generate_news_reel
)
from collections import Counter
import shutil

# Page config
st.set_page_config(
    page_title="News Summarizer & TTS",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Main Page Styling ---
st.markdown("""
<style>
.home-header {
    background: linear-gradient(90deg, #0f2027, #2c5364);
    color: white;
    padding: 2rem 0;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.feature-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 1.5rem;
    padding: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
    border-left: 6px solid #2c5364;
    cursor: pointer;
    color: #000;
}
.feature-card h3, .feature-card p, .feature-card li {
    color: #000;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 24px rgba(44,83,100,0.15);
    border-left: 6px solid #ffcc00;
}
.footer {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-size: 0.9rem;
}
</style>

<div class='home-header'>
    <h1>📰 News Summarizer & TTS</h1>
    <p style='font-size: 1.2em; margin-top: 1rem;'>
        Your AI-powered news assistant for summarization, analysis, and audio updates
    </p>
</div>
""", unsafe_allow_html=True)

# --- Main Features Section ---
st.markdown("### 🚀 Main Features")

# Feature Cards
col1, col2 = st.columns(2)

with col1:
    # News Search Card
    st.markdown("""
    <a href="News_Search" style="text-decoration: none;">
        <div class='feature-card'>
            <h3>📰 News Search & Analysis</h3>
            <p>Search for news by company or topic, analyze sentiment patterns, and get instant summaries with audio playback.</p>
            <ul>
                <li>Company & topic-based search</li>
                <li>Sentiment analysis</li>
                <li>Multi-language audio summaries</li>
            </ul>
        </div>
    </a>
    """, unsafe_allow_html=True)

    # Reels Navigation Button
    st.markdown("""
    <style>
    .reels-button {
        background: #fff;
        color: #000;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        border: 2px solid #2c5364;
    }
    .reels-button h3, .reels-button p {
        color: #000;
    }
    .reels-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 24px rgba(44,83,100,0.15);
    }
    </style>
    <a href="News_Reels" style="text-decoration: none;">
        <div class='reels-button'>
            <h3>🎬 Try News Reels</h3>
            <p style='margin: 0;'>Experience news in an Instagram-style format</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a href="News_Alerts" style="text-decoration: none;">
        <div class='feature-card'>
            <h3>🔔 News Alerts</h3>
            <p>Stay updated with personalized news alerts and notifications for topics that matter to you.</p>
            <ul>
                <li>Custom keyword alerts</li>
                <li>Real-time notifications</li>
                <li>Audio summaries of alerts</li>
            </ul>
        </div>
    </a>
    
    <div class='feature-card'>
        <h3>🌐 Supported Languages</h3>
        <p>Get news summaries in multiple languages with our text-to-speech feature.</p>
        <ul>
            <li>Hindi 🇮🇳</li>
            <li>English 🇬🇧</li>
            <li>Bengali 🇧🇩</li>
            <li>Spanish 🇪🇸</li>
            <li>Tamil 🇮🇳</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Quick Start Guide
st.markdown("### 🎯 Quick Start Guide")
st.markdown("""
1. 📰 **News Search**: Navigate to News Search & Analysis to search and analyze news
2. 🎬 **News Reels**: Click Try News Reels to experience Instagram-style news
3. 🔔 **News Alerts**: Select News Alerts to manage your custom alerts
""")

# Footer
st.markdown("""
<div class='footer'>
    <p>Built with ❤️ by <b>Ujjwal Sinha</b> • <a href='https://github.com/Ujjwal-sinha' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)

# Theme Configuration in Sidebar
st.sidebar.markdown("## 🎨 App Settings")
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #0D1117; color: #fff; }
        .feature-card { 
            background-color: #161B22; 
            color: #fff !important;
        }
        .feature-card h3, .feature-card p, .feature-card li { 
            color: #fff !important; 
        }
        .reels-button {
            background-color: #161B22 !important;
            color: #fff !important;
            border-color: #2c5364 !important;
        }
        .reels-button h3, .reels-button p {
            color: #fff !important;
        }
        .news-card, .reel-card {
            background-color: #161B22 !important;
            color: #fff !important;
        }
        .news-card h3, .news-card p, .news-card div,
        .reel-card h3, .reel-card p, .reel-card div {
            color: #fff !important;
        }
        </style>
    """, unsafe_allow_html=True)