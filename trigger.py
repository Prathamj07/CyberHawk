import subprocess
import os

# Define absolute paths for all programs
base_path = r"D:\Study\SIH 2024\CyberCrew\trials\saved"
programs_to_run_simultaneously = [
    os.path.join(base_path, "x.py"),
    os.path.join(base_path, "RedditScraper.py"),
    os.path.join(base_path, "instascraper.py"),
    os.path.join(base_path, "google_news_url.py"),
]
google_newsdata_program = os.path.join(base_path, "google_newsdata.py")
combined_json_program = os.path.join(base_path, "combined_json.py")

def run_programs():
    processes = []

    # Start simultaneous programs
    for program in programs_to_run_simultaneously:
        if not os.path.exists(program):
            print(f"Error: File not found - {program}")
            continue
        print(f"Starting {program}...")
        process = subprocess.Popen(["python", program], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append(process)

    # Wait for all simultaneous programs to finish
    for process in processes:
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(f"{process.args[1]} completed successfully.")
        else:
            print(f"Error running {process.args[1]}: {stderr.decode('utf-8')}")

    # Run google_newsdata.py after others finish
    if os.path.exists(google_newsdata_program):
        print(f"Starting {google_newsdata_program}...")
        result = subprocess.run(["python", google_newsdata_program], capture_output=True)
        if result.returncode == 0:
            print(f"{google_newsdata_program} completed successfully.")
        else:
            print(f"Error running {google_newsdata_program}: {result.stderr.decode('utf-8')}")
    else:
        print(f"Error: File not found - {google_newsdata_program}")

    # Run combined_json.py after all other programs have finished
    if os.path.exists(combined_json_program):
        print(f"Starting {combined_json_program}...")
        result = subprocess.run(["python", combined_json_program], capture_output=True)
        if result.returncode == 0:
            print(f"{combined_json_program} completed successfully.")
        else:
            print(f"Error running {combined_json_program}: {result.stderr.decode('utf-8')}")
    else:
        print(f"Error: File not found - {combined_json_program}")

if __name__ == "__main__":
    run_programs()
