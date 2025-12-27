import requests
from bs4 import BeautifulSoup
import json

def scrape_cert_in_section():
    frame_url = "https://www.cert-in.org.in/s2cMainServlet?pageid=PUBWEL01"

    try:
        response = requests.get(frame_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    form = soup.find("form", {"name": "homePage"})
    if not form:
        print("Could not find the 'homePage' form.")
        return

    data = []
    count = 0
    for td in form.find_all("td", {"class": "Content"}):
        link_tag = td.find("a", href=True)
        if link_tag and count < 6:
            link_href = link_tag["href"]
            full_link = "https://www.cert-in.org.in/" + link_href
            data.append(full_link)
            count += 1

    if data:
        # Save the links to a JSON file
        output_file = "cert_news.json"
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"URLs saved to {output_file}")
    else:
        print("No data found in the specified section.")

scrape_cert_in_section()
