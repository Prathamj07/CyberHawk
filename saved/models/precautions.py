import sys
import google.generativeai as genai
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Configure API key
API_KEY = os.getenv('GEMINI_API_KEY', '')  # Loaded from environment
genai.configure(api_key=API_KEY)

# Function to get easy-to-understand precautions from Gemini API
def get_precautions(news_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"Analyze the cyber attack in India: '{news_text}' and give two clear, simple precautions to avoid it. Only return the precautions."
    )
    return response.text.replace("*", "").strip() if response else "No precautions found."

if __name__ == "__main__":
    news_content = sys.argv[1]
    precautions = get_precautions(news_content)
    print(f"{precautions}")
