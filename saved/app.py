from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client['news_database']
collection = db['news']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_news', methods=['GET'])
def fetch_news():
    page = int(request.args.get('page', 1))
    limit = 5
    skip = (page - 1) * limit

    # Include 'time' field in the response
    news = list(collection.find({}, {'_id': 0, 'title': 1, 'content': 1, 'source': 1, 'time': 1}).skip(skip).limit(limit))
    return jsonify(news)

if __name__ == "__main__":
    app.run(debug=True)
