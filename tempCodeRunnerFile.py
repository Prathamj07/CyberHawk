import requests
from bs4 import BeautifulSoup

url = "https://www.cert-in.org.in/s2cMainServlet?pageid=PUBWEL02"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    base_url = "https://www.cert-in.org.in/"
    full_urls = [base_url + td.find('a')['href'] for td in soup.find_all('td', class_='BContent') if td.find('a', href=True)]

    for url in full_urls:
        print(url)
