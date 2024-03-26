import feedparser
import requests
import json
import datetime
from bs4 import BeautifulSoup, SoupStrainer
import re
import time
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

def get_summary_with_strainer(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Define a strainer to find all <p> tags within a specific class (e.g., "summary")
            summary_strainer = SoupStrainer("p", class_="summary")
            soup = BeautifulSoup(response.content, 'html.parser', parse_only=summary_strainer)
            summary_paragraphs = soup.find_all('p')
            if summary_paragraphs:
                summary = '\n'.join([p.text.strip() for p in summary_paragraphs])
                return summary
            else:
                print(f"Summary element not found for URL: {url}")
        else:
            print(f"Error fetching summary from URL: {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request error fetching summary from URL: {url}\n{e}")
    except Exception as e:
        print(f"Error fetching summary from URL: {url}\n{e}")
    return "Summary unavailable"


def get_content_with_regex(url, content_regex):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator='\n')  # Combine text from all elements
            match = re.search(content_regex, text)
            if match:
                content = match.group(1)  # Assuming the first capturing group holds the content
                return content
            else:
                print(f"Content not found matching regex for URL: {url}")
        else:
            print(f"Error fetching content from URL: {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request error fetching content from URL: {url}\n{e}")
    except Exception as e:
        print(f"Error fetching content from URL: {url}\n{e}")
    return "Content unavailable"


def generate_content_with_gemini_api(news_titles):
    # Initialize GenerativeModel
    model = genai.GenerativeModel('gemini-pro')
    generated_content = []

    for news in news_titles:
        # Define the question using JSON with context
        question_json = {
            "question": news['title'],
            "categories": ["News"],
            "keywords": extract_keywords(news['title']),
            "sentence": "Here's the latest news:"
        }

        # Convert the JSON to a string
        prompt = json.dumps(question_json)

        # Generate content
        response = model.generate_content(prompt)
        
        # Debug print to inspect response
        print("Response:", response)

        # Check if content generation was successful
        if response.candidates:
            # Extract content from the first candidate
            candidate_content = response.candidates[0].content
            
            # Attempt to extract text content from available attributes
            extracted_content = None
            if hasattr(candidate_content, 'text'):
                extracted_content = candidate_content.text
            elif hasattr(candidate_content, 'text_list'):
                extracted_content = " ".join(candidate_content.text_list)
            elif hasattr(candidate_content, 'parts'):
                extracted_content = " ".join([part.text for part in candidate_content.parts])

            # Log the type of extracted content
            print(f"Extracted content type: {type(extracted_content)}")

            # Append extracted content or a placeholder message
            if extracted_content:
                generated_content.append(extracted_content)
            else:
                generated_content.append("Content extraction failed")
        else:
            print(f"Error generating content for title: {news['title']}. No candidates found.")
            generated_content.append("Content generation failed")

    return generated_content

def extract_keywords(text):
    # Placeholder function to extract keywords from the news title
    # You can implement more sophisticated keyword extraction methods here
    return re.findall(r'\b\w{5,}\b', text)

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
