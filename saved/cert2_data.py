import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# Define the main URL
MAIN_URL = "https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVA01&VACODE=CIVA-2023-2137"

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": MAIN_URL,
}

# Function to fetch a URL with retries
def fetch_url_with_retries(url, headers=None, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise

# Function to update the JSON file with new data
def update_json_file(file_path, new_data):
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        if isinstance(existing_data, list):
            existing_data.append(new_data)
        else:
            existing_data = [existing_data, new_data]
        # Remove redundancy
        unique_data = [dict(t) for t in {tuple(d.items()) for d in existing_data}]
    except (FileNotFoundError, json.JSONDecodeError):
        unique_data = [new_data]

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(unique_data, json_file, indent=4)

# Step 1: Fetch the main page
response = fetch_url_with_retries(MAIN_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Scrape relevant sections from the main page
alert_title = soup.find('span', {'class': 'marker'}).get_text(strip=True) if soup.find('span', {'class': 'marker'}) else "Unknown"
issue_date = soup.find('p', {'class': 'red'}).get_text(strip=True) if soup.find('p', {'class': 'red'}) else "Unknown"

# Find the content in the "contentTD" section
title_text = soup.find('span', {'class': 'contentTD'}).get_text(strip=True) if soup.find('span', {'class': 'contentTD'}) else "Unknown"

# Step 3: Locate the "Indicators of Compromise" and scrape <br> tags data until next <span>
ioc_section = soup.find('b', string=lambda text: "Indicators of Compromise:" in text if text else False)

pdf_text = "No PDF found"
if ioc_section:
    # After finding the <b> section, find all <br> tags until the next <span>
    ioc_text = []
    next_sibling = ioc_section.find_next_sibling()
    while next_sibling:
        if next_sibling.name == 'span':
            break  # Stop when another <span> is encountered
        if next_sibling.name == 'br':
            previous_sibling = next_sibling.previous_sibling
            if previous_sibling and isinstance(previous_sibling, str):
                ioc_text.append(previous_sibling.strip())
        next_sibling = next_sibling.find_next_sibling()

    pdf_text = '\n'.join(ioc_text)

# Step 4: Organize data into JSON
scraped_data = {
    "Alert Title": alert_title,
    "Issue Date": issue_date,
    "Title Text": title_text,
    "Indicators of Compromise": pdf_text,  # This will now contain the scraped data
    "URL": MAIN_URL
}

# Step 5: Update the JSON file
output_file = "scraped_data_with_indicators.json"
update_json_file(output_file, scraped_data)

print(f"Data with Indicators of Compromise saved to {output_file}")
