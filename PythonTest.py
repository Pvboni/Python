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
    categories_count = 0  # Contador para limitar a cinco categorias
    
    for article in articles:
        title = article['title']
        content = article['content']
        category = categorize_content_with_gemini_api(content)
        if category in categorized_articles:
            categorized_articles[category].append((title, article['link']))
        else:
            categorized_articles[category] = [(title, article['link'])]
            categories_count += 1
        if categories_count >= 5:
            break  # Limita a cinco categorias
    
    return categorized_articles

def categorize_content_with_gemini_api(content):
    # Inicializa o GenerativeModel
    model = genai.GenerativeModel('gemini-pro')
    
    # Define uma expressão na prompt para indicar a classificação desejada
    prompt = f"Classificar o texto e agrupar por categoria:\n{content}\n\n"
    
    # Gera o conteúdo
    response = model.generate_content(prompt)

    # Verifica se a classificação do conteúdo foi bem-sucedida
    if response.candidates:
        # Extrai a categoria prevista do primeiro candidato
        predicted_category = response.candidates[0].content.text
        return predicted_category.lower().strip()
    
    # Retorna 'outro' se a classificação falhar
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
