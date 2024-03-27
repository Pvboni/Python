import feedparser

def fetch_latest_news_rss(url):
    news_feed = feedparser.parse(url)
    latest_news = []
    if 'entries' in news_feed:
        for entry in news_feed.entries:
            title = entry.title.strip()
            link = entry.link
            summary = entry.get('summary', '')  # Obtendo o resumo do artigo
            latest_news.append({'title': title, 'link': link, 'summary': summary})
    return latest_news

if __name__ == "__main__":
    rss_url = "https://pontospravoar.com/feed/"
    latest_news = fetch_latest_news_rss(rss_url)

    for article in latest_news:
        print("Título:", article['title'])
        print("Link:", article['link'])
        print("Resumo:", article['summary'])
        print()
