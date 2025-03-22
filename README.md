# News Summarization and Text-to-Speech Application

## Overview

This project is a News Summarization and Text-to-Speech (TTS) application that allows users to fetch the latest news articles for a specific company, analyze the sentiment of the articles, and generate an audio summary in Hindi. The application is built using **FastAPI** for the backend and **Streamlit** for the frontend. It leverages web scraping, natural language processing (NLP), and text-to-speech technologies to provide a comprehensive news analysis tool.

## Features

- 🔍**News Scraping**: Fetches the latest news articles for a given company from Bing News.
- 📈**Sentiment Analysis**: Analyzes the sentiment of each news article using a pre-trained NLP model.
- 📈**Comparative Analysis**: Provides a comparative analysis of the sentiment distribution and topic overlap across articles.
- 🗣️**Text-to-Speech**: Converts the summarized news text into an audio file in Hindi And English.
- ✨**Interactive UI**: A user-friendly Streamlit interface for easy interaction with the application.
- 🔁 **Audio Controls** (Play, Download, Clear)
- 🌗 **Light/Dark Mode Toggle**
- 🧠 **Company Logo Fetching** using Clearbit API
- 📊 **Pie & Bar Charts** for sentiment visualization using Plotly
- 📄 **Structured JSON Output** for summarized data

## Technologies Used

- **Python**: The core programming language used for the project.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Streamlit**: An open-source app framework used to create the web interface.
- **BeautifulSoup**: A Python library used for web scraping tasks. *(no JavaScript)*
- **Transformers**: A library by Hugging Face used for sentiment analysis using pre-trained NLP models.
- **gTTS (Google Text-to-Speech)**: A Python library used to convert text to speech.
- **Pandas**: Used for data manipulation and analysis.
- **NLTK**: A natural language processing library used for text processing.
- **Plotly**: Interactive sentiment charts .
- **Clearbit API**:Logo fetching by domain.
- **googletrans**: Python library for translating text using Google Translate unofficial API.

- **Selenium**: Used for web scraping in more complex scenarios (not heavily used in this project).


## Installation

1. **Clone the repository**:
   ```bash  
   git clone https://github.com/Ujjwal-sinha/News-Summarization-and-Text-to-Speech-Application.git
   cd News-Summarization-and-Text-to-Speech-Application
   ```

2. **Set up a virtual environment**:
   ```bash
  conda create -p venv python==3.12
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI backend**:
   ```bash
   uvicorn api:app --reload
   ```

5. **Run the Streamlit frontend**:
   ```bash
   streamlit run app.py
   ```

6. **Access the application**:
   - The FastAPI backend will be available at `http://127.0.0.1:8000`.
   - The Streamlit frontend will be available at `http://localhost:8501`.

## Usage

1. **Fetch News Articles**:
   - Enter the name of the company in the input field (e.g., "Google" or "Tesla").
   - Click the "Fetch News" button to retrieve the latest news articles.

2. **View Analysis Results**:
   - The application will display the sentiment analysis, comparative analysis, and a summary of the articles.
   - The results are presented in a structured JSON format.

3. **Listen to the Audio Summary**:
   - The application generates an audio summary of the news articles in Hindi.
   - You can play the audio directly in the browser or download it.

4. **Clear Audio**:
   - Use the "Clear Audio" button to remove the generated audio file.

## API Endpoints

- **GET `/news/{company_name}`**:
  - Fetches news articles for the specified company and returns the analysis results.
  - Example: `http://127.0.0.1:8000/news/Google`

- **GET `/tts/{text}`**:
  - Converts the provided text into an audio file (Hindi by default).
  - Example: `http://127.0.0.1:8000/tts/Hello%20World`

## Project Structure

- **`api.py`**: Contains the FastAPI backend code with endpoints for fetching news and generating TTS.
- **`app.py`**: Contains the Streamlit frontend code for the user interface.
- **`utils.py`**: Contains utility functions for web scraping, sentiment analysis, TTS, and comparative analysis.
- **`requirements.txt`**: Lists all the Python dependencies required for the project.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Hugging Face** for the pre-trained sentiment analysis model.
- **Google** for the gTTS library.
- **Streamlit** for the easy-to-use web framework.

## Author

- **Ujjwal Sinha**
- Built with ❤️ for the community.

---

Feel free to explore the code, raise issues, or contribute to the project!