from pybaseballstats.fangraphs import fangraphs_pitching_range, FangraphsPitchingStatType
import inspect

print('=== CHECKING FUNCTION SIGNATURE ===')
sig = inspect.signature(fangraphs_pitching_range)
print(f'Function signature: {sig}')

print('\n=== TESTING WITH MINIMAL PARAMETERS ===')
try:
    # Try with just the required parameters
    pitching_data = fangraphs_pitching_range(
        start_year=2025,
        end_year=2025,
        stat_types=[FangraphsPitchingStatType.STANDARD]
    )
    
    print(f'Success! Got {len(pitching_data)} rows, {len(pitching_data.columns)} columns')
    print('\nColumns with "ba", "avg", "opponent", or "against":')
    ba_cols = []
    for col in pitching_data.columns:
        if any(word in col.lower() for word in ['ba', 'avg', 'opponent', 'against']):
            ba_cols.append(col)
            print(f'  *** {col} ***')
    
    if not ba_cols:
        print('  No opponent BA columns found in STANDARD')
        print('\nFirst 10 columns:')
        for col in pitching_data.columns[:10]:
            print(f'  {col}')
            
    # Try STATCAST_PITCH_TYPE since that's most likely to have pitch-level opponent stats
    print('\n--- TESTING STATCAST_PITCH_TYPE ---')
    statcast_data = fangraphs_pitching_range(
        start_year=2025,
        end_year=2025,
        stat_types=[FangraphsPitchingStatType.STATCAST_PITCH_TYPE]
    )
    
    print(f'STATCAST_PITCH_TYPE: {len(statcast_data)} rows, {len(statcast_data.columns)} columns')
    print('Columns with "ba", "avg", "opponent", or "against":')
    for col in statcast_data.columns:
        if any(word in col.lower() for word in ['ba', 'avg', 'opponent', 'against']):
            print(f'  *** {col} ***')
    
except Exception as e:
    print(f'Error: {e}')
