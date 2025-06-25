import glob
import os
import json

# Find all mlb_matchups JSON files
files = glob.glob("mlb_matchups_*.json")
if files:
    # Get the most recent one
    latest_file = max(files, key=os.path.getctime)
    print(f"Found file: {latest_file}")
    
    with open(latest_file, 'r') as f:
        current_format = json.load(f)
    
    print("\nCurrent JSON structure:")
    print("- Top level keys:", list(current_format.keys()))
    print("- Report keys:", list(current_format['reports'][0].keys()))
    print("- Matchup keys:", list(current_format['reports'][0]['key_matchups'][0].keys()))
    print("\nCurrent matchup format has these fields:")
    for key in current_format['reports'][0]['key_matchups'][0].keys():
        print(f"  - {key}")
else:
    print("No mlb_matchups_*.json files found in current directory")
    print("Files in directory:", os.listdir('.'))
