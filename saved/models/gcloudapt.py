# gcloudapt.py
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from collections import Counter
import time
import sys

# Known APT groups
known_apt_groups = {
    "APT28": "Fancy Bear", "APT29": "Cozy Bear", "APT31": "Zirconium", "APT32": "Ocean Buffalo",
    # Add more groups as needed
}

def find_apt_articles(domain, sector):
    query = f"{domain} {sector} APT site:news.google.com OR site:techcrunch.com OR site:securityaffairs.co"
    apt_names_list = []

    # Perform Google search
    try:
        urls = list(search(query, stop=5))  # Fetch top 5 results
    except Exception as e:
        return []

    # Scrape each URL
    for url in urls:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()

            # Extract APT names
            apt_names = [word.upper() for word in text.split() if word.startswith("apt") and len(word) > 3]
            apt_names_list.extend(apt_names)

            time.sleep(1)  # Avoid rate-limiting
        except Exception as e:
            continue

    # Count occurrences
    apt_counter = Counter(apt_names_list)
    filtered_apt_names = {apt: count for apt, count in apt_counter.items() if apt in known_apt_groups}

    # Return top 3 APTs
    return Counter(filtered_apt_names).most_common(3)

# Main execution from command line
if __name__ == "__main__":
    # Read domain and sector from the command line
    domain = sys.argv[1]
    sector = sys.argv[2]

    # Run the function to find APTs
    results = find_apt_articles(domain, sector)
    
    # Output the results
    print(results)
