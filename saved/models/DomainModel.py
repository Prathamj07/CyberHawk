import sys
from transformers import pipeline

# Load the classifier pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Function to classify the given text
def classify_text(text):
    candidate_labels = ["Data Breach", "Phishing", "DDoS", "Malware", "Financial Theft", "Ransomware"]
    result = classifier(text, candidate_labels)
    return result['labels'][0]  # Return the top label

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
    else:
        input_text = input("Enter the text to classify: ")
    domain = classify_text(input_text)
    print(domain)
