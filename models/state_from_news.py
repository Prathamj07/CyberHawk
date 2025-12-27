import google.generativeai as genai
import requests
import sys
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Configure your Gemini API key
gemini_api_key = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=gemini_api_key)

# Configure your Google Custom Search Engine API key and Custom Search Engine ID
cse_api_key = os.getenv('GOOGLE_API_KEY', '')
cse_id = '216346618d7e04271'  # Replace with your Custom Search Engine ID

def analyze_news_with_gemini(news_text):
    """
    Uses Gemini API to analyze the news article and extract the state, if mentioned.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Modify the prompt to focus on just extracting the state
        prompt = f"Identify the state in this news article: '{news_text}'. Only return the state name, no additional details."
        
        response = model.generate_content(prompt)
        return response.text.strip()  # Clean up any leading/trailing whitespace
    except Exception:
        return None

def search_related_news(news_text):
    """
    Uses Google Custom Search Engine API to find more context around the news topic to infer city/state.
    """
    try:
        url = f"https://www.googleapis.com/customsearch/v1?q={news_text}&key={cse_api_key}&cx={cse_id}"
        response = requests.get(url)
        results = response.json()

        # Check if any results are returned
        if 'items' in results:
            for item in results['items']:
                snippet = item['snippet']
                return snippet  # You can expand this logic as needed
        return None
    except Exception:
        return None

def detect_state_in_news(news_text):
    """
    Combine results from both Gemini and Google Search to detect the state.
    """
    # Step 1: Analyze with Gemini API to extract state
    gemini_result = analyze_news_with_gemini(news_text)
    if gemini_result:
        return gemini_result

    # Step 2: Use Google Custom Search to find additional context (if needed)
    google_result = search_related_news(news_text)
    if google_result:
        return "State inferred from Google search."

    return None

if __name__ == "__main__":
    news_article = sys.argv[1]  # Get news content from command-line arguments
    state_mentioned = detect_state_in_news(news_article)
    print(f"{state_mentioned}")
