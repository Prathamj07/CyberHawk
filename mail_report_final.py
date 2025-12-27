import smtplib
import json
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_json(file_path):
    """Load the JSON data from the specified file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def send_email(to_emails, subject, body):
    """Send an email with the specified details."""
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "hexabytes2024@gmail.com"  # Replace with your email
    sender_password = os.getenv("SENDER_PASSWORD", "")  # Loaded from environment

    # Setting up the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject

    # Attaching the email body
    msg.attach(MIMEText(body, 'plain'))

    # Sending the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            for email in to_emails:
                msg['To'] = email
                server.sendmail(sender_email, email, msg.as_string())
            print(f"Email sent to: {', '.join(to_emails)}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# Mapping states to email addresses
state_email_map = {
    "Andhra Pradesh": [
        "spcid.and@nic.in",
        "digpint-anp@gov.in",
        "cybercrimes1930@cid.appolice.gov.in",
        "cybercrimescid@ap.gov.in"
    ],
    "Arunachal Pradesh": [
        "spsit@arupol.nic.in",
        "takeringu@ips.gov.in"
    ],
    "Assam": [
        "digp-cid@assampolice.gov.in",
        "igp-cid@assampolice.gov.in"
    ],
    "Bihar": [
        "cybercell-bih@nic.in"
    ],
    "Chandigarh": [
        "dspccic.chd@nic.in",
        "dig-chd@nic.in"
    ],
    "Chhattisgarh": [
        "aigtech-phq.cg@gov.in",
        "cybercell-phq.cg@gov.in"
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        "phq-dd@nic.in",
        "digp-daman-dd@nic.in"
    ],
    "Delhi": [
        "ncrp.delhi@delhipolice.gov.in",
        "jointcp.ifsosplcell@delhipolice.gov.in"
    ],
    "Goa": [
        "spcyber@goapolice.gov.in",
        "digpgoa@goapolice.gov.in"
    ],
    "Gujarat": [
        "cc-cid@gujarat.gov.in"
    ],
    "Haryana": [
        "sp-cybercrimephq.pol@hry.gov.in"
    ],
    "Himachal Pradesh": [
        "dig-cybercr-hp@nic.in",
        "adgp-cid-hp@nic.in"
    ],
    "Jammu and Kashmir": [
        "igcrime-jk@nic.in",
        "adgpcidjk@jkpolice.gov.in"
    ],
    "Jharkhand": [
        "cyberps@jhpolice.gov.in"
    ],
    "Karnataka": [
        "cybercrimenodal@ksp.gov.in",
        "cybercrimego@ksp.gov.in"
    ],
    "Kerala": [
        "spcyberops.pol@kerala.gov.in",
        "adgpcyberops.pol@kerala.gov.in"
    ],
    "Ladakh": [
        "itsec-phq@police.ladakh.gov.in",
        "aig-civl@police.ladakh.gov.in"
    ],
    "Lakshadweep": [
        "cctns-lk@nic.in",
        "lak-sop@nic.in"
    ],
    "Madhya Pradesh": [
        "mpcyberpolice@mppolice.gov.in",
        "adg-cybercell@mppolice.gov.in"
    ],
    "Maharashtra": [
        "ig.cbr-mah@gov.in",
        "sp.cbr-mah@gov.in"
    ],
    "Manipur": [
        "sp-cybercrime.mn@manipur.gov.in"
    ],
    "Meghalaya": [
        "ccw-meg@gov.in"
    ],
    "Mizoram": [
        "cidcrime-mz@nic.in",
        "polmizo@rediffmail.com"
    ],
    "Nagaland": [
        "igpcrime-ngl@nic.in",
        "adgplo.ngl@gov.in"
    ],
    "Odisha": [
        "igp2cidcb@odishapolice.gov.in",
        "adgcidcb.orpol@nic.in"
    ],
    "Puducherry": [
        "ssptraffic@py.gov.in",
        "igp@py.gov.in"
    ],
    "Punjab": [
        "aigcc@punjabpolice.gov.in",
        "igp.cyber.c.police@punjabpolice.gov.in"
    ],
    "Rajasthan": [
        "sp.cybercrime@rajpolice.gov.in"
    ],
    "Sikkim": [
        "spcid@sikkimpolice.nic.in",
        "cybercrime666sk@gmail.com"
    ],
    "Tamil Nadu": [
        "sp2cwc@gmail.com",
        "sp1-ccdtnpolice@gov.in"
    ],
    "Telangana": [
        "spoperations-csbts@tspolice.gov.in",
        "director-tscsb@tspolice.gov.in"
    ],
    "Tripura": [
        "spcybercrime@tripurapolice.nic.in",
        "spscrb@tripurapolice.gov.in"
    ],
    "Uttarakhand": [
        "spstf-uk@nic.in"
    ],
    "Uttar Pradesh": [
        "adg-cybercrime.lu@up.gov.in"
    ],
    "West Bengal": [
        "ccwwb-ncrp@policewb.gov.in"
    ],
    "National Agencies": [
        "newsletter@nciipc.gov.in",
        "helpdesk1@nciipc.gov.in",
        "helpdesk2@nciipc.gov.in",
        "ir@nciipc.gov.in",
        "cyberdost@mha.gov.in",
        "aski4c-mha@nic.in",
        "indiaportal@gov.in"
    ]
}


# Main logic
def process_news_and_notify(json_file):
    data = load_json(json_file)
    national_agency_emails = state_email_map["National Agencies"]  # Always include these

    for news in data.get("news", []):
        state = news.get("state")
        severity = news.get("severity")

        if severity and severity.lower() in ["critical", "high", "medium"]:
            state_emails = state_email_map.get(state.title(), [])
            to_emails = state_emails + national_agency_emails  # Combine state and national agencies
            if to_emails:
                subject = f"CyberHawk Alert: {news.get('title')}"
                body = (
                    f"We CyberHawk want to report this news:\n\n"
                    f"Title: {news.get('title')}\n"
                    f"Severity: {severity}\n"
                    f"State: {state}\n"
                    f"Summary: {news.get('summary')}\n"
                    f"Date: {news.get('date')}\n"
                    f"Category: {news.get('category')}\n"
                    f"Author: {news.get('author')}\n"
                    f"Source: {news.get('source')}\n"
                )
                send_email(to_emails, subject, body)
            else:
                print(f"No email addresses configured for state: {state}")
        else:
            print(f"Skipping news with low severity: {news.get('title')}")
    data = load_json(json_file)
    national_agency_emails = state_email_map["National Agencies"]  # Always include these

    for news in data.get("news", []):
        state = news.get("state")
        severity = news.get("severity")

        if severity and severity.lower() in ["critical", "high", "medium"]:
            state_emails = state_email_map.get(state.title(), [])
            if state_emails:
                to_emails = state_emails + state_email_map["National Agencies"]
                subject = f"CyberHawk Alert: {news.get('title')}"
                body = (
                    f"We CyberHawk want to report this news:\n\n"
                    f"Title: {news.get('title')}\n"
                    f"Severity: {severity}\n"
                    f"State: {state}\n"
                    f"Summary: {news.get('summary')}\n"
                    f"Date: {news.get('date')}\n"
                    f"Category: {news.get('category')}\n"
                    f"Author: {news.get('author')}\n"
                    f"Source: {news.get('source')}\n"
                )
                send_email(to_emails, subject, body)
            else:
                print(f"No email addresses configured for state: {state}")
        else:
            print(f"Skipping news with low severity: {news.get('title')}")

# Usage example
process_news_and_notify("sample2.json")
