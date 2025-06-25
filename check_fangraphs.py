from pybaseballstats.fangraphs import fangraphs_pitching_range, FangraphsPitchingStatType
import polars as pl

print('=== FANGRAPHS PITCHING STAT TYPES ===')
# Check what stat types are available
try:
    stat_types = list(FangraphsPitchingStatType)
    print('Available stat types:')
    for stat_type in stat_types:
        print(f'  {stat_type}')
except Exception as e:
    print(f'Error getting stat types: {e}')

print('\n=== TESTING FANGRAPHS PITCHING DATA ===')
try:
    # Try to get 2025 pitching data (small sample)
    pitching_data = fangraphs_pitching_range(
        start_season=2025,
        end_season=2025,
        split_seasons=False,
        stat_type=FangraphsPitchingStatType.STANDARD,
        min_innings=10  # Small sample to test
    )
    
    print('Available columns:')
    for col in pitching_data.columns:
        print(f'  {col}')
    
    print('\nColumns with "ba", "avg", or "opponent":')
    for col in pitching_data.columns:
        if any(word in col.lower() for word in ['ba', 'avg', 'opponent', 'against']):
            print(f'  {col}')
    
    print(f'\nSample data (first pitcher):')
    if len(pitching_data) > 0:
        sample = pitching_data.head(1).to_dict()
        # Print just a few key fields
        for key, value in sample.items():
            if any(word in key.lower() for word in ['name', 'ba', 'avg']):
                print(f'  {key}: {value}')
                
except Exception as e:
    print(f'Error: {e}')
