import requests
from bs4 import BeautifulSoup
import json

def fetch_news_urls():
    # Define the search query and Google News URL
    query = "Latest Cyber Security news in India"
    url = f"https://news.google.com/search?q={query.replace(' ', '%20')}&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }

    # Send a GET request to Google News
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the news URLs. Status code: {response.status_code}")
        return {}

    # Parse the response content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract news article links
    news_urls = {}
    links = soup.find_all("a", class_=["WwrzSb", "JtKRv"])
    for index, link in enumerate(links[:40]):  # Limit to 40 articles
        href = link.get("href")
        if href and href.startswith("./"):
            # Construct full Google News URL
            google_news_url = "https://news.google.com" + href[1:]
            original_url = resolve_original_url(google_news_url)
            news_urls[f"article_{index + 1}"] = original_url if original_url else google_news_url

    return news_urls

def resolve_original_url(google_news_url):
    # Resolve the original article URL from the Google News redirection link
    try:
        # Follow redirects
        response = requests.get(google_news_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }, allow_redirects=True)
        if response.status_code == 200:
            return response.url  # Return the final resolved URL
        else:
            print(f"Failed to resolve URL {google_news_url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error resolving URL {google_news_url}: {e}")
        return None

def save_urls_to_file(news_urls, filename="news_urls.json"):
    # Save the extracted URLs to a JSON file
    with open(filename, "w") as file:
        json.dump(news_urls, file, indent=4)
    print(f"News URLs saved to {filename}")

def main():
    print("Fetching news URLs...\n")
    news_urls = fetch_news_urls()

    if not news_urls:
        print("No news URLs found.")
        return

    save_urls_to_file(news_urls)

if __name__ == "__main__":
    main()
