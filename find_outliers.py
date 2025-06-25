import json
import glob
import os

# Get the most recent file
files = glob.glob("mlb_matchups_*.json")
latest_file = max(files, key=os.path.getctime)

with open(latest_file, 'r') as f:
    data = json.load(f)

print("LOW RELIABILITY MATCHUPS (< 20 PA):")
print("="*50)

low_reliability = []
for report in data['reports']:
    for matchup in report['key_matchups']:
        if matchup['reliability'] == 'LOW':
            low_reliability.append(matchup)

for m in sorted(low_reliability, key=lambda x: x['total_pa']):
    print(f"\n{m['batter']} vs {m['vs_pitcher']}")
    print(f"  BA: {m['weighted_avg_ba']:.3f} (only {m['total_pa']} PA!)")
    print(f"  Team: {m['team']}")

print("\n\nHIGHEST BA MATCHUPS WITH HIGH RELIABILITY:")
print("="*50)

high_reliability = []
for report in data['reports']:
    for matchup in report['key_matchups']:
        if matchup['reliability'] == 'HIGH':
            high_reliability.append(matchup)

top_5 = sorted(high_reliability, key=lambda x: x['weighted_avg_ba'], reverse=True)[:5]
for m in top_5:
    print(f"\n{m['batter']} vs {m['vs_pitcher']}")
    print(f"  BA: {m['weighted_avg_ba']:.3f} ({m['total_pa']} PA)")
    print(f"  Team: {m['team']}")
