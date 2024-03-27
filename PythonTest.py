import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta

# Define the API Key for Gemini
API_KEY = "AIzaSyANhQXJDd-PLX94-CqaVlprs8qG9_Slzq0"
genai.configure(api_key=API_KEY)

def fetch_latest_news_rss(url):
    news_feed = feedparser.parse(url)
    latest_news = []
    two_days_ago = datetime.now() - timedelta(days=2)  # Obtém a data de dois dias atrás
    if 'entries' in news_feed:
        for entry in news_feed.entries:
            # Converte a data da entrada para um objeto datetime
            entry_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            # Verifica se a entrada é dos últimos dois dias
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
            categorized_articles[category].append({'title': title, 'link': article['link']})
        else:
            categorized_articles[category] = [{'title': title, 'link': article['link']}]
    
    return categorized_articles

def categorize_content_with_gemini_api(content):
    # Initialize GenerativeModel
    model = genai.GenerativeModel('gemini-pro')
    
    # Define a prompt with the content of the article
    prompt = f"Classificar o texto:\n{content}\n\n"

    # Generate content
    response = model.generate_content(prompt)

    # Check if content classification was successful
    if response.candidates:
        # Extract the predicted category from the first candidate
        candidate_content = response.candidates[0].content
        
        # Attempt to extract text content from available attributes
        extracted_content = None
        if hasattr(candidate_content, 'text'):
            extracted_content = candidate_content.text
        elif hasattr(candidate_content, 'text_list'):
            extracted_content = " ".join(candidate_content.text_list)
        elif hasattr(candidate_content, 'parts'):
            extracted_content = " ".join([part.text for part in candidate_content.parts])
        
        # Return the predicted category
        if extracted_content:
            return extracted_content.lower().strip()
    
    # Return 'outro' if classification fails
    return 'outro'

if __name__ == "__main__":
    rss_url = "https://pontospravoar.com/feed/"
    latest_news = fetch_latest_news_rss(rss_url)
    categorized_articles = categorize_articles_with_gemini_api(latest_news)

    for category, articles in categorized_articles.items():
        print(f"{category.capitalize()}:")
        for article in articles:
            print(f"Titulo: {article['title']}, Link: {article['link']}")
        print()
