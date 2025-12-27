import warnings
from transformers import pipeline
import logging

# Suppress warnings related to transformers library
warnings.filterwarnings("ignore", category=UserWarning, message=".*weights.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*device.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*label id.*")

# Disable transformers logging (set log level to ERROR to avoid info and warning logs)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Specify the path to the fine-tuned model
extract_dir = "D:/Study/SIH 2024/CyberCrew/models/fine_tuned_model"  # Path to your fine-tuned model

# Initialize the zero-shot classification pipeline for your fine-tuned models
classifier_roberta = pipeline("zero-shot-classification", model="roberta-large-mnli")
classifier_distilbert = pipeline("zero-shot-classification", model=extract_dir)  # Use the fine-tuned model from the specified directory

# Define severity labels with a broader range
severity_labels = [
    "Critical Severity", "High Severity", "Moderate Severity",
    "Low Severity"
]

def classify_cyber_incident_ensemble(news_article):
    """
    Classify the severity of a cyber incident-related news article using an ensemble of models.

    Args:
        news_article (str): The text of the news article.

    Returns:
        dict: A dictionary with the news article and the predicted severity.
    """
    try:
        # Perform zero-shot classification with both models
        result_roberta = classifier_roberta(news_article, candidate_labels=severity_labels)
        result_distilbert = classifier_distilbert(news_article, candidate_labels=severity_labels)

        # Get the predicted labels and confidence scores
        predicted_severity_roberta = result_roberta["labels"][0]
        predicted_severity_distilbert = result_distilbert["labels"][0]

        score_roberta = result_roberta["scores"][0]
        score_distilbert = result_distilbert["scores"][0]

        # Apply a confidence threshold of 0.8 for more confident decisions
        threshold = 0.8

        # Adjust severity based on low confidence (Don't downgrade "Critical" severity, downgrade "High" and "Moderate" if needed)
        def adjust_severity(label, score):
            if score < threshold:
                if label == "Critical Severity":
                    return label  # Do not downgrade "Critical Severity"
                elif label == "High Severity":
                    return "Moderate Severity"  # Downgrade "High Severity" to "Moderate Severity"
                elif label == "Moderate Severity":
                    return "Low Severity"  # Downgrade "Moderate Severity" to "Low Severity"
                else:
                    return label  # "Low Severity" remains as "Low Severity"
            return label

        # If both models agree, return the predicted severity
        if predicted_severity_roberta == predicted_severity_distilbert:
            final_prediction = adjust_severity(predicted_severity_roberta, score_roberta)
        else:
            # If confidence is high for both models, choose the more confident one
            if score_roberta >= threshold and score_roberta >= score_distilbert:
                final_prediction = adjust_severity(predicted_severity_roberta, score_roberta)
            elif score_distilbert >= threshold and score_distilbert > score_roberta:
                final_prediction = adjust_severity(predicted_severity_distilbert, score_distilbert)
            else:
                # If neither model has high confidence, pick the one with the highest confidence
                final_prediction = adjust_severity(predicted_severity_roberta if score_roberta > score_distilbert else predicted_severity_distilbert,
                                                   score_roberta if score_roberta > score_distilbert else score_distilbert)

        # Return the classification result
        return final_prediction

    except Exception as e:
        return {"Error": str(e)}

# Example: Classifying a variety of Indian cyber news articles
indian_cyber_news = [
    "Cyberfraud is surging TO DEATH in India, with Rs. 1,776 crore lost in scams this year alone."
]

# Classify each news article using the ensemble approach
for news_article in indian_cyber_news:
    result = classify_cyber_incident_ensemble(news_article)

    print(result)  # Only print the predicted severity
