import requests
from bs4 import BeautifulSoup
import json
import os

# Define the search query and Google News search URL
query = "cyber attack news in India latest 'cyber attack' when:1d"
url = f"https://news.google.com/search?q={query.replace(' ', '%20')}&hl=en-IN&gl=IN&ceid=IN:en"

# Set headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

# Send the GET request
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all <a> tags with class 'WwrzSb' or 'JtKRv'
    links = soup.find_all("a", class_=["WwrzSb", "JtKRv"])

    new_urls = []
    for link in links:
        href = link.get("href")
        if href and href.startswith("./"):
            full_url = "https://news.google.com" + href[1:]
            if full_url not in new_urls:  
                new_urls.append(full_url)

    file_name = "200.json"
    if os.path.exists(file_name):
        with open(file_name, "r") as json_file:
            existing_urls = json.load(json_file)
    else:
        existing_urls = {}

    existing_urls_set = {url for url in existing_urls.values()}

    filtered_new_urls = [url for url in new_urls if url not in existing_urls_set]

    updated_urls_list = filtered_new_urls + list(existing_urls.values())

    updated_urls = {f"url{i + 1}": url for i, url in enumerate(updated_urls_list)}

    with open(file_name, "w") as json_file:
        json.dump(updated_urls, json_file, indent=4)

    print("News URLs have been updated in '200.json'.")

else:
    
    print(f"Failed to fetch the search results. Status code: {response.status_code}")