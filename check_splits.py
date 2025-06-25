import pybaseballstats.fangraphs as fg
import inspect

# Check the function parameters more closely
print("=== Checking fangraphs_batting_range parameters ===")
print(inspect.signature(fg.fangraphs_batting_range))

# Check if there's a splits parameter
print("\n=== Testing with different parameters ===")
try:
    # Try standard batting data
    data = fg.fangraphs_batting_range(2025, 2025, stat_type=fg.FangraphsBattingStatType.STANDARD)
    print(f"Standard: {len(data)} records, {len(data.columns)} columns")
    
    # Look for any parameter that might give splits
    help(fg.fangraphs_batting_range)
    
except Exception as e:
    print(f"Error: {e}")

# Check if there are other modules for splits
print("\n=== Checking for other split-related functions ===")
import pybaseballstats
all_modules = dir(pybaseballstats)
for module in all_modules:
    if 'split' in module.lower() or 'vs' in module.lower():
        print(f"Found: {module}")
