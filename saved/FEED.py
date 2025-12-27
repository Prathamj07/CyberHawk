import requests
from bs4 import BeautifulSoup
import re
import json

def resolve_google_news_url(google_news_url):
    """
    Resolves the original URL from a Google News redirection link
    by following the redirection.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    try:
        # Allow redirection to automatically resolve the URL
        response = requests.get(google_news_url, headers=headers, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            return response.url  # Resolved original URL
        else:
            print(f"Failed to resolve URL. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error resolving URL: {e}")
        return None

def scrape_news(url):
    """
    Scrapes the news content from the resolved URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }

    # Resolve original URL if it's a Google News URL
    if "news.google.com" in url:
        print("Resolving original URL from Google News link...")
        url = resolve_google_news_url(url)
        if not url:
            print("Failed to resolve original URL.")
            return

    # Fetch and parse the webpage
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "No title found"

    # Extract date (searching for 'IST')
    text_with_ist = None
    for element in soup.find_all(text=re.compile(r'\bIST\b')):
        if element:
            text_with_ist = element.strip()
            break

    # Extract description
    paragraphs = []
    if title_tag:
        next_element = title_tag.find_next()
        while next_element and len(paragraphs) < 6:
            if next_element.name == 'p':
                paragraphs.append(next_element.get_text(strip=True))
            next_element = next_element.find_next()
    description = " ".join(paragraphs)

    # Display the extracted information
    print(f"\nTitle: {title}")
    print(f"Date: {text_with_ist if text_with_ist else 'No date found'}")
    print("\nDescription:")
    print(description if description else "No description found")

def scrape_news_from_json(filename):
    """
    Reads a JSON file containing news URLs and scrapes content for each.
    """
    with open(filename, 'r') as file:
        news_urls = json.load(file)

    for idx, (key, url) in enumerate(news_urls.items(), start=1):
        print(f"\n[{idx}] Scraping URL: {url}")
        scrape_news(url)

# Main Program
if __name__ == "__main__":
    # Provide the JSON file with URLs
    filename = "news_urls.json"
    scrape_news_from_json(filename)
