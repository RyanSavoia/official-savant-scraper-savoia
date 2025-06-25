import pybaseballstats.fangraphs as fg
import inspect

# Check function signatures and docs
print("=== Fangraphs Batting Functions ===")
print("\nfangraphs_batting_range signature:")
print(inspect.signature(fg.fangraphs_batting_range))
print("\nDocstring:")
print(fg.fangraphs_batting_range.__doc__)

print("\n\n=== Let's try to get some data ===")
try:
    # Try to get 2025 batting data
    batting_data = fg.fangraphs_batting_range(2025, 2025)
    print(f"Got {len(batting_data)} records")
    print(f"\nColumns available:")
    for col in batting_data.columns[:20]:  # First 20 columns
        print(f"  {col}")
    
    # Check for split-related columns
    print("\n\nSplit-related columns:")
    split_cols = [col for col in batting_data.columns if 'split' in col.lower() or 'vs' in col.lower() or 'hand' in col.lower()]
    print(split_cols)
    
except Exception as e:
    print(f"Error: {e}")

# Also check what stat types are available
print("\n\n=== Available Stat Types ===")
print("Batting stat types:", fg.FangraphsBattingStatType.__dict__)
