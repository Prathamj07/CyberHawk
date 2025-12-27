import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import os

API_KEYS = [
    '22e81047eb16d07bb32d3ac241db6e0f223e70b8fdffdb0334ce2b0edf4a1f7f',
    '5276d9c692c5b43a80fd127ff16843cccbf22e4e72ea2add9bc3a61a71164199',
    '2abc3ae76e69aa840a2455307ee1ab35e8831943c2ec5c13c758f52bdbabfc4b'
]

def determine_input_type(input_value):
    if len(input_value) in (32, 40, 64):
        return "hash"
    elif "/" in input_value or "." in input_value:
        if "http" in input_value or "https" in input_value:
            return "url"
        elif any(char.isdigit() for char in input_value):
            return "ip"
        else:
            return "domain"
    else:
        return "unknown"

def query_virustotal(input_type, input_value):
    base_url = "https://www.virustotal.com/api/v3"
    endpoints = {
        "hash": f"/files/{input_value}",
        "domain": f"/domains/{input_value}",
        "url": f"/urls/{input_value}",
        "ip": f"/ip_addresses/{input_value}"
    }

    for api_key in API_KEYS:
        url = base_url + endpoints.get(input_type, "")
        headers = {'x-apikey': api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code != 403:
            print(f"Error with API key {api_key}: {response.status_code}")
    print("Failed to get a valid response.")
    return None

def save_to_json(data, filename='virtual.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_data = json.load(f)
        existing_data.update(data)  # Update the existing data with new data
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)
    else:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

def visualize_data(data):
    if 'data' not in data:
        print("No data to visualize")
        return

    attributes = data['data'].get('attributes', {})
    
    threat_labels = attributes.get('tags', [])
    categories = attributes.get('categories', {})
    last_analysis_stats = attributes.get('last_analysis_stats', {})

    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    ax[0].barh(threat_labels, np.ones(len(threat_labels)))
    ax[0].set_title("Threat Labels")
    ax[0].set_xlabel("Count")

    if last_analysis_stats:
        ax[1].bar(last_analysis_stats.keys(), last_analysis_stats.values())
        ax[1].set_title("Last Analysis Stats")
        ax[1].set_xlabel("Analysis Types")
        ax[1].set_ylabel("Count")

    plt.tight_layout()
    plt.show()

def analyze_ioc(input_value):
    input_type = determine_input_type(input_value)
    print(f"Detected Input Type: {input_type.capitalize()}")

    result = query_virustotal(input_type, input_value)
    
    if result:
        print("Analysis Result:", json.dumps(result, indent=4))

        save_to_json(result, filename='virtual.json')

        visualize_data(result)

if __name__ == "_main_":
    input_value = input("Enter IOC (Hash, Domain, URL, or IP): ")
    analyze_ioc(input_value)