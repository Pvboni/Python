import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def fetch_latest_news_rss(url):
    news_feed = feedparser.parse(url)
    latest_news = []
    if 'entries' in news_feed:
        for entry in news_feed.entries:
            title = entry.title.strip()
            link = entry.link
            latest_news.append({'title': title, 'link': link})
    return latest_news

def create_email_body(news):
    body = "Latest news:\n\n"
    for article in news:
        body += f"{article['title']}\n{article['link']}\n\n"
    return body

def send_email(sender_email, receiver_email, subject, body):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    # Usar a senha fornecida anteriormente
    server.login(sender_email, 'imji vpva npah mwyd')

    server.sendmail(sender_email, receiver_email, message.as_string())

    server.quit()

def check_for_radar_ppv(news):
    for article in news:
        if article['title'].startswith("Radar PPV"):
            return True
    return False

if __name__ == "__main__":
    rss_url = "https://pontospravoar.com/feed/"
    sender_email = 'pvboni@gmail.com'
    receiver_email = 'pvboni@gmail.com'
    latest_news = fetch_latest_news_rss(rss_url)
    print("Latest news:", latest_news)  # Verificar se os dados foram obtidos corretamente
    email_subject = "News: Pontos para voar"  # Título do e-mail
    email_body = create_email_body(latest_news)
    print("Email body:", email_body)  # Verificar o corpo do e-mail
    
    if check_for_radar_ppv(latest_news):
        email_subject += " - Radar PPV"
    
    if len(latest_news) > 10:
        email_body = create_email_body(latest_news)
    
    send_email(sender_email, receiver_email, email_subject, email_body)
