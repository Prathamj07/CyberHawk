import json
import requests

API_KEY = "AIzaSyDPBwkW4DNQBHmpP9GSbhpeAow5O2INGpI"  # Replace with your Gemini API Key
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Load the JSON file
file_path = "D:/Study/SIH 2024/CyberCrew/trials/saved/filtered.json"  # Replace with the path to your JSON file
output_file_path = "filtered_cybersecurity_news.json"

with open(file_path, "r") as file:
    news_data = json.load(file)

validated_news = []

for news_item in news_data:
    source = news_item.get("source", "").lower()  
    summary = news_item.get("summary", "")  

    # Directly include news from Google
    if source == "google":
        validated_news.append(news_item)
        print(f"News from Google included directly: {news_item['title']}")
    else:
        # Only create the payload for non-Google news
        payload = {"prompt": summary}

        try:
            # Send the summary to the Gemini API for evaluation
            response = requests.post(API_ENDPOINT, headers=HEADERS, json=payload)

            if response.status_code == 200:
                result = response.json()
                # Ensure the 'suitable' key exists in the response
                is_suitable = result.get("suitable", "").lower() == "yes"

                if is_suitable:
                    validated_news.append(news_item)
                    print(f"News validated and included: {news_item['title']}")
                else:
                    print(f"News removed (unsuitable): {news_item['title']}")
            elif response.status_code == 401:
                print(f"Unauthorized access - Invalid API Key for: {news_item['title']}")
            else:
                print(f"API request failed with status {response.status_code} for: {news_item['title']}")
        except Exception as e:
            print(f"Error occurred while processing '{news_item['title']}': {e}")

# Save validated news to a new JSON file
with open(output_file_path, "w") as file:
    json.dump(validated_news, file, indent=4)

print(f"Filtered cybersecurity news has been saved to '{output_file_path}'.")
