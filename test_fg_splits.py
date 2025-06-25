import pybaseballstats.fangraphs as fg

# Fix the date format - use strings instead of integers
batting_data = fg.fangraphs_batting_range("2024-01-01", "2024-12-31", min_pa=100)
print(f"Got {len(batting_data)} records")
print(f"\nFirst 30 columns:")
for i, col in enumerate(batting_data.columns[:30]):
    print(f"{i+1}. {col}")

# Check for any handedness/split columns
print("\n\nChecking for split-related columns:")
split_cols = [col for col in batting_data.columns if any(x in col.lower() for x in ['split', 'vs', 'hand', 'rhp', 'lhp'])]
if split_cols:
    print("Found:", split_cols)
else:
    print("No split columns found in the default data")

# Let's see if we can get data split by batting hand
print("\n\nTrying to get left-handed batters only:")
lhb_data = fg.fangraphs_batting_range("2024-01-01", "2024-12-31", min_pa=100, batting_hand='L')
print(f"Got {len(lhb_data)} left-handed batters")
