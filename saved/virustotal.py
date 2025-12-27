import requests
import json

API_KEY = '22e81047eb16d07bb32d3ac241db6e0f223e70b8fdffdb0334ce2b0edf4a1f7f'  # Replace with your VirusTotal API key
hash_value = input("Enter the hash to search for: ")

url = f'https://www.virustotal.com/api/v3/files/{hash_value}'
headers = {'x-apikey': API_KEY}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()

    # Extracting important information
    result = {
        'file_metadata': {
            'file_name': data['data']['attributes'].get('file_name', 'N/A'),
            'file_size': data['data']['attributes'].get('size', 'N/A'),
            'file_type': data['data']['attributes'].get('type', 'N/A'),
            'file_hashes': data['data']['attributes'].get('sha256', 'N/A'),
        },
        'last_analysis': {
            'date': data['data']['attributes']['last_analysis_date'],
            'results': data['data']['attributes']['last_analysis_results']
        },
        'threat_labels': data['data']['attributes'].get('tags', []),
        'reputation': data['data']['attributes'].get('reputation', 'N/A'),
    }

    # Printing important info in JSON format
    print(json.dumps(result, indent=4))

else:
    print("Error:", response.status_code, response.text)
