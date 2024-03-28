import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta
from collections import Counter
import time
import nltk
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('punkt')

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
            # Check if the entry date is within the last two days
            if entry_date >= two_days_ago:
                title = entry.title.strip()
                link = entry.link
                content = entry.get('summary', '')  # Obtain the content of the article
                latest_news.append({'title': title, 'link': link, 'content': content})
    return latest_news

def extract_keywords(content):
    # Tokenize the content
    tokens = word_tokenize(content.lower())
    # Define travel-related keywords
    travel_keywords = ["flight", "destination", "hotel", "travel", "tour", "trip"]
    # Extract keywords related to travel
    travel_related_tokens = [token for token in tokens if token in travel_keywords]
    return travel_related_tokens

def categorize_articles_with_gemini_api(articles):
    categorized_articles = {}
    categories_counter = Counter()
    
    # Iterate through each article and categorize them
    for article in articles:
        title = article['title']
        content = article['content']
        # Extract keywords
        keywords = extract_keywords(content)
        category = categorize_content_with_gemini_api(content)
        categories_counter[category] += 1
        
        # Limit categories to top 5
        if len(categories_counter) <= 5:
            if category in categorized_articles:
                categorized_articles[category].append((title, article['link'], keywords))
            else:
                categorized_articles[category] = [(title, article['link'], keywords)]
        else:
            # Group remaining articles under 'other' category
            if 'other' in categorized_articles:
                categorized_articles['other'].append((title, article['link'], keywords))
            else:
                categorized_articles['other'] = [(title, article['link'], keywords)]
    
    return categorized_articles

def categorize_content_with_gemini_api(content):
    # Number of retries
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Initialize GenerativeModel
            model = genai.GenerativeModel('gemini-pro')
            
            # Define a prompt with the content of the article
            prompt = f"Classify the text:\n{content}\n\n"

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
            
            # If no successful response, wait for some time before retrying
            time.sleep(5)  # Wait for 5 seconds before retrying

        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
            else:
                print("Maximum retries reached. Exiting...")
                return 'other'

    # Return 'other' if classification fails
    return 'other'

if __name__ == "__main__":
    rss_url = "https://pontospravoar.com/feed/"
    latest_news = fetch_latest_news_rss(rss_url)
    categorized_articles = categorize_articles_with_gemini_api(latest_news)

    for category, articles in categorized_articles.items():
        print(f"{category.capitalize()}:")
        for article in articles:
            keywords = ', '.join(article[2])
            print(f"{article[0]} - {article[1]} - Keywords: {keywords}")
        print()
