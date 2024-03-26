import requests
from bs4 import BeautifulSoup

def find_summary_and_content_classes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize dictionaries to store tag counts for classes and IDs
    class_counts = {}
    id_counts = {}
    
    # Find all tags in the HTML content
    all_tags = soup.find_all()
    
    # Iterate through all tags to count classes and IDs
    for tag in all_tags:
        # Count classes for each tag
        for class_name in tag.get('class', []):
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # Count IDs for each tag
        id_name = tag.get('id', '')
        if id_name:
            id_counts[id_name] = id_counts.get(id_name, 0) + 1
    
    # Determine the most common class and ID
    most_common_class = max(class_counts, key=class_counts.get)
    most_common_id = max(id_counts, key=id_counts.get)
    
    return most_common_class, most_common_id

def fetch_summary_and_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
        summary_class, content_class = find_summary_and_content_classes(html_content)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find summary based on the most common class identified
        summary = soup.find(class_=summary_class)
        if summary:
            summary_text = summary.get_text()
        else:
            summary_text = "Summary not found"
        
        # Find content based on the most common class identified
        content = soup.find(class_=content_class)
        if content:
            content_text = content.get_text()
        else:
            content_text = "Content not found"
        
        return summary_text, content_text
    else:
        return "Error fetching URL.", None

# Example usage
url = "https://pontospravoar.com/trs-estratgias-para-usar-nos-trs-meses-gratis-da-conta-santander-select/"
summary, content = fetch_summary_and_content(url)
print("Summary:", summary)
print("Content:", content)

