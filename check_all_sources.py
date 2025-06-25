# Check what's available in each source
print('=== CHECKING ALL SOURCES FOR OPPONENT BA ===')

# 1. Baseball Savant
try:
    from pybaseballstats import savant
    print('\n1. BASEBALL SAVANT functions:')
    savant_funcs = [name for name in dir(savant) if not name.startswith('_')]
    for func in savant_funcs:
        if any(word in func.lower() for word in ['pitch', 'opponent', 'against', 'leaderboard']):
            print(f'   {func}')
except:
    print('   Savant not available')

# 2. Fangraphs  
try:
    from pybaseballstats import fangraphs
    print('\n2. FANGRAPHS functions:')
    fg_funcs = [name for name in dir(fangraphs) if not name.startswith('_')]
    for func in fg_funcs:
        if any(word in func.lower() for word in ['pitch', 'opponent', 'against', 'leaderboard']):
            print(f'   {func}')
except:
    print('   Fangraphs not available')

# 3. Baseball Reference
try:
    from pybaseballstats import baseball_reference
    print('\n3. BASEBALL REFERENCE functions:')
    br_funcs = [name for name in dir(baseball_reference) if not name.startswith('_')]
    for func in br_funcs:
        if any(word in func.lower() for word in ['pitch', 'opponent', 'against', 'leaderboard']):
            print(f'   {func}')
except:
    print('   Baseball Reference not available')

# 4. Check if there are other Savant functions
print('\n4. ALL SAVANT functions (looking for pitcher stats):')
try:
    import pybaseballstats
    all_funcs = [name for name in dir(pybaseballstats) if not name.startswith('_')]
    for func in all_funcs:
        if 'pitch' in func.lower() or 'opponent' in func.lower():
            print(f'   {func}')
except:
    print('   Error checking main module')
