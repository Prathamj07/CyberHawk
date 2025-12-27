from pymongo import MongoClient, ASCENDING, DESCENDING
import hashlib
import datetime
import json

MONGO_URI = "mongodb://localhost:27017/"  
DB_NAME = "news_database"
COLLECTION_NAME = "news"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

collection.create_index([("timestamp", DESCENDING)], unique=False)


def read_json_from_file():
    file_path = r"D:\Study\SIH 2024\CyberCrew\combined.json"  
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            return json_data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def get_latest_timestamp():
    latest_doc = collection.find_one(sort=[("timestamp", DESCENDING)])
    return latest_doc["timestamp"] if latest_doc else None


def add_new_articles(json_data):
    if not json_data:
        print("No data to process.")
        return

    latest_timestamp = get_latest_timestamp()
    print(f"Latest timestamp in database: {latest_timestamp}")

    articles = json_data if isinstance(json_data, list) else [json_data]

    new_articles = []
    for article in articles:
        article_timestamp = article.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())
        if latest_timestamp is None or article_timestamp > latest_timestamp:
            article["timestamp"] = article_timestamp
            new_articles.append(article)

    if not new_articles:
        print("No new articles to add.")
        return

    for article in new_articles:
        json_string = str(article)  
        hash_object = hashlib.sha256(json_string.encode())
        article["data_hash"] = hash_object.hexdigest()

        collection.insert_one(article)
        print(f"Added new article with hash: {article['data_hash']}")

    print(f"Added {len(new_articles)} new articles.")


def fetch_data_and_verify():
    data = list(collection.find().sort("timestamp", DESCENDING))
    for doc in data:
        computed_hash = hashlib.sha256(str(doc).encode()).hexdigest()
        stored_hash = doc.get('data_hash', '')

        print(f"Document: {doc}")
        print(f"Computed Hash: {computed_hash}")
        print(f"Stored Hash: {stored_hash}")

        if computed_hash == stored_hash:
            print("Data is intact.")
        else:
            print("Data has been tampered with!")
        print("---")
    return data


if __name__ == "__main__":
    json_data = read_json_from_file()
    if json_data:
        add_new_articles(json_data)

    fetch_data_and_verify()
