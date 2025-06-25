# Test file to check if our changes maintain the same JSON structure
import json

# Load current output
with open("mlb_matchups_20250623_194717.json", 'r') as f:
    current_format = json.load(f)

print("Current JSON structure:")
print("- Top level keys:", list(current_format.keys()))
print("- Report keys:", list(current_format['reports'][0].keys()))
print("- Matchup keys:", list(current_format['reports'][0]['key_matchups'][0].keys()))
print("\nCurrent matchup format has these fields:")
for key in current_format['reports'][0]['key_matchups'][0].keys():
    print(f"  - {key}")
