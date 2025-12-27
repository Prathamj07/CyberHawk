import requests
import json
import sys
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Function to search news article using Google Custom Search API
def search_google_news(news_text):
    api_key = os.getenv('GOOGLE_API_KEY', '')  # Loaded from environment
    cse_id = '216346618d7e04271'  # Replace with your Custom Search Engine ID

    # Refined query to focus on news and cyber-related topics
    query = f"{news_text} AND (cyber OR news OR security OR hacking OR breach)"
    
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}'

    # Expanded list of trusted Indian news websites (including cyber-related ones)
    trusted_news_domains = [
        'ndtv.com', 'timesofindia.indiatimes.com', 'thehindu.com', 'indiatoday.in', 'dailypioneer.com',
        'deccanherald.com', 'hindustantimes.com', 'news18.com', 'moneycontrol.com', 'scroll.in',
        'firstpost.com', 'mid-day.com', 'thewire.in', 'rediff.com', 'timesnownews.com', 'livemint.com',
        'thequint.com', 'business-standard.com', 'scoopwhoop.com', 'outlookindia.com', 'theprint.in',
        'indiatimes.com', 'indianexpress.com', 'telegraphindia.com', 'tribuneindia.com', 'gulfnews.com/india',
        'asianage.com', 'hindustantimes.com', 'livehindustan.com', 'thebetterindia.com', 'newsx.com',
        'tribuneindia.com', 'manoramaonline.com', 'karvymobile.com', 'techradar.com/in', 'cybersecurityindia.in',
        'hackerearth.com/blog', 'infosecawareness.in', 'thecyberpost.com', 'indianexpress.com/technology',
        'computing.co.in', 'itgovernance.co.in', 'indianweb2.com', 'thetechportal.com', 'techtree.com', 'digit.in',
        'dataquest.in', 'techcrunch.in', 'sify.com/itworld', 'edexlive.com/technology', 'techgig.com',
        'cybersecurity-insider.com', 'infosec.org', 'hackerone.com/blog', 'broadcom.com/blogs', 'securityintelligence.com',
        'darkreading.com', 'cybersecurityventures.com', 'cyberbrief.com', 'geekwire.com', 'gizmodo.com', 'engadget.com',
        'wired.com', 'zdnet.com', 'cloudsecurityalliance.org', 'krebsonsecurity.com', 'fortinet.com/blog',
        'nakedsecurity.sophos.com', 'redcanary.com/blog', 'businesstoday.in', 'startupindia.gov.in', 'cyberdomekerala.org',
        'techstartups.in', 'itwire.com', 'yourstory.com', 'thelogicalindian.com', 'cyberfraudindia.org', 'connectindia.org',
        'cybertechindia.com', 'economicstimes.com', 'expresscomputer.in', 'businessinsider.in', 'datastrategy.com',
        'riskthreats.com', 'finextra.com', 'securitymagazine.com', 'buzzfeednews.com', 'internetsecurity.com',
        'vulnerabilityexplorer.com', 'securelist.com', 'tripwire.com', 'attackiq.com', 'prosecuritynews.com',
        'secureworks.com', 'fireeye.com', 'microsoft.com', 'dell.com', 'cyberdefensemagazine.com', 'securityweek.com',
        'csoonline.com', 'guardian.com', 'bbc.com', 'theverge.com', 'techbarricade.com', 'sociable.co', 'securesense.com',
        'monitoringtools.com', 'cnbc.com', 'proactivecybersecurity.com'
    ]

    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()

        # Check if the search results contain any valid URLs
        if 'items' in results:
            
            # Set to store unique websites
            websites_found = set()
            trusted_websites_count = 0

            # Loop through all the items and track the domains
            for item in results['items']:
                link = item['link']
                source_domain = link.split('/')[2]  # Extract domain from the URL
                websites_found.add(source_domain)  # Add the domain to the set

                # Check if the domain is in the trusted list
                if any(trusted_domain in source_domain for trusted_domain in trusted_news_domains):
                    trusted_websites_count += 1

            # Evaluate the authenticity based on trusted websites
            if trusted_websites_count > 5:
                authenticity = "Definitely true"
            elif trusted_websites_count > 3:
                authenticity = "Likely true"
            elif trusted_websites_count > 1:
                authenticity = "Probably true"
            else:
                authenticity = "True"

            return authenticity  # Returning the authenticity result

        else:
            print("No results found.")
            return "Probably fake"  # If no results found, mark as probably fake

    else:
        return "Probably fake"  # Error in fetching, mark as probably fake


if __name__ == "__main__":
    if len(sys.argv) > 1:
        news_text = sys.argv[1]  # Get news content from command-line arguments
        authenticity = search_google_news(news_text)
        print(f"{authenticity}")
    