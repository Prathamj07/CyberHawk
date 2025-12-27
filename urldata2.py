import json
from googlenewsdecoder import new_decoderv1
import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
def standardize_date(date_string):
    """
    Standardize the date string to a single format.
    Input formats can be diverse (e.g., "Nov 29, 2024 10:27 PM IST").
    Output format will be "YYYY-MM-DD HH:mm:ss".
    """
    # Try parsing with known formats
    formats = [
        "%b %d, %Y %I:%M %p IST",  # Format: Nov 29, 2024 10:27 PM IST
        "%b %d, %Y %H:%M IST",     # Format: Nov 29, 2024 08:00 IST
        "%B %d, %Y %H:%M IST"      # Format: November 27, 2024 07:29 IST
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    # If no format matches, return as-is (or handle the error as needed)
    print(f"Could not parse date: {date_string}")
    return date_string

from bs4 import BeautifulSoup
import re
from datetime import datetime
import requests

def scrape_news(url):
    """
    Scrape the news details from a given URL.
    Returns a dictionary with title, content, standardized time, and URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }

    # Send a GET request
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"

    # Extract text containing "IST"
    text_with_ist = None
    for element in soup.find_all(text=re.compile(r'\bIST\b')):
        if element:
            text_with_ist = element.strip()
            break

    # Extract and standardize time
    standardized_time = text_with_ist  # Default to the original text if conversion fails
    if text_with_ist:
        date_match = re.search(r'\b(\w+ \d{1,2}, \d{4}, \d{1,2}:\d{2} [AP]M IST)\b', text_with_ist)
        if date_match:
            date_str = date_match.group(1)
            try:
                # Convert to 'YYYY-MM-DD HH:mm:ss'
                date_obj = datetime.strptime(date_str, '%b %d, %Y, %I:%M %p IST')
                standardized_time = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

    # Extract description
    description = ""
    paragraphs = soup.find_all('p')
    if paragraphs:
        description = "\n".join([p.get_text(strip=True) for p in paragraphs[:6]])

    # Return the extracted information
    return {
        "title": title,
        "content": description if description else "No description found",
        "time": standardized_time,
        "url": url
    }


def save_to_json(file_path, data):
    """
    Save extracted data to a JSON file. Appends to existing file if present and avoids duplicates.
    """
    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Avoid duplicates by checking URL
    existing_urls = {item["url"] for item in existing_data}
    new_data = [item for item in data if item["url"] not in existing_urls]

    # Append new data
    existing_data.extend(new_data)

    # Save back to the file
    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)

def main():
    # Load the JSON file containing the URLs
    json_file = "news_urls.json"
    output_file = "news_data.json"
    collected_data = []

    try:
        with open(json_file, "r") as file:
            urls_dict = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    interval_time = 1  # Set a longer interval time to ensure proper decoding

    # Process each URL in the dictionary
    for key, url in urls_dict.items():
        print(f"Decoding {key}: {url}")
        attempt = 0
        success = False

        # Retry up to 3 times if decoding fails
        while attempt < 3 and not success:
            try:
                decoded_url = new_decoderv1(url, interval=interval_time)
                if decoded_url.get("status"):
                    decoded_url = decoded_url['decoded_url']  # Get the decoded URL
                    print(f"Decoded URL for {key}: {decoded_url}")
                    
                    # Scrape the news details and save them
                    news_data = scrape_news(decoded_url)
                    if news_data:
                        collected_data.append(news_data)
                        print(f"Collected news data for {key}")
                    success = True  # Mark as successful if decoded
                else:
                    print(f"Error for {key}: {decoded_url['message']}")
                    attempt += 1  # Increment retry count
            except Exception as e:
                print(f"Error occurred while decoding {key}: {e}")
                save_to_json(output_file, collected_data)  # Save data before exiting
                return

            # Wait before retrying
            if not success:
                print(f"Retrying {key} in {interval_time} seconds...")
                time.sleep(interval_time)

    # Save the final collected data
    save_to_json(output_file, collected_data)
    print(f"All news data saved to {output_file}.")

if __name__ == "__main__":
    main()
