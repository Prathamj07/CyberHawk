import sys
from transformers import pipeline

# Initialize the zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the candidate labels (sectors) for classification
candidate_labels = [
    "Banking Sector", "Educational Sector", "Healthcare Sector",
    "Telecom Sector", "Retail Sector", "Government Sector",
    "Energy Sector", "Transportation Sector", "Technology Sector",
    "Media Sector"
]

# Function to classify the sector of a given news article
def classify_news_sector(news_article):
    # Perform zero-shot classification
    result = classifier(news_article, candidate_labels=candidate_labels)
    
    # Extract the predicted sector with the highest score
    return result['labels'][0]  # Return only the top predicted sector

if __name__ == "__main__":
    # Ensure input is provided through command line arguments
    if len(sys.argv) > 1:
        input_text = sys.argv[1]  # Capture the input text passed from the command line
        predicted_sector = classify_news_sector(input_text)
        print(predicted_sector)  # Output the predicted sector
    
