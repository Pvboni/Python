import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta

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
    # Placeholder para a extração de conteúdo relevante
    extracted_content = content

    # Placeholder para a extração de entidades e relações
    entities = extract_entities(extracted_content)
    relations = extract_relations(extracted_content)
    
    # Placeholder para o cálculo da probabilidade por categoria
    category_probabilities = {'programa_de_pontos': 0.3, 'promocao_de_passagens_aereas': 0.6, 'outro': 0.1}

    # Retorno da categoria com maior probabilidade
    return max(category_probabilities.items(), key=lambda x: x[1])[0]

def extract_entities(content):
    # Função de extração de entidades
    # Placeholder para implementação real
    return []

def extract_relations(content):
    # Função de extração de relações
    # Placeholder para implementação real
    return []

if __name__ == "__main__":
    rss_url = "https://pontospravoar.com/feed/"
    latest_news = fetch_latest_news_rss(rss_url)
    categorized_articles = categorize_articles_with_gemini_api(latest_news)

    for category, articles in categorized_articles.items():
        print(f"{category.capitalize()}:")
        for article in articles:
            print(f"{article[0]} - {article[1]}")
        print()
