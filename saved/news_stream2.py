import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import base64
import os

dashboard_path = r"D:/Study/SIH 2024/CyberCrew/trials/FinalDashboard.pbix"

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "hexabytes2024@gmail.com" 
sender_password = "voan kkoj dntd jfjk"  

def load_news_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def display_news_item(news_item):
    st.markdown(f"""
    <div style="border: 2px solid #0072B2; padding: 20px; margin-bottom: 20px; border-radius: 10px; background-color: #f4f7fc; width: 90%; margin-left: auto; margin-right: auto;">
        <h3 style="color: #0072B2; font-weight: bold; text-align: center;">{news_item['title']}</h3>
        <p style="color: #333; font-size: 14px; font-weight: bold; text-align: center;"> Time: {news_item['time']}</p>
        <p style="color: #555; font-weight: bold;">{news_item['summary']}</p>
        <p style="font-weight: bold;"><b>Domain:</b> {news_item['domain']}</p>
        <p style="font-weight: bold;"><b>Sector:</b> {news_item['sector']}</p>
        <p style="font-weight: bold;"><b>State:</b> {news_item['state']}</p>
        <p style="font-weight: bold;"><b>Severity:</b> {news_item['severity']}</p>
        <p style="font-weight: bold;"><b>Legal Status:</b> {news_item['legal']}</p>
        <p style="font-weight: bold;"><b>Precautions:</b><br>{news_item['precautions']}</p>
        <p><a href="{news_item['url']}" target="_blank" style="color: #0072B2;">Read more</a></p>
    </div>
    """, unsafe_allow_html=True)

def analyze_ioc(input_value):
    API_KEY = '22e81047eb16d07bb32d3ac241db6e0f223e70b8fdffdb0334ce2b0edf4a1f7f'  # Replace with your VirusTotal API key
    base_url = 'https://www.virustotal.com/api/v3/'

    # If the input is a URL, it must be base64 encoded to send to the API
    def encode_url(url):
        """Encodes a URL using base64 encoding."""
        return base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8').rstrip("=")

    # Determine the API endpoint based on the input type
    if input_value.startswith("http"):
        encoded_url = encode_url(input_value)
        url = f'{base_url}urls/{encoded_url}'
    else:
        url = f'{base_url}files/{input_value}'

    headers = {'x-apikey': API_KEY}

    # Fetch the data from the API
    with st.spinner("Fetching data..."):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Extract relevant information
            attributes = data['data']['attributes']
            result = {
                'file_metadata': attributes,
                'last_analysis': {
                    'date': attributes.get('last_analysis_date'),
                    'results': attributes.get('last_analysis_results')
                },
                'threat_labels': attributes.get('tags', []),
                'reputation': attributes.get('reputation', 0),
            }

            # Display Metadata
            file_metadata = result['file_metadata']
            st.markdown(f"**File Name**: {file_metadata.get('names', ['N/A'])[0]} <br>"
                        f"**File Size**: {file_metadata.get('size', 'N/A')} bytes <br>"
                        f"**File Type**: {file_metadata.get('type_description', 'N/A')} <br>"
                        f"**File Hash**: {file_metadata.get('sha256', 'N/A')}", unsafe_allow_html=True)

            # Visualization of Last Analysis Results
            engines = list(result["last_analysis"]["results"].keys())
            categories = [
                result["last_analysis"]["results"][engine]["category"]
                for engine in engines
            ]
            category_count = {category: categories.count(category) for category in set(categories)}

            st.markdown("### Detection by Category")
            if category_count:
                fig = px.bar(
                    x=list(category_count.keys()),
                    y=list(category_count.values()),
                    labels={"x": "Category", "y": "Count"},
                    title="Detection by Category"
                )
                st.plotly_chart(fig)
            else:
                st.info("No analysis data available.")

            # Visualization of Threat Labels
            threat_labels = result["threat_labels"]
            if threat_labels:
                st.markdown("### Threat Labels Distribution")
                fig2 = px.pie(
                    values=[1] * len(threat_labels),
                    names=threat_labels,
                    title="Threat Labels Distribution"
                )
                st.plotly_chart(fig2)
            else:
                st.info("No threat labels available.")

            # Reputation Gauge
            reputation = result["reputation"]
            st.markdown("### Reputation Score")
            if isinstance(reputation, int):
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=reputation,
                    title={"text": "Reputation Score"},
                    gauge={"axis": {"range": [-100, 100]}}
                ))
                st.plotly_chart(fig3)
            else:
                st.info("No reputation data available.")

        else:
            st.error(f"Failed to fetch data: {response.status_code} {response.text}")

