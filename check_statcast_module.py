import pybaseballstats.statcast_leaderboards as sc

# List all functions in the statcast_leaderboards module
print("Functions in statcast_leaderboards module:")
funcs = [f for f in dir(sc) if not f.startswith('_')]
for func in funcs:
    print(f"  - {func}")
