import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta
from collections import Counter
import time
import nltk
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('punkt')

# Define o API Key para o Gemini
API_KEY = "AIzaSyANhQXJDd-PLX94-CqaVlprs8qG9_Slzq0"
genai.configure(api_key=API_KEY)

def fetch_latest_news_rss(url):
    two_days_ago = datetime.now() - timedelta(days=2)
    news_feed = feedparser.parse(url)
    latest_news = []
    if 'entries' in news_feed:
        for entry in news_feed.entries:
            entry_date = datetime(*entry.published_parsed[:6])
            # Verifica se a data de entrada está dentro dos últimos dois dias
            if entry_date >= two_days_ago:
                title = entry.title.strip()
                link = entry.link
                content = entry.get('summary', '')  # Obtém o conteúdo do artigo
                latest_news.append({'title': title, 'link': link, 'content': content})
    return latest_news

def extract_keywords(content):
    # Tokenize o conteúdo
    tokens = word_tokenize(content.lower())
    # Extrai palavras-chave
    keywords = list(set(tokens))  # Remove duplicatas
    return keywords

def categorize_articles_with_gemini_api(articles):
    categorized_articles = {}
    categories_counter = Counter()
    
    # Itera através de cada artigo e os categoriza
    for article in articles:
        title = article['title']
        content = article['content']
        # Extract palavras-chave
        keywords = extract_keywords(content)
        category = categorize_content_with_gemini_api(content)
        categories_counter[category] += 1
        
        # Limita as categorias para as cinco principais
        if len(categories_counter) <= 5:
            if category in categorized_articles:
                categorized_articles[category].append((title, article['link'], keywords))
            else:
                categorized_articles[category] = [(title, article['link'], keywords)]
        else:
            # Agrupa os artigos restantes na categoria 'other'
            if 'other' in categorized_articles:
                categorized_articles['other'].append((title, article['link'], keywords))
            else:
                categorized_articles['other'] = [(title, article['link'], keywords)]
    
    return categorized_articles

def categorize_content_with_gemini_api(content):
    # Número de tentativas
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Inicializa o GenerativeModel
            model = genai.GenerativeModel('gemini-pro')
            
            # Define um prompt com o conteúdo do artigo
            prompt = f"Classify the text:\n{content}\n\n"

            # Gera o conteúdo
            response = model.generate_content(prompt)

            # Verifica se a classificação do conteúdo foi bem-sucedida
            if response.candidates:
                # Extrai a categoria prevista do primeiro candidato
                candidate_content = response.candidates[0].content
                
                # Tenta extrair o conteúdo de texto dos atributos disponíveis
                extracted_content = None
                if hasattr(candidate_content, 'parts'):
                    extracted_content = " ".join([part.text for part in candidate_content.parts])
                
                # Retorna a categoria prevista
                if extracted_content:
                    return extracted_content.lower().strip()
            
            # Se não houver resposta bem-sucedida, aguarde um tempo antes de tentar novamente
            time.sleep(5)  # Espera 5 segundos antes de tentar novamente

        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
            else:
                print("Maximum retries reached. Exiting...")
                return 'other'

    # Retorna 'other' se a classificação falhar
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
