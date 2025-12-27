import sys
import spacy

# Load spaCy's pre-trained model for English
nlp = spacy.load("en_core_web_sm")

# List of Cyber Laws and their relevant keywords
laws_dict = {
    'Section 66A IT Act': ['cyberstalking', 'offensive messages', 'social media abuse'],
    'Section 66B IT Act': ['stolen computer resource', 'stolen communication device'],
    'Section 66C IT Act': ['identity theft', 'impersonation'],
    'Section 66D IT Act': ['fraud', 'cheating by personation'],
    'Section 66E IT Act': ['privacy violation', 'obscene image', 'revenge porn'],
    'Section 66F IT Act': ['cyber terrorism', 'terrorism through cyberspace'],
    'Section 67 IT Act': ['obscene material', 'obscene content'],
    'Section 67A IT Act': ['sexually explicit material'],
    'Section 67B IT Act': ['child pornography', 'child abuse images'],
    'Section 68 IT Act': ['non-compliance with government directions'],
    'Section 69A IT Act': ['blocking access to information', 'national security'],
    'Section 69B IT Act': ['intercepting and decrypting information'],
    'Section 70 IT Act': ['critical infrastructure protection'],
    'Section 72 IT Act': ['breach of confidentiality', 'data breach'],
    'Section 72A IT Act': ['unauthorized disclosure of information'],
    'Section 73 IT Act': ['sending offensive messages'],
    'Section 74 IT Act': ['misuse of digital signature'],
    'Section 85 IT Act': ['offenses by company officers'],
    'Section 66 IT Act': ['hacking', 'unauthorized access to data'],
    'Section 65 IT Act': ['tampering with computer source documents'],
    'Section 83 IT Act': ['juvenile offenses'],
    
    # IPC related
    'Section 419 IPC': ['cheating by personation'],
    'Section 420 IPC': ['fraud', 'deception'],
    'Section 406 IPC': ['criminal breach of trust'],
    'Section 408 IPC': ['criminal breach of trust by clerk or servant'],
    'Section 499 IPC': ['defamation', 'online defamation'],
    'Section 503 IPC': ['criminal intimidation', 'threatening messages'],
    'Section 507 IPC': ['criminal intimidation through anonymous communication'],
    'Section 354C IPC': ['voyeurism', 'watching without consent'],
    'Section 354D IPC': ['stalking', 'cyberstalking'],
    'Section 375 IPC': ['rape', 'cyber rape'],
    'Section 376 IPC': ['rape', 'cyber sexual assault'],
    'Section 377 IPC': ['unnatural offenses', 'online sexual abuse'],
    'Section 468 IPC': ['forgery', 'document falsification'],
    'Section 471 IPC': ['using forged documents'],
    
    # Data Protection and Cybersecurity Laws
    'The Personal Data Protection Bill 2019': ['data privacy', 'data protection', 'unauthorized data processing'],
    'The Information Technology (Reasonable Security Practices and Procedures) Rules 2011': ['data security', 'data protection measures'],
    'The Digital Information Security in Healthcare Act': ['healthcare data security', 'patient data privacy'],
    'The Intermediary Guidelines and Digital Media Ethics Code 2021': ['online content regulation', 'illegal online content'],
    
    # Cybercrime Reporting and Investigation
    'The National Cybercrime Reporting Portal': ['cybercrime reporting', 'cyber incidents'],
    'The Cybercrime Investigation Cell': ['cybercrime investigation', 'cybercriminals'],
    
    # Other Cybercrime Offenses
    'Phishing': ['phishing', 'fraudulent emails', 'fake websites'],
    'Hacking': ['hacking', 'unauthorized access'],
    'Cyberbullying': ['cyberbullying', 'online harassment'],
    'Online Fraud': ['online fraud', 'financial fraud'],
    'Identity Theft': ['identity theft', 'fake identity'],
    'Data Theft': ['data theft', 'data breach'],
    'Ransomware': ['ransomware', 'cyber extortion'],
    'Social Media Abuse': ['social media abuse', 'defamation online'],
}

def clean_text(text):
    doc = nlp(text)
    return " ".join([token.text.lower() for token in doc if not token.is_stop and not token.is_punct])

def map_to_laws(news_text):
    detected_laws = []
    for law, keywords in laws_dict.items():
        if any(keyword in news_text.lower() for keyword in keywords):
            detected_laws.append(law)
    return detected_laws

def detect_violated_laws(news_text):
    cleaned_news = clean_text(news_text)
    return map_to_laws(cleaned_news)

if __name__ == "__main__":
    news_content = sys.argv[1]  # Accept news line as input
    laws_detected = detect_violated_laws(news_content)
    print(", ".join(laws_detected) if laws_detected else "No laws violated")
