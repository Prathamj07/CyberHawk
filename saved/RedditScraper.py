import praw
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from newspaper import Article
from bs4.element import Comment
import json

# Initialize the Reddit client
reddit = praw.Reddit(
    client_id="qxvPVMTHwLAr3Hn3aDKvKA",
    client_secret="naYXikPju-Kssuq8l2FnP1eqfDo-Ig",
    user_agent="CyberIncidentScraper by /u/Creepy-Ad-7640"
)

def is_visible_text(element):
    """
    Filter to check if an element contains visible text.
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def fetch_article_text_dynamic(article_url):
    """
    Fetch the main content of an article from its URL dynamically.
    """
    try:
        article = Article(article_url)
        article.download()
        article.parse()
        if article.text.strip():
            return article.text.strip()
    except Exception as e:
        print(f"newspaper3k failed: {e}. Falling back to BeautifulSoup...")

    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.find_all(string=True)  # Get all string nodes
        visible_texts = filter(is_visible_text, texts)
        article_content = "\n".join(text.strip() for text in visible_texts if text.strip())
        return article_content
    except requests.RequestException as e:
        print(f"Error fetching the URL {article_url}: {e}")
        return None

def is_url_valid(url):
    """
    Validate a URL by sending a HEAD request.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code // 100 == 2
    except requests.RequestException:
        return False

def fetch_top_posts_of_current_year(subreddit_name, search_query, limit=25, existing_data=None):
    """
    Fetches the top posts of the current year from a subreddit based on the search query.
    """
    data = [] if existing_data is None else existing_data
    current_year = datetime.now().year
    start_timestamp = datetime(current_year, 1, 1).timestamp()

    # Fetch the top posts of the year
    fetched_posts = reddit.subreddit(subreddit_name).search(search_query, sort="top", time_filter="year", limit=100)

    for post in fetched_posts:
        # Filter posts that are from the current year
        if post.created_utc < start_timestamp:
            continue

        clean_title = post.title.replace('\r', '').replace('\n', '').strip()

        # Domain-specific filter: Ensure the title contains at least one keyword
        keywords = [
            "cyber attack", "data breach", "cybersecurity", "hacking", "ransomware",
            "malware", "phishing", "denial of service", "DDoS", "cyber espionage", "cyber warfare"
        ]
        if not any(keyword.lower() in clean_title.lower() for keyword in keywords):
            continue  # Skip posts that don't match the required domain

        if any(post.url == item.get("url") for item in data):
            continue  # Skip duplicate posts

        post_date = datetime.fromtimestamp(post.created_utc, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        post_data = {
            "title": clean_title,
            "url": post.url,
            "time": post_date,
            "source": "reddit"
        }

        if is_url_valid(post.url):
            article_content = fetch_article_text_dynamic(post.url)
            post_data["content"] = article_content if article_content else "Failed to extract content from this URL"
        else:
            post_data["content"] = "URL is not valid or no longer accessible"

        data.insert(0, post_data)  # Add new data at the top

        if len(data) >= limit:
            break

    return data

def save_data_to_json(data, filename="reddit.json"):
    """
    Save the scraped data to a JSON file.
    """
    try:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data has been written to {filename}")
    except Exception as e:
        print(f"Failed to save data to JSON: {e}")

def load_data_from_json(filename="reddit.json"):
    """
    Load existing data from a JSON file, if available.
    """
    try:
        with open(filename, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}")
        return []

if __name__ == "__main__":
    # Load existing data
    existing_data = load_data_from_json()

    # Fetch the top posts of the current year from the "cybersecurity" subreddit
    subreddit_name = "India"
    search_query = "cyber attack, data breach, cybersecurity, hacking, ransomware, malware, phishing, denial of service, DDoS, cyber espionage, cyber warfare"
    posts_data = fetch_top_posts_of_current_year(subreddit_name, search_query, limit=10, existing_data=existing_data)

    # Save updated data
    save_data_to_json(posts_data)
