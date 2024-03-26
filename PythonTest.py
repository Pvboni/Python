import feedparser
import requests
import json
import datetime
from bs4 import BeautifulSoup
import re
import google.generativeai as genai

# Define the API Key for Gemini
API_KEY = "AIzaSyANhQXJDd-PLX94-CqaVlprs8qG9_Slzq0"
genai.configure(api_key=API_KEY)

def fetch_latest_news_rss(urls):
    latest_news = []
    for url in urls:
        news_feed = feedparser.parse(url)
        if 'entries' in news_feed:
            for entry in news_feed.entries:
                title = clean_text(entry.title.strip())
                link = entry.link
                published_date = entry.published_parsed
                today = datetime.date.today()  
                published_datetime = datetime.datetime(*published_date[:6])
                if published_datetime.date() == today:
                    summary = get_summary(link)
                    latest_news.append({'title': title, 'link': link, 'summary': summary})
    return latest_news

def clean_text(text):
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
    return cleaned_text

def get_summary(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            summary = '\n'.join([paragraph.text.strip() for paragraph in paragraphs[:3]])
            return summary
        else:
            print(f"Error fetching summary from URL: {url}")
            return "Summary unavailable"
    except Exception as e:
        print(f"Error fetching summary from URL: {url}\n{e}")
        return "Summary unavailable"

def generate_content_with_gemini_api(news_titles):
    # Initialize GenerativeModel
    model = genai.GenerativeModel('gemini-pro')
    generated_content = []

    for news in news_titles:
        # Define the question using JSON
        question_json = {
            "question": news['title']
        }

        # Convert the JSON to a string
        prompt = json.dumps(question_json)

        # Generate content
        response = model.generate_content(prompt)

        # Check if content generation was successful
        if response.candidates:
            # Extract content from the first candidate
            candidate_content = response.candidates[0].content
            extracted_content = None
            
            # Attempt to extract text content from available attributes
            if hasattr(candidate_content, 'text'):
                extracted_content = candidate_content.text
            elif hasattr(candidate_content, 'title'):
                extracted_content = candidate_content.title
            elif hasattr(candidate_content, 'summary'):
                extracted_content = candidate_content.summary

            # Append extracted content or a placeholder message
            if extracted_content:
                generated_content.append(extracted_content)
            else:
                generated_content.append("Content extraction failed")
        else:
            print(f"Error generating content for title: {news['title']}. No candidates found.")
            generated_content.append("Content generation failed")

    return generated_content


if __name__ == "__main__":
    rss_urls = [
        "https://pontospravoar.com/feed/",
        "https://passageirodeprimeira.com/feed/"
    ]

    latest_news = fetch_latest_news_rss(rss_urls)
    generated_content = generate_content_with_gemini_api(latest_news)

    for news, content in zip(latest_news, generated_content):
        print(f"Title: {news['title']}")
        print(f"Summary: {news['summary']}")
        print(f"Generated content: {content}\n")
