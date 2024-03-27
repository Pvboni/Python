import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta
import time

# Define the API Key for Gemini
API_KEY = "AIzaSyANhQXJDd-PLX94-CqaVlprs8qG9_Slzq0"
genai.configure(api_key=API_KEY)

def fetch_latest_news_rss(url):
    two_days_ago = datetime.now() - timedelta(days=2)
    news_feed = feedparser.parse(url)
    latest_news = []
    if 'entries' in news_feed:
        for entry in news_feed.entries:
            entry_date = datetime(*entry.published_parsed[:6])
            # Verifica se a data da entrada é posterior a dois dias atrás
            if entry_date >= two_days_ago:
                title = entry.title.strip()
                link = entry.link
                content = entry.get('summary', '')  # Obtendo o conteúdo do artigo
                latest_news.append({'title': title, 'link': link, 'content': content})
    return latest_news

def categorize_articles_with_gemini_api(articles):
    categorized_articles = {}
    
    for article in articles:
        title = article['title']
        content = article['content']
        category = categorize_content_with_gemini_api(content)
        if category in categorized_articles:
            categorized_articles[category].append((title, article['link']))
        else:
            categorized_articles[category] = [(title, article['link'])]
    
    return categorized_articles

def categorize_content_with_gemini_api(content):
    # Initialize GenerativeModel
    model = genai.GenerativeModel('gemini-pro')
    
    # Define a prompt with the content of the article
    prompt = f"Classificar o texto:\n{content}\n\n"

    # Retry logic to handle potential errors
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            # Generate content
            response = model.generate_content(prompt)

            # Check if content classification was successful
            if response.candidates:
                # Extract the predicted category from the first candidate
                candidate_content = response.candidates[0].content
                
                # Attempt to extract text content from available attributes
                extracted_content = None
                if hasattr(candidate_content, 'parts'):
                    extracted_content = " ".join([part.text for part in candidate_content.parts])
                
                # Return the predicted category
                if extracted_content:
                    return extracted_content.lower().strip()
            
            # If classification fails, return 'outro'
            return 'outro'
        
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying...")
            retries += 1
            time.sleep(1)  # Wait for a second before retrying
    
    # Return 'outro' if classification fails after retries
    return 'outro'

if __name__ == "__main__":
    rss_url = "https://pontospravoar.com/feed/"
    latest_news = fetch_latest_news_rss(rss_url)
    categorized_articles = categorize_articles_with_gemini_api(latest_news)

    for category, articles in categorized_articles.items():
        print(f"{category.capitalize()}:")
        for article in articles:
            print(f"{article[0]} - {article[1]}")
        print()
