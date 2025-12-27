import json
import os


file_paths = {
    "news_data": "news_data.json",  
    "twitter": "D:/Study/SIH 2024/CyberCrew/tweets/X.json",  
    "reddit": "reddit.json",  
    "instagram": "instagram_posts.json",  
}


entry_counts = {
    "news_data": 4,
    "twitter": 3,
    "reddit": 2,
    "instagram": 2,
}

expected_fields = ["title", "time", "url", "content", "source"]

def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return []

def enforce_field_order(entry, fields):
    return {field: entry.get(field, None) for field in fields}

def combine_jsons(file_paths, entry_counts, expected_fields):
    combined_data = []
    sources_data = {}

    for source, file_path in file_paths.items():
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            sources_data[source] = []
        else:
            sources_data[source] = load_json(file_path)

    while any(sources_data.values()):  
        for source, count in entry_counts.items():
            if sources_data[source]:  
                to_add = sources_data[source][:count] 
                combined_data.extend(
                    [enforce_field_order(entry, expected_fields) for entry in to_add]
                )
                sources_data[source] = sources_data[source][count:]  

    return combined_data

def save_combined_json(combined_data, output_file="combined.json"):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(combined_data, file, indent=4, ensure_ascii=False)  
        print(f"Combined JSON saved to {output_file}")
    except Exception as e:
        print(f"Error saving combined JSON: {e}")

if __name__ == "__main__":
    combined_data = combine_jsons(file_paths, entry_counts, expected_fields)
    save_combined_json(combined_data)
