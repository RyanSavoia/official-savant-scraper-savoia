# Check if there are other ways to access Baseball Savant data
print('=== CHECKING ALL AVAILABLE MODULES ===')

try:
    import pybaseballstats
    print('Main pybaseballstats module attributes:')
    for attr in dir(pybaseballstats):
        if not attr.startswith('_'):
            print(f'  {attr}')
            
    # Check if there's a direct savant module
    try:
        from pybaseballstats import savant
        print('\nSavant module found!')
        print('Savant functions:')
        for attr in dir(savant):
            if not attr.startswith('_') and callable(getattr(savant, attr)):
                print(f'  {attr}')
    except:
        print('\nNo direct savant module')
        
    # Check statcast_leaderboards module
    try:
        from pybaseballstats import statcast_leaderboards
        print('\nStatcast leaderboards functions:')
        for attr in dir(statcast_leaderboards):
            if not attr.startswith('_') and callable(getattr(statcast_leaderboards, attr)):
                print(f'  {attr}')
    except:
        print('\nNo statcast_leaderboards module')
        
    # Check if there are other leaderboard functions
    print('\n=== TESTING OTHER STATCAST FUNCTIONS ===')
    from pybaseballstats.statcast_leaderboards import *
    
    # Try the other function we haven't tested
    try:
        other_data = statcast_pitch_arsenal_stats_leaderboard(2025, min_pa=50)
        print(f'\nstatcast_pitch_arsenal_stats_leaderboard: {len(other_data)} rows')
        print('Sample columns:')
        for col in other_data.columns[:15]:
            print(f'  {col}')
            
        print('\nColumns with opponent/BA data:')
        for col in other_data.columns:
            if any(word in col.lower() for word in ['ba', 'avg', 'opponent', 'against']):
                print(f'  *** {col} ***')
                
    except Exception as e:
        print(f'Error with pitch_arsenal_stats: {e}')

except Exception as e:
    print(f'Error: {e}')
