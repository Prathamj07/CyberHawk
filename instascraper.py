from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
import json
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Path to Tesseract executable (adjust if necessary)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Set up the headless option (Optional)
options = Options()
options.add_argument("--headless")  # Uncomment for headless mode if desired

# Path to ChromeDriver (handled by webdriver_manager)
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)

# Instagram login credentials
username = "sociopatrol"  # Replace with your username
password = os.getenv("INSTAGRAM_PASSWORD", "")  # Loaded from environment

# List of target users
target_users = ["cybersafe.news", "quitehacker", "cybercrimemagazine"]

# Open Instagram login page
browser.get("https://www.instagram.com/accounts/login/")
time.sleep(5)

# Enter username
browser.find_element(By.NAME, "username").send_keys(username)
browser.find_element(By.NAME, "password").send_keys(password)
browser.find_element(By.NAME, "password").send_keys(Keys.RETURN)

# Wait for login to complete
time.sleep(5)

# JSON file path
json_file_path = 'instagram_posts.json'

# Function to extract multiple posts information
def extract_post_info(target_user, num_posts=3):  # Changed to top 3 posts
    browser.get(f"https://www.instagram.com/{target_user}/")
    time.sleep(5)
    
    posts_info = []
    
    try:
        # Find the post links for the desired number of posts
        posts = browser.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        post_links = [post.get_attribute("href") for post in posts[:num_posts]]

        for index, post_url in enumerate(post_links):
            try:
                browser.get(post_url)
                time.sleep(5)
                
                # Take a screenshot of the visible post
                screenshot_path = f"{target_user}_post_{index + 1}_screenshot.png"
                browser.save_screenshot(screenshot_path)
                
                # Use OCR to extract text from the screenshot
                img = Image.open(screenshot_path)
                content_text = pytesseract.image_to_string(img)
                
                # Clean up content_text by removing unwanted newline characters
                cleaned_content = content_text.replace('\n', ' ').strip()

                # Extract the time of the post (actual upload time)
                try:
                    post_time = browser.find_element(By.XPATH, "//time").get_attribute("datetime")
                    # Convert the time to ISO format
                    formatted_time = datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S.%fZ").isoformat()
                except Exception as e:
                    print(f"Error extracting post time for {target_user}: {e}")
                    formatted_time = "N/A"

                # Organize data into a dictionary format, now including post URL
                post_info = {
                    "title": target_user,
                    "content": cleaned_content,
                    "time": formatted_time,
                    "url": post_url,
                    "source": "insta"
                }
                
                posts_info.append(post_info)

                # Delete the screenshot after extracting data
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)

            except Exception as e:
                print(f"Error extracting post {index + 1} for {target_user}: {e}")

    except Exception as e:
        print(f"Error locating posts for {target_user}: {e}")

    return posts_info

# Function to load existing data from the JSON file (if exists)
def load_existing_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("Error reading JSON file, starting with an empty list.")
                return []
    else:
        return []

# Function to check if a post is already in the JSON data
def is_duplicate(existing_data, new_post):
    for post in existing_data:
        if (
            post["title"] == new_post["title"] and
            post["content"] == new_post["content"] and
            post["time"] == new_post["time"]
        ):
            return True
    return False

# Function to save updated data to the JSON file
def save_data_to_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Load existing data
existing_data = load_existing_data(json_file_path)

# Collect data for each target user
for user in target_users:
    user_posts_info = extract_post_info(user, num_posts=5)  # Get top 3 posts
    if user_posts_info:
        for post in user_posts_info:
            if not is_duplicate(existing_data, post):
                existing_data.append(post)  # Append new data if not duplicate

# Save updated data back to the JSON file
save_data_to_json(json_file_path, existing_data)

# Close the browser
browser.quit()

print(f"Extracted {len(existing_data)} unique post URLs.")