# Email sending function
def send_email(subject, body, recipient_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        st.success("Incident reported successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def sidebar_navigation():
    st.sidebar.title("Navigation")
    options = ["Feed", "Visualization", "Interactive Dashboard", "Cyber Intelligence", "Report Incident", "Threat Actors"]
    choice = st.sidebar.radio("Select Option", options)
    return choice

# Incident Reporting Page
def report_incident():
    st.title("Report an Incident")
    with st.form(key='incident_form'):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        contact = st.text_input("Your Contact Number")
        crime_type = st.selectbox("Type of Cyber Crime", ["Malware", "Ransomware", "DDoS", "Data Breach", "Phishing", "Financial Theft"])
        description = st.text_area("Describe the Incident")
        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        subject = f"Cyber Crime Report: {crime_type}"
        body = f"""
        Incident Report:

        Name: {name}
        Email: {email}
        Contact: {contact}
        Type of Cyber Crime: {crime_type}
        Description: {description}
        """
        send_email(subject, body, "cyberdost@mha.gov.in")

def display_visualizations(json_file_path):
    st.title("Cyber Visualization Dashboard")
    try:
        data = pd.read_json(json_file_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Records by Sector")
        sector_count = data['sector'].value_counts().reset_index()
        sector_count.columns = ['Sector', 'Count']
        fig1 = px.bar(sector_count, x='Sector', y='Count', title="Records by Sector", color='Count')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("2. Records by Domain")
        domain_count = data['domain'].value_counts().reset_index()
        domain_count.columns = ['Domain', 'Count']
        fig2 = px.pie(domain_count, names='Domain', values='Count', title="Records by Domain")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("3. Severity Distribution")
        severity_count = data['severity'].value_counts().reset_index()
        severity_count.columns = ['Severity', 'Count']
        fig3 = px.bar(severity_count, x='Severity', y='Count', title="Severity Distribution", color='Count')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("4. Fakeness Analysis")
        fakeness_count = data['fakeness'].value_counts().reset_index()
        fakeness_count.columns = ['Fakeness', 'Count']
        fig4 = px.pie(fakeness_count, names='Fakeness', values='Count', title="Fakeness Analysis")
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("5. Records by Source and State")
    col5, col6 = st.columns(2)

    with col5:
        source_count = data['source'].value_counts().reset_index()
        source_count.columns = ['Source', 'Count']
        fig5 = px.bar(source_count, x='Source', y='Count', title="Records by Source", color='Count')
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        state_count = data['state'].value_counts().reset_index()
        state_count.columns = ['State', 'Count']
        fig6 = px.bar(state_count, x='State', y='Count', title="Records by State", color='Count')
        st.plotly_chart(fig6, use_container_width=True)

# Main Function
def app():
    st.title("CyberHawk")
    choice = sidebar_navigation()

    if choice == "Feed":
        st.subheader("Cyber News Feed")
        json_file_path = "E:/backup SIH/SIH/SIH/trials/saved/updated_processednew.json"
        try:
            news_data = load_news_data(json_file_path)
            for news_item in news_data:
                display_news_item(news_item)
                time.sleep(2)
        except Exception as e:
            st.error(f"Error: {e}")

    elif choice == "Visualization":
        json_file_path = r"E:/backup SIH/SIH/SIH/trials/saved/updated_processednew.json"
        display_visualizations(json_file_path)

    elif choice == "Interactive Dashboard":
        st.subheader("Interactive Cyber Mapping Dashboard")
        
        if st.button("Open Dashboard in Power BI"):
            try:
                os.startfile(dashboard_path)  
                st.success("Opening the Power BI dashboard...")
            except Exception as e:
                st.error(f"Error opening the dashboard: {e}")
    
    elif choice == "Cyber Intelligence":
        st.subheader("Cyber Threat Intelligence")
        input_value = st.text_input("Enter IOC (hash, URL, domain, IP)")
        if st.button("Analyze"):
            analyze_ioc(input_value)

    elif choice == "Report Incident":
        report_incident()

if __name__ == "__main__":
    app()