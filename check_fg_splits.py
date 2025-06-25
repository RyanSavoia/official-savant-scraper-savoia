import pybaseballstats.fangraphs as fg

# First, let's check what's in the Bats column
batting_data = fg.fangraphs_batting_range("2024-01-01", "2024-12-31", min_pa=100)
print("Sample of Bats column:")
print(batting_data['Bats'].unique())

# Now let's check if there are functions specifically for splits
import pybaseballstats
fg_functions = [f for f in dir(pybaseballstats) if 'fg_' in f and 'split' in f.lower()]
print(f"\n\nFangraphs functions with 'split' in name: {fg_functions}")

# Let's also check for a splits-specific function
if hasattr(fg, 'fangraphs_batting_splits'):
    print("\nFound fangraphs_batting_splits function!")
else:
    print("\nNo fangraphs_batting_splits function found")

# Check all available fg functions
print("\n\nAll Fangraphs functions:")
all_fg = [f for f in dir(pybaseballstats) if f.startswith('fg_')]
for func in all_fg:
    print(f"  - {func}")
