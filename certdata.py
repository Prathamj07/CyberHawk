import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

def save_urls_to_json():
    url = "https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVA01&VACODE=CIVA-2023-2153"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Use a session to keep the connection alive
    session = requests.Session()

    # Retry mechanism
    retries = 3
    for _ in range(retries):
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                base_url = "https://www.cert-in.org.in/"
                # Extract hrefs from the page
                full_urls = [base_url + td.find('a')['href'] for td in soup.find_all('td', class_='BContent') if td.find('a', href=True)]

                # Save URLs to JSON file
                with open("cert_news.json", "w") as json_file:
                    json.dump(full_urls, json_file, indent=4)

                print("URLs saved to cert_news.json")
                break  # If the request was successful, break out of the loop
            else:
                print(f"Failed to load page: {url}. Status code: {response.status_code}")
                break  # Stop retrying after a failed response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying...")
            sleep(5)  # Wait for 5 seconds before retrying
    else:
        print("Failed to fetch the page after multiple retries.")

def scrape_urls_from_json():
    input_file = "cert_news.json"
    output_file = "scraped_cert_details.json"

    try:
        with open(input_file, "r") as json_file:
            urls = json.load(json_file)
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        return

    scraped_data = []

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    for url in urls:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Content"))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            data = {}

            # Extract title
            title_tag_1 = soup.find('span', class_='ContentTD; subhead')
            title_tag_2 = soup.find('span', class_='contentTD')
            if title_tag_1 and title_tag_2:
                data['Title'] = f"{title_tag_1.get_text(strip=True)} - {title_tag_2.get_text(strip=True)}"
            else:
                data['Title'] = 'N/A'

            # Extract issue date
            issue_date_tag = soup.find('p', class_='contentTD; red')
            if issue_date_tag:
                issue_date_text = issue_date_tag.get_text(strip=True)
                data['Original Issue Date'] = issue_date_text.split(":")[1].strip() if ":" in issue_date_text else 'N/A'
            else:
                data['Original Issue Date'] = 'N/A'

            # Extract severity rating
            severity_tag = soup.find('span', class_='contentTD; severity')
            if severity_tag:
                severity_text = severity_tag.get_text(strip=True).replace("Severity Rating:", "").strip()
                data['Severity Rating'] = severity_text
            else:
                data['Severity Rating'] = 'N/A'

            # Extract other sections
            field_mappings = {
                "Software Affected": {"tag": "p", "contains": "Software Affected"},
                "Overview": {"tag": "p", "contains": "Overview"},
                "Target Audience": {"tag": "p", "contains": "Target Audience"},
                "Risk Assessment": {"tag": "p", "contains": "Risk Assessment"},
                "Impact Assessment": {"tag": "p", "contains": "Impact Assessment"},
                "Description": {"tag": "p", "contains": "Description"},
                "Solution": {"tag": "p", "contains": "Solution"}
            }

            for field, details in field_mappings.items():
                try:
                    if "contains" in details:
                        element = soup.find(details["tag"], string=lambda s: s and details["contains"] in s)
                        if element:
                            sibling = element.find_next_sibling() or element.parent.find_next_sibling()
                            data[field] = sibling.get_text(strip=True) if sibling else "N/A"
                        else:
                            data[field] = "N/A"
                except Exception as e:
                    data[field] = f"Error: {e}"

            scraped_data.append(data)

        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    driver.quit()

    # Save scraped data to JSON
    with open(output_file, "w") as json_file:
        json.dump(scraped_data, json_file, indent=4)

    print(f"Scraped data saved to {output_file}")

# Run the functions
save_urls_to_json()
scrape_urls_from_json()
