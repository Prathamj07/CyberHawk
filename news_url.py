import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to fetch Google News search results and extract URLs
# Function to fetch Google News search results and extract URLs
def fetch_google_news_urls(query, max_urls=250):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    search_url = f"https://www.google.com/search?q={query}&tbm=nws"
    urls = set()  # Use a set to avoid duplicates
    page = 0

    while len(urls) < max_urls:
        # Add pagination
        paginated_url = f"{search_url}&start={page * 10}"
        response = requests.get(paginated_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page + 1}. HTTP Status: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Log raw HTML for debugging (Optional)
        # print(response.text)

        # Look for news article links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith("/url?q="):
                url = href.split('/url?q=')[1].split('&')[0]
                if "google.com" not in url:  # Exclude Google internal links
                    urls.add(url)
                    if len(urls) >= max_urls:
                        break

        print(f"Fetched {len(urls)} URLs so far...")
        time.sleep(2)  # Sleep to avoid getting blocked
        page += 1

    return list(urls)


# Main function to execute scraping
def main():
    query = "cyber incident news in India \"Cyber Incident\" when:1y"
    max_urls = 250
    print(f"Fetching Google News URLs for query: '{query}'...")
    try:
        urls = fetch_google_news_urls(query, max_urls)
        
        # Save URLs to a CSV file
        df = pd.DataFrame(urls, columns=["News URLs"])
        output_file = "google_news_urls.csv"
        df.to_csv(output_file, index=False)
        print(f"Scraped {len(urls)} URLs. Saved to '{output_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
