from fastapi import FastAPI
from utils import scrape_news, analyze_sentiment, text_to_speech, comparative_analysis, generate_final_output

app = FastAPI()

@app.get("/news/{company_name}")
def get_news(company_name: str):
    articles = scrape_news(company_name)
    for article in articles:
        article['sentiment'] = analyze_sentiment(article['summary'])
    
    comparative_analysis_result = comparative_analysis(articles)
    final_output = generate_final_output(company_name, articles, comparative_analysis_result)
    
    return final_output

@app.get("/tts/{text}")
def get_tts(text: str):
    audio_file = text_to_speech(text)
    return {"message": "TTS generated successfully", "audio_file": audio_file}