from pybaseballstats.fangraphs import fangraphs_pitching_range, FangraphsPitchingStatType
import polars as pl

print('=== TESTING FANGRAPHS PITCHING DATA ===')

# Test the most promising stat types for opponent BA
promising_types = [
    FangraphsPitchingStatType.STANDARD,
    FangraphsPitchingStatType.ADVANCED,
    FangraphsPitchingStatType.STATCAST_PITCH_TYPE,
    FangraphsPitchingStatType.STATCAST_PITCH_TYPE_VALUE,
    FangraphsPitchingStatType.PITCH_INFO_PITCH_TYPE
]

for stat_type in promising_types:
    try:
        print(f'\n--- TESTING {stat_type} ---')
        pitching_data = fangraphs_pitching_range(
            start_year=2025,
            end_year=2025,
            split_seasons=False,
            stat_types=[stat_type],  # Note: plural and as list
            min_innings=10
        )
        
        print(f'Columns ({len(pitching_data.columns)} total):')
        # Look for opponent/BA related columns
        ba_cols = []
        for col in pitching_data.columns:
            if any(word in col.lower() for word in ['ba', 'avg', 'opponent', 'against']):
                ba_cols.append(col)
                print(f'  *** {col} ***')
        
        if not ba_cols:
            print('  No opponent BA columns found')
            
        # Show sample if we found relevant columns
        if ba_cols and len(pitching_data) > 0:
            print(f'Sample data:')
            sample = pitching_data.head(1).to_dict()
            for col in ba_cols[:5]:  # Show first 5 relevant columns
                if col in sample:
                    print(f'  {col}: {sample[col]}')
                    
    except Exception as e:
        print(f'Error with {stat_type}: {e}')
