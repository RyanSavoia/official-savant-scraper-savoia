import pybaseballstats
from pybaseballstats.statcast_leaderboards import statcast_pitch_arsenal_stats_leaderboard
import polars as pl
import re

def parse_batter_name(lineup_string):
    """Extract batter name from various lineup formats"""
    # Remove numbers from start/end
    cleaned = re.sub(r'^\d+\s+', '', lineup_string)
    cleaned = re.sub(r'\s+\d+$', '', cleaned)
    
    # Remove handedness indicators (L), (R), (S)
    cleaned = re.sub(r'\([LRS]\)', '', cleaned)
    
    # Remove position abbreviations
    position_pattern = r'\b(C|1B|2B|3B|SS|LF|CF|RF|DH)\b'
    cleaned = re.sub(position_pattern, '', cleaned)
    
    # Clean up extra spaces
    name = ' '.join(cleaned.split()).strip()
    
    # Split name parts
    parts = name.split()
    
    if len(parts) >= 2:
        if parts[-1].lower() in ['jr', 'jr.', 'sr', 'sr.', 'ii', 'iii']:
            last_name = f"{parts[-2]} {parts[-1]}"
            first_name = ' '.join(parts[:-2])
        else:
            last_name = parts[-1]
            first_name = ' '.join(parts[:-1])
        
        return f"{last_name}, {first_name}"
    
    return name

# Load data
print("Loading 2025 batter data...")
all_batters = statcast_pitch_arsenal_stats_leaderboard(2025)
print(f"Total records in leaderboard: {len(all_batters)}")

# Get unique batters
unique_batters = all_batters.select('last_name, first_name').unique()
print(f"Unique batters in leaderboard: {len(unique_batters)}")

# Test with actual lineup
test_lineup = [
    "1   Sam Haggerty (S) CF",
    "2   Wyatt Langford (R) LF", 
    "3   Corey Seager (L) SS",
    "4   Marcus Semien (R) 2B",
    "5   Adolis García (R) RF",
    "6   Jonah Heim (S) C",
    "7   Josh Jung (R) 3B",
    "8   Kyle Higashioka (R) DH",
    "9   Ezequiel Duran (R) 1B"
]

print("\nChecking TEX lineup:")
found = 0
missing = 0

for batter_string in test_lineup:
    batter_name = parse_batter_name(batter_string)
    last_name = batter_name.split(',')[0].lower()
    
    matches = all_batters.filter(
        pl.col('last_name, first_name').str.to_lowercase().str.contains(last_name)
    )
    
    if len(matches) > 0:
        found += 1
        print(f"✓ {batter_name} - FOUND ({len(matches)} records)")
    else:
        missing += 1
        print(f"✗ {batter_name} - NOT IN LEADERBOARD")

print(f"\nSummary: {found}/9 batters found ({(found/9)*100:.1f}% coverage)")
print(f"Missing {missing} batters from leaderboard data")
