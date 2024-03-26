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
                title = clean_text(entry.title.strip())  # Clean the news title
                link = entry.link
                published_date = entry.published_parsed
                today = datetime.date.today()  
                published_datetime = datetime.datetime(*published_date[:6])
                if published_datetime.date() == today:
                    summary = get_summary(link)
                    latest_news.append({'title': title, 'link': link, 'summary': summary})
    return latest_news

def clean_text(text):
    # Remove special characters using regular expressions
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
    return cleaned_text

def get_summary(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        summary = '\n'.join([paragraph.text.strip() for paragraph in paragraphs[:3]])
        return summary
    else:
        print(f"Error fetching summary from URL: {url}")
        return None

def generate_content_with_gemini_api(news_titles):
    # Initialize GenerativeModel
    model = genai.GenerativeModel('gemini-pro')

    # Generate content for each news title using Gemini API
    generated_content = []
    for title in news_titles:
        # Define the question using JSON
        question_json = {
            "question": title
        }

        # Convert the JSON to a string
        prompt = json.dumps(question_json)

        # Generate content
        response = model.generate_content(prompt)

        if response.status_code == 200:
            # Append the response text to the list of generated content
            generated_content.append(response.text)
        else:
            print(f"Error generating content for title: {title}")
            generated_content.append(None)

    return generated_content

if __name__ == "__main__":
    rss_urls = [
        "https://pontospravoar.com/feed/",
        "https://passageirodeprimeira.com/feed/"
    ]

    # Fetch latest news titles from RSS feeds
    latest_news = fetch_latest_news_rss(rss_urls)
    news_titles = [news['title'] for news in latest_news]

    # Generate content for news titles using Gemini API
    generated_content = generate_content_with_gemini_api(news_titles)

    # Print the generated content for each news title
    for title, content in zip(news_titles, generated_content):
        print(f"Title: {title}")
        if content:
            print(f"Generated Content: {content}\n")
        else:
            print("Failed to generate content.\n")
