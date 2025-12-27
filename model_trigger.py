import os
import concurrent.futures
import subprocess
import json


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
base_path = "D:/Study/SIH 2024/CyberCrew/trials/saved/models"


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data  
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []

def run_model(model_name, content):
    command = ['python', model_name, content]
    print(f"Executing command: {command}") 
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"Command Output (stdout): {result.stdout}")  # Debug: show standard output
    
    if result.returncode != 0:
        print(f"Error executing script {model_name}. Return code: {result.returncode}")
        return "Error in model execution"
    
    return format_output(result.stdout)

def format_output(stdout):
    return stdout.strip() 
def run_all_models_parallel(content, model_scripts):
    model_results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {model: executor.submit(run_model, model_name, content)
                   for model, model_name in model_scripts.items()}
        
        for model, future in futures.items():
            try:
                model_results[model] = future.result()
            except Exception as e:
                print(f"Error while running model {model}: {e}")
                model_results[model] = "Error in execution"
    
    return model_results

def update_json_data(news_data, model_scripts, json_file_path):
    for entry in news_data:
        summary = entry.get('summary', '')  # Extract the summary from the entry
        if not summary:
            print("No summary found in entry. Skipping.")
            continue
        
        print(f"Processing summary: {summary}")
        model_results = run_all_models_parallel(summary, model_scripts)
        
        for key, value in model_results.items():
            entry[key] = value if value else "No result"  # Default value if no output is generated

        print(f"Updated entry: {entry}")
    
    try:
        with open(json_file_path, 'w') as file:
            json.dump(news_data, file, indent=4)
        print(f"JSON file updated successfully: {json_file_path}")
    except IOError as e:
        print(f"Error writing to file {json_file_path}: {e}")

if __name__ == "__main__":
    json_file_path = "D:/Study/SIH 2024/CyberCrew/processed.json"  # Your input file with summaries
    model_scripts = {
            "domain": "DomainModel.py", 
            "sector": "SectorModel.py", 
            "state": "state_from_news.py",
            "fakeness": "news_detector.py",
            "severity": "severity.py",        "precautions": "precautions.py",  
        }

    news_data = load_json(json_file_path)
    
    if not news_data:
        print("No data loaded from JSON file. Exiting.")
    else:
        # Run all models and update the news data
        update_json_data(news_data, model_scripts, json_file_path)
