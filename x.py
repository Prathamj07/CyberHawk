import os
import sys
import pandas as pd
import json
from datetime import datetime
from fake_headers import Headers
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class Tweet:
    def __init__(self, card):
        self.error = False
        try:
            self.username = card.find_element("xpath", './/div[@data-testid="User-Name"]//span').text
            self.tweet_url = card.find_element("xpath", ".//a[contains(@href, '/status/')]").get_attribute("href")
            self.tweet_time = card.find_element("xpath", ".//time").get_attribute("datetime")
            self.content = " ".join(
                [content.text for content in card.find_elements("xpath", '(.//div[@data-testid="tweetText"])[1]//span')]
            )
        except NoSuchElementException:
            self.error = True

        self.tweet = {"username": self.username, "url": self.tweet_url, "time": self.tweet_time, "content": self.content}

class TwitterScraper:
    TWITTER_LOGIN_URL = "https://twitter.com/i/flow/login"

    def __init__(self, username, password, max_tweets=50):
        self.username = username
        self.password = password
        self.max_tweets = max_tweets
        self.data = []
        self.driver = self._get_driver()

    def _get_driver(self):
        print("Setting up WebDriver...")
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")

        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            print("WebDriver is ready.")
            return driver
        except WebDriverException as e:
            print(f"Error setting up WebDriver: {e}")
            sys.exit(1)

    def login(self):
        print("Logging in...")
        self.driver.get(self.TWITTER_LOGIN_URL)
        sleep(5)
        
        try:
            username_field = self.driver.find_element("xpath", '//input[@name="text"]')
            username_field.send_keys(self.username)
            username_field.send_keys(Keys.RETURN)
            sleep(3)

            password_field = self.driver.find_element("xpath", '//input[@name="password"]')
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            sleep(5)
            print("Login successful.")
        except NoSuchElementException as e:
            print(f"Login failed: Could not locate an element. Details: {e}")
            self.driver.quit()
            sys.exit(1)

    def search_tweets(self, query):
        # Modify URL to fetch top tweets instead of latest
        url = f"https://twitter.com/search?q={query}&src=typed_query"  # Remove `&f=live` for "Top"
        self.driver.get(url)
        sleep(5)  # Increase wait time to ensure the page has fully loaded

        tweet_ids = set()
        scroll_attempts = 0
        while len(self.data) < self.max_tweets and scroll_attempts < 10:  # Increase scroll attempts to 10
            cards = self.driver.find_elements("xpath", '//article[@data-testid="tweet"]')
            
            if not cards:
                print("No more tweets found.")
                break  # If no tweets are found, stop scrolling.

            for card in cards:
                tweet = Tweet(card)
                if not tweet.error and tweet.tweet["url"] not in tweet_ids:
                    tweet_ids.add(tweet.tweet["url"])
                    self.data.append(tweet.tweet)
                    if len(self.data) >= self.max_tweets:
                        break

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)  # Increased wait time between scrolls to ensure page load
            scroll_attempts += 1

        if len(self.data) >= self.max_tweets:
            print("Scraping complete.")
        else:
            print("Scraping incomplete. Reached maximum scroll attempts.")

    def save_to_file(self, filename="X.json"):
        """
        Save scraped tweets to a file. Updates the same file on each run and avoids duplicates.
        The 'username' field is replaced with 'title', which contains:
            "title": "username: first 15 words of content"
        A new field 'source' is added with the value 'twitter'.
        """
        now = datetime.now()
        folder_path = "./tweets/"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = f"{folder_path}{filename}"

        # Load existing data if the file exists
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    print("Existing JSON file is empty or corrupted. Starting fresh.")

        # Transform the data: Replace 'username' with 'title' in the desired format and add 'source'
        transformed_data = []
        for tweet in self.data:
            first_15_words = " ".join(tweet['content'].split()[:15])  # Extract the first 15 words
            tweet['title'] = f"{tweet['username']}: {first_15_words}"  # Combine username and content
            tweet['source'] = 'twitter'  # Add source field
            del tweet['username']  # Remove the 'username' field
            transformed_data.append(tweet)

        # Prepend new data to the existing data, avoiding duplicates
        all_data = transformed_data + existing_data  # Prepend new data to the top of the list
        unique_data = {tweet['url']: tweet for tweet in all_data}.values()  # Use URL as a unique identifier

        # Save back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(list(unique_data), f, ensure_ascii=False, indent=4)
        print(f"Tweets updated in JSON format: {file_path}")


# Script Configuration
if __name__ == "__main__":
    USERNAME = "cybercrew23"
    PASSWORD = "Pass@0987"
    QUERIES = [
        "cybersecurity in India",
        "cyber attack in India",
        "cyber crime news in India"
    ]
    MAX_TWEETS = 100
    OUTPUT_FORMAT = "json"  

    scraper = TwitterScraper(username=USERNAME, password=PASSWORD, max_tweets=MAX_TWEETS)
    scraper.login()

    for query in QUERIES:
        print(f"Scraping tweets for query: {query}")
        scraper.search_tweets(query)

    scraper.save_to_file()
    scraper.close()
