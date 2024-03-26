import requests
from bs4 import BeautifulSoup

def get_summary_and_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
    except requests.exceptions.RequestException as e:
        return "Error fetching URL: " + str(e), None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debugging output to print the parsed HTML
        print("Parsed HTML:")
        print(soup.prettify())
        
        # Adjust parsing strategy to target specific elements or classes
        summary_element = soup.find('div', class_='post-summary')  # Example class for summary
        content_element = soup.find('div', class_='post-content')  # Example class for content
        
        # Check if summary and content elements are found
        if summary_element and content_element:
            summary = summary_element.get_text().strip()
            content = content_element.get_text().strip()
            return summary, content
        else:
            return "Summary or content not found on the page.", None
    
    else:
        return "Unexpected status code: " + str(response.status_code), None

# Test the function with a sample URL
url = "https://pontospravoar.com/trs-estratgias-para-usar-nos-trs-meses-gratis-da-conta-santander-select/"
summary, content = get_summary_and_content(url)
print("Summary:", summary)
print("Content:", content)
