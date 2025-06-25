import json

# Load the most recent output file
import glob
import os

# Get the most recent mlb_matchups file
files = glob.glob("mlb_matchups_*.json")
latest_file = max(files, key=os.path.getctime)

with open(latest_file, 'r') as f:
    data = json.load(f)

# Analyze reliability
reliability_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
pa_ranges = {'0-10': 0, '10-20': 0, '20-50': 0, '50+': 0}

for report in data['reports']:
    for matchup in report['key_matchups']:
        reliability_counts[matchup['reliability']] += 1
        
        pa = matchup['total_pa']
        if pa < 10:
            pa_ranges['0-10'] += 1
        elif pa < 20:
            pa_ranges['10-20'] += 1
        elif pa < 50:
            pa_ranges['20-50'] += 1
        else:
            pa_ranges['50+'] += 1

print("RELIABILITY BREAKDOWN:")
total = sum(reliability_counts.values())
for level, count in reliability_counts.items():
    print(f"  {level}: {count} matchups ({count/total*100:.1f}%)")

print("\nPLATE APPEARANCES DISTRIBUTION:")
for range_name, count in pa_ranges.items():
    print(f"  {range_name} PA: {count} matchups")
